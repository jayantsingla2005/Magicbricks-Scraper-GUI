#!/usr/bin/env python3
"""
Simple Parallel Processing Test
Minimal test to validate parallel processing concepts without complex logging.
"""

import time
import json
import threading
import queue
import random
from typing import Dict, List, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# BeautifulSoup for parsing
from bs4 import BeautifulSoup


class SimpleParallelProcessor:
    """
    Simple parallel property processing for testing core concepts
    """
    
    def __init__(self):
        """Initialize simple parallel processor"""
        
        # Research-validated settings
        self.config = {
            'max_workers': 3,  # Conservative for testing
            'request_delay_range': (4.5, 5.3),  # Research: 4.9s ± 0.4s
            'timeout_per_property': 30,
            'max_properties': 5  # Small test batch
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
            'section_success_rates': {section: 0 for section in self.target_sections}
        }
        
        # Thread management
        self.results_queue = queue.Queue()
        self.processing_lock = threading.Lock()
        
        print("🚀 Simple Parallel Processor initialized")
        print(f"⚙️ Configuration: {self.config['max_workers']} workers, "
              f"{self.config['request_delay_range']} delay range")
    
    def test_parallel_processing(self) -> Dict[str, Any]:
        """
        Test parallel processing with sample URLs
        """
        
        print("\n🚀 Starting Simple Parallel Processing Test")
        print("="*50)
        
        self.stats['start_time'] = datetime.now()
        
        try:
            # Use sample URLs from our CSV data
            sample_urls = self._get_sample_urls()
            
            if not sample_urls:
                print("❌ No sample URLs available for testing")
                return {'status': 'error', 'error': 'No URLs available'}
            
            print(f"✅ Testing with {len(sample_urls)} sample URLs")
            
            # Process URLs in parallel
            self._process_urls_parallel(sample_urls)
            
            # Collect results
            results = self._collect_results()
            
            # Finalize statistics
            self._finalize_stats()
            
            print("✅ Simple parallel processing test complete!")
            self._print_statistics()
            
            return {
                'status': 'success',
                'statistics': self.stats,
                'results': results
            }
            
        except Exception as e:
            print(f"❌ Parallel processing test failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'statistics': self.stats
            }
    
    def _get_sample_urls(self) -> List[str]:
        """Get sample URLs for testing"""
        
        # Try to load from CSV
        import csv
        import os
        
        sample_urls = []
        
        # Look for CSV files
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv') and 'properties' in f.lower()]
        
        if csv_files:
            print(f"📄 Loading URLs from {csv_files[0]}")
            
            try:
                with open(csv_files[0], 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    for row in reader:
                        if 'property_url' in row and row['property_url']:
                            url = row['property_url'].strip()
                            if url.startswith('http') and 'magicbricks.com' in url:
                                sample_urls.append(url)
                        
                        if len(sample_urls) >= self.config['max_properties']:
                            break
                
                print(f"✅ Loaded {len(sample_urls)} URLs from CSV")
                
            except Exception as e:
                print(f"⚠️ Error reading CSV: {str(e)}")
        
        # Fallback to hardcoded URLs if CSV loading fails
        if not sample_urls:
            print("🔄 Using fallback sample URLs")
            sample_urls = [
                'https://www.magicbricks.com/vipul-greens-sector-48-gurgaon-pdpid-4d4235303030333036',
                'https://www.magicbricks.com/property-detail/3-bhk-apartment-dlf-phase-2-gurgaon',
                'https://www.magicbricks.com/property-detail/2-bhk-apartment-sector-45-gurgaon'
            ]
        
        return sample_urls[:self.config['max_properties']]
    
    def _process_urls_parallel(self, urls: List[str]):
        """Process URLs using parallel workers"""
        
        print(f"🔄 Processing {len(urls)} URLs with {self.config['max_workers']} workers")
        
        # Process with thread pool
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            # Submit tasks
            futures = []
            for i, url in enumerate(urls):
                future = executor.submit(self._process_single_url, url, f"worker-{i+1}")
                futures.append(future)
            
            # Wait for completion
            for future in as_completed(futures):
                try:
                    result = future.result()
                    self.results_queue.put(result)
                    
                    # Update statistics
                    with self.processing_lock:
                        self.stats['total_properties_processed'] += 1
                        if result['status'] == 'success':
                            self.stats['successful_extractions'] += 1
                            self.stats['total_data_sections_extracted'] += result.get('sections_extracted', 0)
                        else:
                            self.stats['failed_extractions'] += 1
                    
                except Exception as e:
                    print(f"❌ Worker error: {str(e)}")
                    with self.processing_lock:
                        self.stats['total_properties_processed'] += 1
                        self.stats['failed_extractions'] += 1
    
    def _process_single_url(self, url: str, worker_id: str) -> Dict[str, Any]:
        """Process a single URL"""
        
        start_time = time.time()
        
        try:
            print(f"🔍 {worker_id}: Processing {url}")
            
            # Setup browser
            driver = self._setup_browser()
            
            # Navigate to URL
            driver.get(url)
            
            # Wait for page load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            # Parse page
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Analyze data sections
            sections_found = self._analyze_data_sections(soup)
            
            driver.quit()
            
            processing_time = time.time() - start_time
            
            print(f"✅ {worker_id}: Found {sections_found}/8 sections in {processing_time:.2f}s")
            
            # Research-validated delay
            delay = random.uniform(*self.config['request_delay_range'])
            time.sleep(delay)
            
            return {
                'status': 'success',
                'url': url,
                'worker_id': worker_id,
                'processing_time': processing_time,
                'sections_extracted': sections_found,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            print(f"❌ {worker_id}: Failed to process {url}: {str(e)}")
            
            return {
                'status': 'error',
                'url': url,
                'worker_id': worker_id,
                'processing_time': processing_time,
                'error': str(e),
                'sections_extracted': 0,
                'timestamp': datetime.now().isoformat()
            }
    
    def _setup_browser(self) -> webdriver.Chrome:
        """Setup browser for processing"""
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Anti-detection measures
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _analyze_data_sections(self, soup: BeautifulSoup) -> int:
        """Analyze data sections availability"""
        
        sections_found = 0
        page_text = soup.get_text().lower()
        
        # Search patterns for each section
        search_patterns = {
            'amenities': ['amenity', 'amenities', 'feature', 'facilities'],
            'floor_plan': ['floor', 'plan', 'layout', 'bhk'],
            'neighborhood': ['nearby', 'locality', 'neighborhood'],
            'pricing_details': ['price', 'cost', 'payment', 'emi'],
            'project_info': ['project', 'builder', 'developer'],
            'specifications': ['specification', 'specs', 'construction'],
            'location_details': ['location', 'address', 'map'],
            'images': ['image', 'photo', 'gallery']
        }
        
        for section_name, patterns in search_patterns.items():
            found = False
            
            for pattern in patterns:
                if pattern in page_text or soup.find(class_=lambda x: x and pattern in x.lower()):
                    found = True
                    break
            
            if found:
                sections_found += 1
        
        return sections_found
    
    def _collect_results(self) -> List[Dict[str, Any]]:
        """Collect all processing results"""
        
        results = []
        
        while not self.results_queue.empty():
            try:
                result = self.results_queue.get_nowait()
                results.append(result)
            except queue.Empty:
                break
        
        return results
    
    def _finalize_stats(self):
        """Finalize processing statistics"""
        
        self.stats['end_time'] = datetime.now()
        
        if self.stats['start_time']:
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            
            if self.stats['total_properties_processed'] > 0:
                self.stats['throughput_per_minute'] = (self.stats['total_properties_processed'] / duration) * 60
                self.stats['success_rate'] = (self.stats['successful_extractions'] / self.stats['total_properties_processed']) * 100
    
    def _print_statistics(self):
        """Print processing statistics"""
        
        print("\n📊 SIMPLE PARALLEL PROCESSING STATISTICS")
        print("="*50)
        print(f"🔍 Total Properties Processed: {self.stats['total_properties_processed']}")
        print(f"✅ Successful Extractions: {self.stats['successful_extractions']}")
        print(f"❌ Failed Extractions: {self.stats['failed_extractions']}")
        
        if 'success_rate' in self.stats:
            print(f"📈 Success Rate: {self.stats['success_rate']:.1f}%")
        
        if 'throughput_per_minute' in self.stats:
            print(f"⚡ Throughput: {self.stats['throughput_per_minute']:.1f} properties/minute")
        
        print(f"📊 Total Data Sections: {self.stats['total_data_sections_extracted']}")


def main():
    """Main test function"""
    
    print("🧪 Simple Parallel Processing Test")
    print("Testing research-validated parallel processing concepts...")
    print()
    
    try:
        # Initialize processor
        processor = SimpleParallelProcessor()
        
        # Run test
        result = processor.test_parallel_processing()
        
        if result['status'] == 'success':
            print("\n✅ SIMPLE PARALLEL PROCESSING TEST SUCCESSFUL!")
            stats = result['statistics']
            print(f"📊 Processed: {stats['total_properties_processed']} properties")
            if 'success_rate' in stats:
                print(f"✅ Success Rate: {stats['success_rate']:.1f}%")
            if 'throughput_per_minute' in stats:
                print(f"⚡ Throughput: {stats['throughput_per_minute']:.1f} properties/minute")
        else:
            print(f"\n❌ SIMPLE PARALLEL PROCESSING TEST FAILED: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return None


if __name__ == "__main__":
    main()
