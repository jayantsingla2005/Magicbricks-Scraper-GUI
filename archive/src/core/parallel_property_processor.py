#!/usr/bin/env python3
"""
Parallel Property Processor
Implements multi-threaded detailed property scraping with research-validated timing and targeting.
Based on research findings: 4.9s delays, 8 high-availability data sections, 3-5 concurrent threads.
"""

import time
import json
import threading
import queue
import random
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
    from utils.logger import ScraperLogger
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class ParallelPropertyProcessor:
    """
    Research-validated parallel property processing system
    Implements multi-threaded detailed property scraping with optimal timing and error handling
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize parallel property processor"""
        
        self.config = config
        self.logger = ScraperLogger(config)
        
        # Research-validated settings
        self.processing_config = {
            'max_workers': 4,  # Research shows 3-5 optimal
            'request_delay_range': (4.5, 5.3),  # Research: 4.9s ± 0.4s
            'max_retries': 3,
            'timeout_per_property': 45,  # 3.27s load + processing time
            'batch_size': 20,  # Process in batches for memory management
            'error_threshold': 0.15,  # Stop if >15% error rate
            'session_rotation_interval': 50  # Rotate sessions every 50 properties
        }
        
        # Target data sections (research: 100% availability)
        self.target_sections = [
            'amenities', 'floor_plan', 'neighborhood', 'pricing_details',
            'project_info', 'specifications', 'location_details', 'images'
        ]
        
        # Processing statistics
        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_properties_processed': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'total_data_sections_extracted': 0,
            'average_processing_time': 0,
            'error_rate': 0,
            'throughput_per_minute': 0,
            'section_success_rates': {section: 0 for section in self.target_sections}
        }
        
        # Thread management
        self.url_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.error_queue = queue.Queue()
        self.processing_lock = threading.Lock()
        
        # Initialize components
        self.url_manager = URLDiscoveryManager()

        print("🚀 Parallel Property Processor initialized")
        print(f"⚙️ Configuration: {self.processing_config['max_workers']} workers, "
              f"{self.processing_config['request_delay_range']} delay range")
        print(f"🎯 Target sections: {', '.join(self.target_sections)}")
    
    def process_properties_parallel(self, session_id: str, max_properties: int = 100) -> Dict[str, Any]:
        """
        Process properties in parallel using research-validated approach
        """
        
        print("🚀 Starting parallel property processing")
        print(f"📊 Target: {max_properties} properties with {self.processing_config['max_workers']} workers")
        
        self.stats['start_time'] = datetime.now()
        
        try:
            # Step 1: Load property URLs
            self.logger.info("📡 Loading property URLs from discovery queue...")
            property_urls = self._load_property_urls(session_id, max_properties)
            
            if not property_urls:
                self.logger.warning("⚠️ No property URLs available for processing")
                return self._finalize_stats()
            
            self.logger.info(f"✅ Loaded {len(property_urls)} property URLs for processing")
            
            # Step 2: Process in parallel batches
            self.logger.info("🔄 Starting parallel processing...")
            self._process_urls_in_parallel(property_urls)
            
            # Step 3: Collect and analyze results
            self.logger.info("📊 Collecting and analyzing results...")
            results = self._collect_and_analyze_results()
            
            # Step 4: Save results
            self.logger.info("💾 Saving processing results...")
            self._save_processing_results(results, session_id)
            
            # Finalize statistics
            final_stats = self._finalize_stats()
            
            self.logger.info("✅ Parallel property processing complete!")
            self._log_final_statistics()
            
            return {
                'status': 'success',
                'statistics': final_stats,
                'results': results,
                'session_id': session_id
            }
            
        except Exception as e:
            self.logger.error(f"❌ Parallel processing failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'statistics': self._finalize_stats(),
                'session_id': session_id
            }
    
    def _load_property_urls(self, session_id: str, max_properties: int) -> List[Dict[str, Any]]:
        """Load property URLs from discovery queue"""
        
        # Get pending URLs from discovery manager
        pending_urls = self.url_manager.get_pending_urls(limit=max_properties * 2)  # Get extra for filtering
        
        if not pending_urls:
            # Try to discover new URLs if none pending
            self.logger.info("🔍 No pending URLs found, attempting discovery...")
            discovery_result = self.url_manager.discover_urls_from_listings(
                start_page=1,
                max_pages=5,
                session_id=session_id
            )
            
            # Try again after discovery
            pending_urls = self.url_manager.get_pending_urls(limit=max_properties)
        
        # Format URLs for processing
        property_urls = []
        for url_data in pending_urls[:max_properties]:
            property_urls.append({
                'url': url_data['url'],
                'url_id': url_data.get('id'),
                'priority': url_data.get('priority', 2),
                'metadata': url_data.get('metadata', {}),
                'discovery_session': url_data.get('session_id', session_id)
            })
        
        return property_urls
    
    def _process_urls_in_parallel(self, property_urls: List[Dict[str, Any]]):
        """Process URLs using parallel workers"""
        
        # Add URLs to processing queue
        for url_data in property_urls:
            self.url_queue.put(url_data)
        
        # Process in batches to manage memory
        total_urls = len(property_urls)
        batch_size = self.processing_config['batch_size']
        
        for batch_start in range(0, total_urls, batch_size):
            batch_end = min(batch_start + batch_size, total_urls)
            batch_urls = property_urls[batch_start:batch_end]
            
            self.logger.info(f"🔄 Processing batch {batch_start//batch_size + 1}: "
                           f"URLs {batch_start + 1}-{batch_end} of {total_urls}")
            
            # Process batch with thread pool
            with ThreadPoolExecutor(max_workers=self.processing_config['max_workers']) as executor:
                # Submit worker tasks
                futures = []
                for i in range(self.processing_config['max_workers']):
                    future = executor.submit(self._worker_thread, f"worker-{i+1}")
                    futures.append(future)
                
                # Wait for batch completion
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        self.logger.error(f"❌ Worker thread error: {str(e)}")
            
            # Check error rate and stop if too high
            current_error_rate = self._calculate_current_error_rate()
            if current_error_rate > self.processing_config['error_threshold']:
                self.logger.warning(f"⚠️ High error rate detected ({current_error_rate:.1%}), stopping processing")
                break
            
            self.logger.info(f"✅ Batch {batch_start//batch_size + 1} complete. "
                           f"Success rate: {(1-current_error_rate):.1%}")
    
    def _worker_thread(self, worker_id: str):
        """Individual worker thread for processing properties"""
        
        self.logger.info(f"🔧 Worker {worker_id} started")
        
        # Setup browser for this worker
        driver = self._setup_worker_browser()
        extractor = DetailedPropertyExtractor(self.config)
        
        processed_count = 0
        
        try:
            while True:
                try:
                    # Get next URL from queue (with timeout)
                    url_data = self.url_queue.get(timeout=5)
                    
                    if url_data is None:  # Poison pill to stop worker
                        break
                    
                    # Process single property
                    result = self._process_single_property(driver, extractor, url_data, worker_id)
                    
                    # Store result
                    self.results_queue.put(result)
                    
                    # Update statistics
                    with self.processing_lock:
                        self.stats['total_properties_processed'] += 1
                        if result['status'] == 'success':
                            self.stats['successful_extractions'] += 1
                            self.stats['total_data_sections_extracted'] += result.get('sections_extracted', 0)
                        else:
                            self.stats['failed_extractions'] += 1
                    
                    processed_count += 1
                    
                    # Mark URL as processed in discovery manager
                    if url_data.get('url_id'):
                        self.url_manager.mark_url_processed(url_data['url_id'], result['status'] == 'success')
                    
                    # Research-validated delay between requests
                    delay = random.uniform(*self.processing_config['request_delay_range'])
                    time.sleep(delay)
                    
                    self.url_queue.task_done()
                    
                except queue.Empty:
                    # No more URLs to process
                    break
                except Exception as e:
                    self.logger.error(f"❌ Worker {worker_id} error processing property: {str(e)}")
                    self.error_queue.put({
                        'worker_id': worker_id,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat(),
                        'url_data': url_data if 'url_data' in locals() else None
                    })
                    
                    if 'url_data' in locals():
                        self.url_queue.task_done()
        
        finally:
            driver.quit()
            self.logger.info(f"🔧 Worker {worker_id} finished. Processed {processed_count} properties")
    
    def _process_single_property(self, driver: webdriver.Chrome, extractor: DetailedPropertyExtractor, 
                                url_data: Dict[str, Any], worker_id: str) -> Dict[str, Any]:
        """Process a single property page"""
        
        url = url_data['url']
        start_time = time.time()
        
        try:
            self.logger.info(f"🔍 {worker_id}: Processing {url}")
            
            # Navigate to property page
            driver.get(url)
            
            # Wait for page load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content (research-validated)
            time.sleep(3)
            
            # Extract property details
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            property_model = DetailedPropertyModel()
            
            # Extract all target sections
            sections_extracted = 0
            section_results = {}
            
            for section in self.target_sections:
                try:
                    if section == 'amenities':
                        extractor._extract_amenities(soup, property_model)
                        section_results[section] = len(property_model.amenities) > 0
                    elif section == 'floor_plan':
                        extractor._extract_floor_plan(soup, property_model)
                        section_results[section] = bool(property_model.floor_plan)
                    elif section == 'neighborhood':
                        extractor._extract_neighborhood(soup, property_model)
                        section_results[section] = len(property_model.neighborhood) > 0
                    elif section == 'pricing_details':
                        extractor._extract_pricing_details(soup, property_model)
                        section_results[section] = bool(property_model.pricing_details)
                    elif section == 'project_info':
                        extractor._extract_project_info(soup, property_model)
                        section_results[section] = bool(property_model.project_info)
                    elif section == 'specifications':
                        extractor._extract_specifications(soup, property_model)
                        section_results[section] = bool(property_model.specifications)
                    elif section == 'location_details':
                        extractor._extract_location_details(soup, property_model)
                        section_results[section] = bool(property_model.location_details)
                    elif section == 'images':
                        extractor._extract_images(soup, property_model)
                        section_results[section] = len(property_model.images) > 0
                    
                    if section_results[section]:
                        sections_extracted += 1
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ {worker_id}: Failed to extract {section} from {url}: {str(e)}")
                    section_results[section] = False
            
            processing_time = time.time() - start_time
            
            # Calculate completeness
            completeness = property_model.calculate_completeness()
            
            result = {
                'status': 'success',
                'url': url,
                'url_data': url_data,
                'worker_id': worker_id,
                'processing_time': processing_time,
                'sections_extracted': sections_extracted,
                'section_results': section_results,
                'completeness': completeness,
                'property_data': property_model.to_dict(),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ {worker_id}: Extracted {sections_extracted}/8 sections from {url} "
                           f"({completeness:.1f}% complete) in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            self.logger.error(f"❌ {worker_id}: Failed to process {url}: {str(e)}")
            
            return {
                'status': 'error',
                'url': url,
                'url_data': url_data,
                'worker_id': worker_id,
                'processing_time': processing_time,
                'error': str(e),
                'sections_extracted': 0,
                'timestamp': datetime.now().isoformat()
            }
    
    def _setup_worker_browser(self) -> webdriver.Chrome:
        """Setup optimized browser for worker thread"""
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Anti-detection measures (research-validated)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent rotation
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        # Performance optimizations
        chrome_options.add_argument('--disable-images')  # Faster loading
        chrome_options.add_argument('--disable-javascript')  # We don't need JS for extraction
        
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
    
    def _collect_and_analyze_results(self) -> List[Dict[str, Any]]:
        """Collect and analyze all processing results"""
        
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
            
            for section in self.target_sections:
                section_successes = sum(1 for r in successful_results 
                                      if r.get('section_results', {}).get(section, False))
                self.stats['section_success_rates'][section] = (
                    section_successes / len(successful_results) * 100 if successful_results else 0
                )
        
        return results
    
    def _save_processing_results(self, results: List[Dict[str, Any]], session_id: str):
        """Save processing results to files"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        results_filename = f"parallel_processing_results_{session_id}_{timestamp}.json"
        with open(results_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'session_id': session_id,
                'timestamp': timestamp,
                'statistics': self.stats,
                'results': results
            }, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📁 Results saved: {results_filename}")
    
    def _finalize_stats(self) -> Dict[str, Any]:
        """Finalize processing statistics"""
        
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
    
    def _log_final_statistics(self):
        """Log final processing statistics"""
        
        self.logger.info("📊 PARALLEL PROCESSING STATISTICS")
        self.logger.info("=" * 50)
        self.logger.info(f"🔍 Total Properties Processed: {self.stats['total_properties_processed']}")
        self.logger.info(f"✅ Successful Extractions: {self.stats['successful_extractions']}")
        self.logger.info(f"❌ Failed Extractions: {self.stats['failed_extractions']}")
        self.logger.info(f"📈 Success Rate: {100 - self.stats['error_rate']:.1f}%")
        self.logger.info(f"⚡ Throughput: {self.stats['throughput_per_minute']:.1f} properties/minute")
        self.logger.info(f"📊 Total Data Sections: {self.stats['total_data_sections_extracted']}")
        
        self.logger.info("\n🎯 SECTION SUCCESS RATES:")
        for section, rate in self.stats['section_success_rates'].items():
            status = "🟢" if rate > 80 else "🟡" if rate > 60 else "🔴"
            self.logger.info(f"   {status} {section}: {rate:.1f}%")


def main():
    """Main function for testing parallel processing"""
    
    print("🚀 Parallel Property Processor")
    print("Testing research-validated parallel processing implementation...")
    
    try:
        # Load configuration
        with open('config/scraper_config.json', 'r') as f:
            config = json.load(f)
        
        # Initialize processor
        processor = ParallelPropertyProcessor(config)
        
        # Test parallel processing
        session_id = f"parallel_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        result = processor.process_properties_parallel(
            session_id=session_id,
            max_properties=20  # Test with 20 properties
        )
        
        if result['status'] == 'success':
            print("\n✅ PARALLEL PROCESSING TEST SUCCESSFUL!")
            stats = result['statistics']
            print(f"📊 Processed: {stats['total_properties_processed']} properties")
            print(f"✅ Success Rate: {100 - stats['error_rate']:.1f}%")
            print(f"⚡ Throughput: {stats['throughput_per_minute']:.1f} properties/minute")
        else:
            print(f"\n❌ PARALLEL PROCESSING TEST FAILED: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return None


if __name__ == "__main__":
    main()
