#!/usr/bin/env python3
"""
Multi-City Parallel Processing System
Enable parallel scraping of multiple cities with individual progress tracking and coordination.
"""

import threading
import queue
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum

# Import our systems
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode
from multi_city_system import MultiCitySystem
from error_handling_system import ErrorHandlingSystem


class ProcessingStatus(Enum):
    """Processing status for each city"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class CityProcessingResult:
    """Result of processing a single city"""
    city_code: str
    city_name: str
    status: ProcessingStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    pages_scraped: int = 0
    properties_found: int = 0
    properties_saved: int = 0
    error_message: Optional[str] = None
    session_id: Optional[str] = None
    output_file: Optional[str] = None


class MultiCityParallelProcessor:
    """
    Parallel processing system for multiple cities with coordination and monitoring
    """
    
    def __init__(self, max_workers: int = 3, progress_callback: Callable = None):
        """Initialize parallel processor"""
        
        self.max_workers = max_workers
        self.progress_callback = progress_callback
        
        # Systems
        self.city_system = MultiCitySystem()
        self.error_system = ErrorHandlingSystem()
        
        # Processing state
        self.processing_results = {}
        self.is_processing = False
        self.executor = None
        self.futures = {}
        
        # Progress tracking
        self.overall_progress = {
            'total_cities': 0,
            'completed_cities': 0,
            'failed_cities': 0,
            'start_time': None,
            'estimated_completion': None,
            'current_status': 'Ready'
        }
        
        # Thread-safe communication
        self.progress_queue = queue.Queue()
        self.stop_event = threading.Event()
        
        print(f"🏭 Multi-City Parallel Processor Initialized")
        print(f"   👥 Max workers: {max_workers}")
        print(f"   🏙️ Cities available: {len(self.city_system.cities)}")
    
    def start_parallel_processing(self, selected_cities: List[str], 
                                 scraping_config: Dict[str, Any]) -> bool:
        """Start parallel processing of multiple cities"""
        
        if self.is_processing:
            print("⚠️ Processing already in progress")
            return False
        
        try:
            # Validate cities
            validation = self.city_system.validate_city_selection(selected_cities)
            if validation['invalid_cities']:
                print(f"❌ Invalid cities: {validation['invalid_cities']}")
                return False
            
            # Initialize processing
            self.is_processing = True
            self.stop_event.clear()
            self.processing_results = {}
            
            # Setup progress tracking
            self.overall_progress.update({
                'total_cities': len(selected_cities),
                'completed_cities': 0,
                'failed_cities': 0,
                'start_time': datetime.now(),
                'current_status': 'Starting parallel processing...'
            })
            
            # Initialize results for each city
            for city_code in selected_cities:
                city = self.city_system.cities[city_code]
                self.processing_results[city_code] = CityProcessingResult(
                    city_code=city_code,
                    city_name=city.name,
                    status=ProcessingStatus.PENDING
                )
            
            # Start processing thread
            processing_thread = threading.Thread(
                target=self._run_parallel_processing,
                args=(selected_cities, scraping_config),
                daemon=True
            )
            processing_thread.start()
            
            print(f"🚀 Started parallel processing for {len(selected_cities)} cities")
            return True
            
        except Exception as e:
            self.error_system.handle_error(e, {
                'selected_cities': selected_cities,
                'scraping_config': scraping_config
            }, 'parallel_processing_start')
            self.is_processing = False
            return False
    
    def _run_parallel_processing(self, selected_cities: List[str], 
                                scraping_config: Dict[str, Any]):
        """Run parallel processing in separate thread"""
        
        try:
            # Create thread pool
            self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
            
            # Submit tasks for each city
            self.futures = {}
            for city_code in selected_cities:
                if self.stop_event.is_set():
                    break
                
                future = self.executor.submit(
                    self._process_single_city,
                    city_code,
                    scraping_config
                )
                self.futures[city_code] = future
                
                # Small delay between submissions to avoid overwhelming
                time.sleep(0.5)
            
            # Monitor completion
            self._monitor_processing_completion()
            
        except Exception as e:
            self.error_system.handle_error(e, {
                'selected_cities': selected_cities
            }, 'parallel_processing_execution')
        
        finally:
            self._cleanup_processing()
    
    def _process_single_city(self, city_code: str, scraping_config: Dict[str, Any]) -> CityProcessingResult:
        """Process a single city"""
        
        result = self.processing_results[city_code]
        
        try:
            # Update status
            result.status = ProcessingStatus.RUNNING
            result.start_time = datetime.now()
            self._notify_progress(city_code, 'started')
            
            # Get city info
            city = self.city_system.cities[city_code]
            
            # Create scraper instance for this city
            scraper = IntegratedMagicBricksScraper(
                headless=scraping_config.get('headless', True),
                incremental_enabled=scraping_config.get('incremental_enabled', True)
            )
            
            # Configure for this city
            city_config = scraping_config.copy()
            city_config['city'] = city.magicbricks_url_code
            
            print(f"🏙️ Starting scraping for {city.name} ({city_code})")
            
            # Start scraping
            scraping_result = scraper.scrape_properties_with_incremental(
                city=city.magicbricks_url_code,
                mode=scraping_config.get('mode', ScrapingMode.INCREMENTAL),
                max_pages=scraping_config.get('max_pages', 100)
            )
            
            if scraping_result['success']:
                # Update result with success data
                result.status = ProcessingStatus.COMPLETED
                result.pages_scraped = scraping_result.get('pages_scraped', 0)
                result.properties_found = scraping_result.get('session_stats', {}).get('properties_found', 0)
                result.properties_saved = scraping_result.get('properties_scraped', 0)
                result.session_id = scraping_result.get('session_stats', {}).get('session_id')
                
                # Save results to city-specific file
                if scraper.properties:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    mode = scraping_config.get('mode', ScrapingMode.INCREMENTAL).value
                    filename = f"magicbricks_{city.magicbricks_url_code}_{mode}_{timestamp}.csv"
                    output_path = Path(scraping_config.get('output_directory', '.')) / filename
                    
                    df = scraper.save_to_csv(str(output_path))
                    if df is not None:
                        result.output_file = str(output_path)
                
                # Update city statistics
                self.city_system.update_city_statistics(
                    city_code,
                    result.properties_saved,
                    int((result.end_time - result.start_time).total_seconds() / 60) if result.end_time else 0
                )
                
                print(f"✅ Completed scraping for {city.name}: {result.properties_saved} properties")
                
            else:
                # Handle scraping failure
                result.status = ProcessingStatus.FAILED
                result.error_message = scraping_result.get('error', 'Unknown error')
                
                print(f"❌ Failed scraping for {city.name}: {result.error_message}")
            
            # Clean up scraper
            scraper.close()
            
        except Exception as e:
            # Handle processing error
            result.status = ProcessingStatus.FAILED
            result.error_message = str(e)
            
            self.error_system.handle_error(e, {
                'city_code': city_code,
                'city_name': city.name if 'city' in locals() else 'Unknown'
            }, 'city_processing')
            
            print(f"❌ Error processing {city_code}: {str(e)}")
        
        finally:
            result.end_time = datetime.now()
            self._notify_progress(city_code, 'completed')
        
        return result
    
    def _monitor_processing_completion(self):
        """Monitor processing completion and update overall progress"""
        
        try:
            completed_count = 0
            
            # Wait for all futures to complete
            for city_code, future in self.futures.items():
                if self.stop_event.is_set():
                    break
                
                try:
                    # Wait for completion with timeout
                    result = future.result(timeout=3600)  # 1 hour timeout per city
                    completed_count += 1
                    
                    # Update overall progress
                    if result.status == ProcessingStatus.COMPLETED:
                        self.overall_progress['completed_cities'] += 1
                    else:
                        self.overall_progress['failed_cities'] += 1
                    
                    # Calculate progress percentage
                    progress_percentage = (completed_count / self.overall_progress['total_cities']) * 100
                    
                    # Estimate completion time
                    if completed_count > 0:
                        elapsed_time = datetime.now() - self.overall_progress['start_time']
                        avg_time_per_city = elapsed_time.total_seconds() / completed_count
                        remaining_cities = self.overall_progress['total_cities'] - completed_count
                        estimated_remaining = remaining_cities * avg_time_per_city
                        
                        self.overall_progress['estimated_completion'] = datetime.now().timestamp() + estimated_remaining
                    
                    # Update status
                    self.overall_progress['current_status'] = f"Processing... {completed_count}/{self.overall_progress['total_cities']} cities completed"
                    
                    # Notify progress callback
                    if self.progress_callback:
                        self.progress_callback({
                            'type': 'overall_progress',
                            'progress_percentage': progress_percentage,
                            'completed_cities': completed_count,
                            'total_cities': self.overall_progress['total_cities'],
                            'current_status': self.overall_progress['current_status']
                        })
                    
                except Exception as e:
                    print(f"⚠️ Error waiting for {city_code}: {str(e)}")
                    self.overall_progress['failed_cities'] += 1
                    completed_count += 1
            
            # Final status update
            self.overall_progress['current_status'] = f"Completed: {self.overall_progress['completed_cities']} successful, {self.overall_progress['failed_cities']} failed"
            
            if self.progress_callback:
                self.progress_callback({
                    'type': 'processing_complete',
                    'completed_cities': self.overall_progress['completed_cities'],
                    'failed_cities': self.overall_progress['failed_cities'],
                    'total_cities': self.overall_progress['total_cities']
                })
            
        except Exception as e:
            self.error_system.handle_error(e, {}, 'processing_monitoring')
    
    def _notify_progress(self, city_code: str, event_type: str):
        """Notify progress for individual city"""
        
        if self.progress_callback:
            result = self.processing_results.get(city_code)
            if result:
                self.progress_callback({
                    'type': 'city_progress',
                    'city_code': city_code,
                    'city_name': result.city_name,
                    'event_type': event_type,
                    'status': result.status.value,
                    'pages_scraped': result.pages_scraped,
                    'properties_saved': result.properties_saved,
                    'error_message': result.error_message
                })
    
    def _cleanup_processing(self):
        """Clean up processing resources"""
        
        try:
            if self.executor:
                self.executor.shutdown(wait=True)
                self.executor = None
            
            self.futures.clear()
            self.is_processing = False
            
            print("🧹 Parallel processing cleanup completed")
            
        except Exception as e:
            print(f"⚠️ Error during cleanup: {str(e)}")
    
    def stop_processing(self):
        """Stop parallel processing"""
        
        if not self.is_processing:
            return
        
        print("🛑 Stopping parallel processing...")
        
        # Set stop event
        self.stop_event.set()
        
        # Cancel pending futures
        for city_code, future in self.futures.items():
            if not future.done():
                future.cancel()
                
                # Update result status
                if city_code in self.processing_results:
                    self.processing_results[city_code].status = ProcessingStatus.CANCELLED
        
        # Update overall status
        self.overall_progress['current_status'] = 'Processing stopped by user'
        
        if self.progress_callback:
            self.progress_callback({
                'type': 'processing_stopped',
                'message': 'Processing stopped by user request'
            })
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get comprehensive processing summary"""
        
        summary = {
            'overall_progress': self.overall_progress.copy(),
            'city_results': {},
            'statistics': {
                'total_pages_scraped': 0,
                'total_properties_found': 0,
                'total_properties_saved': 0,
                'successful_cities': 0,
                'failed_cities': 0,
                'average_properties_per_city': 0,
                'total_processing_time': 0
            }
        }
        
        # Process individual city results
        for city_code, result in self.processing_results.items():
            summary['city_results'][city_code] = {
                'city_name': result.city_name,
                'status': result.status.value,
                'pages_scraped': result.pages_scraped,
                'properties_found': result.properties_found,
                'properties_saved': result.properties_saved,
                'processing_time': (result.end_time - result.start_time).total_seconds() if result.start_time and result.end_time else 0,
                'error_message': result.error_message,
                'output_file': result.output_file
            }
            
            # Update statistics
            summary['statistics']['total_pages_scraped'] += result.pages_scraped
            summary['statistics']['total_properties_found'] += result.properties_found
            summary['statistics']['total_properties_saved'] += result.properties_saved
            
            if result.status == ProcessingStatus.COMPLETED:
                summary['statistics']['successful_cities'] += 1
            elif result.status == ProcessingStatus.FAILED:
                summary['statistics']['failed_cities'] += 1
            
            if result.start_time and result.end_time:
                summary['statistics']['total_processing_time'] += (result.end_time - result.start_time).total_seconds()
        
        # Calculate averages
        total_cities = len(self.processing_results)
        if total_cities > 0:
            summary['statistics']['average_properties_per_city'] = summary['statistics']['total_properties_saved'] / total_cities
        
        return summary
    
    def export_processing_report(self, filename: str = None) -> str:
        """Export detailed processing report"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"multi_city_processing_report_{timestamp}.json"
        
        try:
            summary = self.get_processing_summary()
            
            # Add metadata
            report = {
                'report_metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'processor_version': '1.0',
                    'max_workers': self.max_workers
                },
                'processing_summary': summary
            }
            
            # Convert datetime objects to strings for JSON serialization
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return obj
            
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=convert_datetime)
            
            print(f"📊 Processing report exported to {filename}")
            return filename
            
        except Exception as e:
            self.error_system.handle_error(e, {'filename': filename}, 'report_export')
            return None


def main():
    """Test the multi-city parallel processor"""
    
    try:
        print("🧪 TESTING MULTI-CITY PARALLEL PROCESSOR")
        print("="*50)
        
        # Progress callback for testing
        def progress_callback(progress_data):
            print(f"📊 Progress: {progress_data}")
        
        # Initialize processor
        processor = MultiCityParallelProcessor(max_workers=2, progress_callback=progress_callback)
        
        # Test configuration
        test_cities = ['DEL', 'MUM', 'BLR']  # Delhi, Mumbai, Bangalore
        test_config = {
            'mode': ScrapingMode.INCREMENTAL,
            'max_pages': 2,  # Small test
            'headless': True,
            'incremental_enabled': True,
            'output_directory': '.'
        }
        
        print(f"\n🚀 Starting parallel processing test...")
        print(f"Cities: {test_cities}")
        print(f"Config: {test_config}")
        
        # Start processing (this would run in background)
        success = processor.start_parallel_processing(test_cities, test_config)
        
        if success:
            print("✅ Parallel processing started successfully!")
            
            # In a real scenario, this would run in background
            # For testing, we'll just show the setup worked
            time.sleep(2)
            
            # Get summary
            summary = processor.get_processing_summary()
            print(f"\n📊 Processing summary:")
            print(f"Total cities: {summary['overall_progress']['total_cities']}")
            print(f"Status: {summary['overall_progress']['current_status']}")
            
            # Stop processing for test
            processor.stop_processing()
            
        else:
            print("❌ Failed to start parallel processing")
        
        print("\n✅ Multi-city parallel processor test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Multi-city parallel processor test failed: {str(e)}")
        return False


if __name__ == "__main__":
    main()
