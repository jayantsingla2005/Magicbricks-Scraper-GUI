#!/usr/bin/env python3
"""
Production Parallel Property Processor
Production-ready implementation based on comprehensive 50-property research validation.
Optimized for 7 perfect-availability sections with robust error handling.
"""

import time
import json
import threading
import queue
import random
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
from pathlib import Path

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# BeautifulSoup for parsing
from bs4 import BeautifulSoup

# Add src directory to path
import sys
sys.path.append(str(Path(__file__).parent.parent))

try:
    from core.url_discovery_manager import URLDiscoveryManager
    from core.detailed_property_extractor import DetailedPropertyExtractor, DetailedPropertyModel
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class ProductionParallelProcessor:
    """
    Production-ready parallel property processing system
    Based on comprehensive 50-property research validation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize production parallel processor"""
        
        self.config = config
        
        # Research-validated production settings
        self.processing_config = {
            'max_workers': 4,  # Optimal based on research
            'request_delay_range': (4.5, 5.5),  # Research-validated timing
            'max_retries': 3,
            'timeout_per_property': 45,
            'batch_size': 25,  # Larger batches for production
            'error_threshold': 0.10,  # 10% error threshold
            'session_rotation_interval': 100,  # Rotate every 100 properties
            'memory_cleanup_interval': 50,  # Clean memory every 50 properties
            'progress_report_interval': 10  # Report progress every 10 properties
        }
        
        # Research-validated target sections (7 perfect + 1 good availability)
        self.priority_sections = [
            'amenities', 'floor_plan', 'neighborhood', 'pricing_details',
            'project_info', 'location_details', 'images'  # 100% availability
        ]
        
        self.secondary_sections = [
            'specifications'  # 76% availability
        ]
        
        self.all_target_sections = self.priority_sections + self.secondary_sections
        
        # Production statistics tracking
        self.stats = {
            'session_id': None,
            'start_time': None,
            'end_time': None,
            'total_properties_processed': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'total_data_sections_extracted': 0,
            'priority_sections_extracted': 0,
            'secondary_sections_extracted': 0,
            'average_processing_time': 0,
            'error_rate': 0,
            'throughput_per_minute': 0,
            'section_success_rates': {section: 0 for section in self.all_target_sections},
            'property_type_stats': {},
            'batch_performance': []
        }
        
        # Thread management
        self.url_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.error_queue = queue.Queue()
        self.processing_lock = threading.Lock()
        
        # Initialize components
        self.url_manager = URLDiscoveryManager()
        
        print("🚀 Production Parallel Processor initialized")
        print(f"⚙️ Configuration: {self.processing_config['max_workers']} workers, "
              f"{self.processing_config['request_delay_range']} delay range")
        print(f"🎯 Priority sections (100% availability): {', '.join(self.priority_sections)}")
        print(f"🎯 Secondary sections (76% availability): {', '.join(self.secondary_sections)}")
    
    def process_properties_production(self, session_id: str, max_properties: int = 200) -> Dict[str, Any]:
        """
        Process properties in production mode with comprehensive validation
        """
        
        print("\n🚀 Starting Production Parallel Property Processing")
        print("="*70)
        
        self.stats['session_id'] = session_id
        self.stats['start_time'] = datetime.now()
        
        try:
            # Step 1: Load property URLs
            print("📡 Step 1: Loading Property URLs from Discovery Queue...")
            property_urls = self._load_production_property_urls(session_id, max_properties)
            
            if not property_urls:
                print("⚠️ No property URLs available for processing")
                return self._finalize_production_stats()
            
            print(f"✅ Loaded {len(property_urls)} property URLs for production processing")
            
            # Step 2: Process in optimized parallel batches
            print(f"\n🔄 Step 2: Processing {len(property_urls)} Properties in Parallel...")
            self._process_urls_production_parallel(property_urls)
            
            # Step 3: Collect and analyze results
            print("\n📊 Step 3: Collecting and Analyzing Production Results...")
            results = self._collect_and_analyze_production_results()
            
            # Step 4: Save production results
            print("\n💾 Step 4: Saving Production Results...")
            self._save_production_results(results, session_id)
            
            # Step 5: Generate production report
            print("\n📋 Step 5: Generating Production Report...")
            production_report = self._generate_production_report(results)
            
            # Finalize statistics
            final_stats = self._finalize_production_stats()
            
            print("\n✅ Production Parallel Property Processing Complete!")
            self._log_production_statistics()
            
            return {
                'status': 'success',
                'statistics': final_stats,
                'results': results,
                'production_report': production_report,
                'session_id': session_id
            }
            
        except Exception as e:
            print(f"❌ Production processing failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'statistics': self._finalize_production_stats(),
                'session_id': session_id
            }
    
    def _load_production_property_urls(self, session_id: str, max_properties: int) -> List[Dict[str, Any]]:
        """Load property URLs for production processing"""
        
        # Get pending URLs from discovery manager
        pending_urls = self.url_manager.get_pending_urls(limit=max_properties * 2)
        
        if not pending_urls:
            # Discover new URLs if none pending
            print("🔍 No pending URLs found, discovering new properties...")
            discovery_result = self.url_manager.discover_urls_from_listings(
                start_page=1,
                max_pages=10,  # More pages for production
                session_id=session_id
            )
            
            # Try again after discovery
            pending_urls = self.url_manager.get_pending_urls(limit=max_properties)
        
        # Format URLs for production processing
        property_urls = []
        for url_data in pending_urls[:max_properties]:
            property_urls.append({
                'url': url_data['url'],
                'url_id': url_data.get('id'),
                'priority': url_data.get('priority', 2),
                'metadata': url_data.get('metadata', {}),
                'discovery_session': url_data.get('session_id', session_id),
                'expected_property_type': self._predict_property_type(url_data)
            })
        
        return property_urls
    
    def _predict_property_type(self, url_data: Dict[str, Any]) -> str:
        """Predict property type from URL metadata for optimization"""
        
        metadata = url_data.get('metadata', {})
        title = metadata.get('listing_title', '').lower()
        
        if 'house' in title or 'independent' in title:
            return 'house'
        elif 'plot' in title or 'land' in title:
            return 'plot'
        elif 'villa' in title:
            return 'villa'
        elif 'floor' in title or 'builder floor' in title:
            return 'floor'
        else:
            return 'apartment'  # default
    
    def _process_urls_production_parallel(self, property_urls: List[Dict[str, Any]]):
        """Process URLs using optimized production parallel workers"""
        
        # Add URLs to processing queue
        for url_data in property_urls:
            self.url_queue.put(url_data)
        
        # Process in optimized batches
        total_urls = len(property_urls)
        batch_size = self.processing_config['batch_size']
        
        for batch_start in range(0, total_urls, batch_size):
            batch_end = min(batch_start + batch_size, total_urls)
            batch_number = batch_start // batch_size + 1
            
            print(f"\n🔄 Processing Batch {batch_number}: URLs {batch_start + 1}-{batch_end} of {total_urls}")
            
            batch_start_time = time.time()
            
            # Process batch with optimized thread pool
            with ThreadPoolExecutor(max_workers=self.processing_config['max_workers']) as executor:
                # Submit worker tasks
                futures = []
                for i in range(self.processing_config['max_workers']):
                    future = executor.submit(self._production_worker_thread, f"worker-{i+1}", batch_number)
                    futures.append(future)
                
                # Wait for batch completion
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"❌ Worker thread error: {str(e)}")
            
            batch_duration = time.time() - batch_start_time
            batch_properties = min(batch_size, total_urls - batch_start)
            batch_throughput = (batch_properties / batch_duration) * 60 if batch_duration > 0 else 0
            
            # Record batch performance
            self.stats['batch_performance'].append({
                'batch_number': batch_number,
                'properties_processed': batch_properties,
                'duration_seconds': batch_duration,
                'throughput_per_minute': batch_throughput
            })
            
            print(f"✅ Batch {batch_number} complete: {batch_properties} properties in {batch_duration:.1f}s "
                  f"({batch_throughput:.1f} properties/minute)")
            
            # Check error rate and stop if too high
            current_error_rate = self._calculate_current_error_rate()
            if current_error_rate > self.processing_config['error_threshold']:
                print(f"⚠️ High error rate detected ({current_error_rate:.1%}), stopping processing")
                break
            
            # Memory cleanup between batches
            if batch_number % (self.processing_config['memory_cleanup_interval'] // batch_size) == 0:
                print("🧹 Performing memory cleanup...")
                import gc
                gc.collect()
            
            # Extended break between batches for production stability
            if batch_end < total_urls:
                print("⏱️ Taking production stability break...")
                time.sleep(5)
    
    def _production_worker_thread(self, worker_id: str, batch_number: int):
        """Optimized production worker thread"""
        
        print(f"🔧 Production Worker {worker_id} started for batch {batch_number}")
        
        # Setup optimized browser for production
        driver = self._setup_production_browser()
        extractor = DetailedPropertyExtractor(self.config)
        
        processed_count = 0
        
        try:
            while True:
                try:
                    # Get next URL from queue (with timeout)
                    url_data = self.url_queue.get(timeout=10)
                    
                    if url_data is None:  # Poison pill to stop worker
                        break
                    
                    # Process single property with production optimization
                    result = self._process_single_property_production(driver, extractor, url_data, worker_id)
                    
                    # Store result
                    self.results_queue.put(result)
                    
                    # Update statistics with thread safety
                    with self.processing_lock:
                        self.stats['total_properties_processed'] += 1
                        if result['status'] == 'success':
                            self.stats['successful_extractions'] += 1
                            self.stats['total_data_sections_extracted'] += result.get('sections_extracted', 0)
                            self.stats['priority_sections_extracted'] += result.get('priority_sections_extracted', 0)
                            self.stats['secondary_sections_extracted'] += result.get('secondary_sections_extracted', 0)
                        else:
                            self.stats['failed_extractions'] += 1
                        
                        # Progress reporting
                        if self.stats['total_properties_processed'] % self.processing_config['progress_report_interval'] == 0:
                            success_rate = (self.stats['successful_extractions'] / self.stats['total_properties_processed']) * 100
                            print(f"📊 Progress: {self.stats['total_properties_processed']} processed, "
                                  f"{success_rate:.1f}% success rate")
                    
                    processed_count += 1
                    
                    # Mark URL as processed in discovery manager
                    if url_data.get('url_id'):
                        self.url_manager.mark_url_processed(url_data['url_id'], result['status'] == 'success')
                    
                    # Research-validated production delay
                    delay = random.uniform(*self.processing_config['request_delay_range'])
                    time.sleep(delay)
                    
                    self.url_queue.task_done()
                    
                except queue.Empty:
                    # No more URLs to process
                    break
                except Exception as e:
                    print(f"❌ Worker {worker_id} error processing property: {str(e)}")
                    self.error_queue.put({
                        'worker_id': worker_id,
                        'batch_number': batch_number,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat(),
                        'url_data': url_data if 'url_data' in locals() else None
                    })
                    
                    if 'url_data' in locals():
                        self.url_queue.task_done()
        
        finally:
            driver.quit()
            print(f"🔧 Production Worker {worker_id} finished. Processed {processed_count} properties")
    
    def _process_single_property_production(self, driver: webdriver.Chrome, extractor: DetailedPropertyExtractor, 
                                          url_data: Dict[str, Any], worker_id: str) -> Dict[str, Any]:
        """Process a single property with production optimization"""
        
        url = url_data['url']
        start_time = time.time()
        
        try:
            # Navigate to property page
            driver.get(url)
            
            # Optimized page load wait
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Research-validated wait for dynamic content
            time.sleep(3)
            
            # Extract property details with production optimization
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            property_model = DetailedPropertyModel()
            
            # Extract priority sections (100% availability)
            priority_sections_extracted = 0
            secondary_sections_extracted = 0
            section_results = {}
            
            # Process priority sections first
            for section in self.priority_sections:
                try:
                    success = self._extract_section_optimized(extractor, soup, property_model, section)
                    section_results[section] = success
                    if success:
                        priority_sections_extracted += 1
                except Exception as e:
                    print(f"⚠️ {worker_id}: Failed to extract priority section {section}: {str(e)}")
                    section_results[section] = False
            
            # Process secondary sections
            for section in self.secondary_sections:
                try:
                    success = self._extract_section_optimized(extractor, soup, property_model, section)
                    section_results[section] = success
                    if success:
                        secondary_sections_extracted += 1
                except Exception as e:
                    print(f"⚠️ {worker_id}: Failed to extract secondary section {section}: {str(e)}")
                    section_results[section] = False
            
            processing_time = time.time() - start_time
            total_sections_extracted = priority_sections_extracted + secondary_sections_extracted
            
            # Calculate completeness
            completeness = property_model.calculate_completeness()
            
            result = {
                'status': 'success',
                'url': url,
                'url_data': url_data,
                'worker_id': worker_id,
                'processing_time': processing_time,
                'sections_extracted': total_sections_extracted,
                'priority_sections_extracted': priority_sections_extracted,
                'secondary_sections_extracted': secondary_sections_extracted,
                'section_results': section_results,
                'completeness': completeness,
                'property_data': property_model.to_dict(),
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ {worker_id}: Extracted {total_sections_extracted}/8 sections "
                  f"(P:{priority_sections_extracted}/7, S:{secondary_sections_extracted}/1) "
                  f"from {url} ({completeness:.1f}% complete) in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            print(f"❌ {worker_id}: Failed to process {url}: {str(e)}")
            
            return {
                'status': 'error',
                'url': url,
                'url_data': url_data,
                'worker_id': worker_id,
                'processing_time': processing_time,
                'error': str(e),
                'sections_extracted': 0,
                'priority_sections_extracted': 0,
                'secondary_sections_extracted': 0,
                'timestamp': datetime.now().isoformat()
            }
    
    def _extract_section_optimized(self, extractor: DetailedPropertyExtractor, soup: BeautifulSoup, 
                                 property_model: DetailedPropertyModel, section: str) -> bool:
        """Extract a specific section with optimization"""
        
        try:
            if section == 'amenities':
                extractor._extract_amenities(soup, property_model)
                return len(property_model.amenities) > 0
            elif section == 'floor_plan':
                extractor._extract_floor_plan(soup, property_model)
                return bool(property_model.floor_plan)
            elif section == 'neighborhood':
                extractor._extract_neighborhood(soup, property_model)
                return len(property_model.neighborhood) > 0
            elif section == 'pricing_details':
                extractor._extract_pricing_details(soup, property_model)
                return bool(property_model.pricing_details)
            elif section == 'project_info':
                extractor._extract_project_info(soup, property_model)
                return bool(property_model.project_info)
            elif section == 'specifications':
                extractor._extract_specifications(soup, property_model)
                return bool(property_model.specifications)
            elif section == 'location_details':
                extractor._extract_location_details(soup, property_model)
                return bool(property_model.location_details)
            elif section == 'images':
                extractor._extract_images(soup, property_model)
                return len(property_model.images) > 0
            
            return False
            
        except Exception:
            return False
    
    def _setup_production_browser(self) -> webdriver.Chrome:
        """Setup optimized browser for production processing"""
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Production anti-detection measures
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Production performance optimizations
        chrome_options.add_argument('--disable-images')  # Faster loading
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--disable-default-apps')
        
        # User agent rotation for production
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # Execute script to hide automation
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver

    def _calculate_current_error_rate(self) -> float:
        """Calculate current error rate"""

        total = self.stats['total_properties_processed']
        if total == 0:
            return 0.0

        return self.stats['failed_extractions'] / total

    def _collect_and_analyze_production_results(self) -> List[Dict[str, Any]]:
        """Collect and analyze all production processing results"""

        results = []

        # Collect all results from queue
        while not self.results_queue.empty():
            try:
                result = self.results_queue.get_nowait()
                results.append(result)
            except queue.Empty:
                break

        # Analyze section success rates
        if results:
            successful_results = [r for r in results if r['status'] == 'success']

            for section in self.all_target_sections:
                section_successes = sum(1 for r in successful_results
                                      if r.get('section_results', {}).get(section, False))
                self.stats['section_success_rates'][section] = (
                    section_successes / len(successful_results) * 100 if successful_results else 0
                )

            # Analyze by property type
            property_type_stats = {}
            for result in successful_results:
                prop_type = result.get('url_data', {}).get('expected_property_type', 'unknown')
                if prop_type not in property_type_stats:
                    property_type_stats[prop_type] = {
                        'count': 0,
                        'total_sections': 0,
                        'priority_sections': 0,
                        'secondary_sections': 0
                    }

                property_type_stats[prop_type]['count'] += 1
                property_type_stats[prop_type]['total_sections'] += result.get('sections_extracted', 0)
                property_type_stats[prop_type]['priority_sections'] += result.get('priority_sections_extracted', 0)
                property_type_stats[prop_type]['secondary_sections'] += result.get('secondary_sections_extracted', 0)

            # Calculate averages
            for prop_type, stats in property_type_stats.items():
                if stats['count'] > 0:
                    stats['avg_total_sections'] = stats['total_sections'] / stats['count']
                    stats['avg_priority_sections'] = stats['priority_sections'] / stats['count']
                    stats['avg_secondary_sections'] = stats['secondary_sections'] / stats['count']

            self.stats['property_type_stats'] = property_type_stats

        return results

    def _save_production_results(self, results: List[Dict[str, Any]], session_id: str):
        """Save production processing results to files"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create production results directory
        results_dir = f"production_results_{session_id}_{timestamp}"
        os.makedirs(results_dir, exist_ok=True)

        # Save detailed results
        results_filename = os.path.join(results_dir, "detailed_results.json")
        with open(results_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'session_id': session_id,
                'timestamp': timestamp,
                'statistics': self.stats,
                'results': results
            }, f, indent=2, ensure_ascii=False, default=str)

        # Save CSV summary
        csv_filename = os.path.join(results_dir, "production_summary.csv")
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            import csv
            writer = csv.writer(f)

            # Write header
            writer.writerow(['URL', 'Status', 'Sections_Extracted', 'Priority_Sections', 'Secondary_Sections',
                           'Completeness', 'Processing_Time', 'Property_Type', 'Worker_ID'])

            # Write results
            for result in results:
                writer.writerow([
                    result.get('url', ''),
                    result.get('status', ''),
                    result.get('sections_extracted', 0),
                    result.get('priority_sections_extracted', 0),
                    result.get('secondary_sections_extracted', 0),
                    result.get('completeness', 0),
                    result.get('processing_time', 0),
                    result.get('url_data', {}).get('expected_property_type', ''),
                    result.get('worker_id', '')
                ])

        # Save property data in structured format
        property_data_filename = os.path.join(results_dir, "extracted_property_data.json")
        property_data = []
        for result in results:
            if result['status'] == 'success' and 'property_data' in result:
                property_data.append({
                    'url': result['url'],
                    'extraction_timestamp': result['timestamp'],
                    'completeness': result['completeness'],
                    'property_data': result['property_data']
                })

        with open(property_data_filename, 'w', encoding='utf-8') as f:
            json.dump(property_data, f, indent=2, ensure_ascii=False, default=str)

        print(f"📁 Production results saved to: {results_dir}/")
        print(f"   📄 Detailed results: detailed_results.json")
        print(f"   📊 Summary: production_summary.csv")
        print(f"   🏠 Property data: extracted_property_data.json")

    def _generate_production_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive production report"""

        successful_results = [r for r in results if r['status'] == 'success']
        failed_results = [r for r in results if r['status'] == 'error']

        report = {
            'executive_summary': {
                'total_properties_processed': len(results),
                'successful_extractions': len(successful_results),
                'failed_extractions': len(failed_results),
                'success_rate': (len(successful_results) / len(results) * 100) if results else 0,
                'average_sections_per_property': statistics.mean([r.get('sections_extracted', 0) for r in successful_results]) if successful_results else 0,
                'average_priority_sections': statistics.mean([r.get('priority_sections_extracted', 0) for r in successful_results]) if successful_results else 0,
                'average_secondary_sections': statistics.mean([r.get('secondary_sections_extracted', 0) for r in successful_results]) if successful_results else 0
            },
            'performance_metrics': {
                'average_processing_time': statistics.mean([r.get('processing_time', 0) for r in successful_results]) if successful_results else 0,
                'throughput_per_minute': self.stats.get('throughput_per_minute', 0),
                'batch_performance': self.stats.get('batch_performance', [])
            },
            'data_quality_metrics': {
                'section_success_rates': self.stats.get('section_success_rates', {}),
                'priority_sections_performance': {
                    section: self.stats['section_success_rates'].get(section, 0)
                    for section in self.priority_sections
                },
                'secondary_sections_performance': {
                    section: self.stats['section_success_rates'].get(section, 0)
                    for section in self.secondary_sections
                }
            },
            'property_type_analysis': self.stats.get('property_type_stats', {}),
            'error_analysis': {
                'error_rate': self.stats.get('error_rate', 0),
                'common_errors': self._analyze_common_errors(),
                'failed_urls': [r.get('url', '') for r in failed_results]
            },
            'recommendations': self._generate_production_recommendations(successful_results, failed_results)
        }

        return report

    def _analyze_common_errors(self) -> List[Dict[str, Any]]:
        """Analyze common errors from error queue"""

        errors = []
        while not self.error_queue.empty():
            try:
                error = self.error_queue.get_nowait()
                errors.append(error)
            except queue.Empty:
                break

        # Group errors by type
        error_groups = {}
        for error in errors:
            error_msg = error.get('error', 'Unknown error')
            error_type = error_msg.split(':')[0] if ':' in error_msg else error_msg

            if error_type not in error_groups:
                error_groups[error_type] = {
                    'count': 0,
                    'examples': []
                }

            error_groups[error_type]['count'] += 1
            if len(error_groups[error_type]['examples']) < 3:
                error_groups[error_type]['examples'].append(error_msg)

        # Convert to sorted list
        common_errors = [
            {
                'error_type': error_type,
                'count': data['count'],
                'examples': data['examples']
            }
            for error_type, data in sorted(error_groups.items(), key=lambda x: x[1]['count'], reverse=True)
        ]

        return common_errors

    def _generate_production_recommendations(self, successful_results: List[Dict[str, Any]],
                                           failed_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate production recommendations based on results"""

        recommendations = []

        # Success rate recommendations
        success_rate = (len(successful_results) / (len(successful_results) + len(failed_results)) * 100) if (successful_results or failed_results) else 0

        if success_rate >= 95:
            recommendations.append({
                'category': 'performance',
                'priority': 'high',
                'recommendation': f"Excellent success rate ({success_rate:.1f}%) - system ready for increased volume",
                'action': 'Scale up processing capacity'
            })
        elif success_rate >= 85:
            recommendations.append({
                'category': 'performance',
                'priority': 'medium',
                'recommendation': f"Good success rate ({success_rate:.1f}%) - minor optimizations needed",
                'action': 'Investigate and resolve common error patterns'
            })
        else:
            recommendations.append({
                'category': 'performance',
                'priority': 'critical',
                'recommendation': f"Low success rate ({success_rate:.1f}%) - requires immediate attention",
                'action': 'Review error patterns and implement fixes before scaling'
            })

        # Section extraction recommendations
        priority_section_avg = statistics.mean([r.get('priority_sections_extracted', 0) for r in successful_results]) if successful_results else 0

        if priority_section_avg >= 6.5:  # 93% of 7 priority sections
            recommendations.append({
                'category': 'data_quality',
                'priority': 'high',
                'recommendation': f"Excellent priority section extraction ({priority_section_avg:.1f}/7 avg) - maintain current approach",
                'action': 'Continue with current extraction methods'
            })
        else:
            recommendations.append({
                'category': 'data_quality',
                'priority': 'high',
                'recommendation': f"Priority section extraction needs improvement ({priority_section_avg:.1f}/7 avg)",
                'action': 'Review and optimize extraction selectors for priority sections'
            })

        # Throughput recommendations
        throughput = self.stats.get('throughput_per_minute', 0)

        if throughput >= 10:
            recommendations.append({
                'category': 'throughput',
                'priority': 'medium',
                'recommendation': f"Excellent throughput ({throughput:.1f} properties/minute) - consider scaling",
                'action': 'Evaluate infrastructure for increased parallel processing'
            })
        elif throughput >= 5:
            recommendations.append({
                'category': 'throughput',
                'priority': 'medium',
                'recommendation': f"Good throughput ({throughput:.1f} properties/minute) - optimization opportunities exist",
                'action': 'Optimize request delays and worker configuration'
            })
        else:
            recommendations.append({
                'category': 'throughput',
                'priority': 'high',
                'recommendation': f"Low throughput ({throughput:.1f} properties/minute) - requires optimization",
                'action': 'Review processing bottlenecks and optimize system configuration'
            })

        return recommendations

    def _finalize_production_stats(self) -> Dict[str, Any]:
        """Finalize production processing statistics"""

        self.stats['end_time'] = datetime.now()

        if self.stats['start_time']:
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()

            if self.stats['total_properties_processed'] > 0:
                self.stats['average_processing_time'] = duration / self.stats['total_properties_processed']
                self.stats['throughput_per_minute'] = (self.stats['total_properties_processed'] / duration) * 60

            self.stats['error_rate'] = (
                self.stats['failed_extractions'] / self.stats['total_properties_processed'] * 100
                if self.stats['total_properties_processed'] > 0 else 0
            )

        return self.stats

    def _log_production_statistics(self):
        """Log final production processing statistics"""

        print("\n📊 PRODUCTION PARALLEL PROCESSING STATISTICS")
        print("=" * 70)
        print(f"🔍 Total Properties Processed: {self.stats['total_properties_processed']}")
        print(f"✅ Successful Extractions: {self.stats['successful_extractions']}")
        print(f"❌ Failed Extractions: {self.stats['failed_extractions']}")
        print(f"📈 Success Rate: {100 - self.stats['error_rate']:.1f}%")
        print(f"⚡ Throughput: {self.stats['throughput_per_minute']:.1f} properties/minute")
        print(f"📊 Total Data Sections: {self.stats['total_data_sections_extracted']}")
        print(f"🎯 Priority Sections: {self.stats['priority_sections_extracted']}")
        print(f"🎯 Secondary Sections: {self.stats['secondary_sections_extracted']}")

        print(f"\n🎯 PRIORITY SECTION SUCCESS RATES (100% availability expected):")
        for section in self.priority_sections:
            rate = self.stats['section_success_rates'].get(section, 0)
            status = "🟢" if rate > 90 else "🟡" if rate > 70 else "🔴"
            print(f"   {status} {section}: {rate:.1f}%")

        print(f"\n🎯 SECONDARY SECTION SUCCESS RATES (76% availability expected):")
        for section in self.secondary_sections:
            rate = self.stats['section_success_rates'].get(section, 0)
            status = "🟢" if rate > 70 else "🟡" if rate > 50 else "🔴"
            print(f"   {status} {section}: {rate:.1f}%")

        if self.stats['property_type_stats']:
            print(f"\n🏠 PROPERTY TYPE PERFORMANCE:")
            for prop_type, stats in self.stats['property_type_stats'].items():
                print(f"   📋 {prop_type}: {stats['count']} properties, "
                      f"{stats.get('avg_total_sections', 0):.1f} avg sections")


def main():
    """Main function for testing production parallel processing"""

    print("🚀 Production Parallel Property Processor")
    print("Testing production-ready parallel processing implementation...")

    try:
        # Load configuration
        with open('config/scraper_config.json', 'r') as f:
            config = json.load(f)

        # Initialize processor
        processor = ProductionParallelProcessor(config)

        # Test production parallel processing
        session_id = f"production_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        result = processor.process_properties_production(
            session_id=session_id,
            max_properties=50  # Test with 50 properties
        )

        if result['status'] == 'success':
            print("\n✅ PRODUCTION PARALLEL PROCESSING TEST SUCCESSFUL!")
            stats = result['statistics']
            print(f"📊 Processed: {stats['total_properties_processed']} properties")
            print(f"✅ Success Rate: {100 - stats['error_rate']:.1f}%")
            print(f"⚡ Throughput: {stats['throughput_per_minute']:.1f} properties/minute")
            print(f"🎯 Priority Sections: {stats['priority_sections_extracted']}")
            print(f"🎯 Secondary Sections: {stats['secondary_sections_extracted']}")
        else:
            print(f"\n❌ PRODUCTION PARALLEL PROCESSING TEST FAILED: {result.get('error', 'Unknown error')}")

        return result

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return None


if __name__ == "__main__":
    main()
