#!/usr/bin/env python3
"""
Production Parallel Processing Test with CSV Data
Test production system using existing CSV property data as fallback.
"""

import time
import json
import csv
import random
from typing import Dict, List, Any
from datetime import datetime

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# BeautifulSoup for parsing
from bs4 import BeautifulSoup

# Add src directory to path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / 'src'))

try:
    from src.core.detailed_property_extractor import DetailedPropertyExtractor, DetailedPropertyModel
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class ProductionCSVTester:
    """
    Production parallel processing test using CSV data
    """
    
    def __init__(self):
        """Initialize production CSV tester"""
        
        # Load configuration
        with open('config/scraper_config.json', 'r') as f:
            self.config = json.load(f)
        
        # Production-validated settings from research
        self.processing_config = {
            'max_workers': 4,
            'request_delay_range': (4.5, 5.5),
            'batch_size': 10,  # Smaller for testing
            'target_properties': 20
        }
        
        # Research-validated sections
        self.priority_sections = [
            'amenities', 'floor_plan', 'neighborhood', 'pricing_details',
            'project_info', 'location_details', 'images'
        ]
        
        self.secondary_sections = ['specifications']
        
        self.test_results = {
            'start_time': None,
            'end_time': None,
            'total_properties_processed': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'priority_sections_extracted': 0,
            'secondary_sections_extracted': 0,
            'section_success_rates': {},
            'processing_times': [],
            'property_results': []
        }
        
        print("🧪 Production CSV Tester Initialized")
        print(f"🎯 Target: {self.processing_config['target_properties']} properties")
        print(f"⚙️ Workers: {self.processing_config['max_workers']}")
    
    def test_production_with_csv(self) -> Dict[str, Any]:
        """
        Test production parallel processing using CSV property data
        """
        
        print("\n🚀 Starting Production Test with CSV Data")
        print("="*60)
        
        self.test_results['start_time'] = datetime.now()
        
        try:
            # Step 1: Load property URLs from CSV
            print("📄 Step 1: Loading Property URLs from CSV...")
            property_urls = self._load_urls_from_csv()
            
            if not property_urls:
                print("❌ No property URLs found in CSV files")
                return {'status': 'error', 'error': 'No URLs available'}
            
            print(f"✅ Loaded {len(property_urls)} property URLs for testing")
            
            # Step 2: Process properties in parallel
            print(f"\n🔄 Step 2: Processing Properties in Parallel...")
            self._process_properties_parallel(property_urls)
            
            # Step 3: Analyze results
            print(f"\n📊 Step 3: Analyzing Results...")
            self._analyze_results()
            
            # Set end time before generating report
            self.test_results['end_time'] = datetime.now()

            # Step 4: Generate report
            print(f"\n📋 Step 4: Generating Production Report...")
            report = self._generate_report()
            
            print("\n✅ Production CSV Test Complete!")
            self._print_summary()
            
            return {
                'status': 'success',
                'test_results': self.test_results,
                'report': report
            }
            
        except Exception as e:
            print(f"❌ Production CSV test failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'test_results': self.test_results
            }
    
    def _load_urls_from_csv(self) -> List[str]:
        """Load property URLs from CSV files"""
        
        property_urls = []
        
        # Look for CSV files
        import os
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv') and 'properties' in f.lower()]
        
        if not csv_files:
            print("❌ No CSV files found")
            return []
        
        print(f"📁 Found {len(csv_files)} CSV files")
        
        for csv_file in csv_files:
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    for row in reader:
                        if 'property_url' in row and row['property_url']:
                            url = row['property_url'].strip()
                            
                            if url.startswith('http') and 'magicbricks.com' in url:
                                property_urls.append(url)
                        
                        if len(property_urls) >= self.processing_config['target_properties']:
                            break
                
                print(f"✅ Loaded {len(property_urls)} URLs from {csv_file}")
                
                if len(property_urls) >= self.processing_config['target_properties']:
                    break
                
            except Exception as e:
                print(f"⚠️ Error reading {csv_file}: {str(e)}")
        
        # Shuffle and limit
        random.shuffle(property_urls)
        return property_urls[:self.processing_config['target_properties']]
    
    def _process_properties_parallel(self, property_urls: List[str]):
        """Process properties using production parallel approach"""
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import threading
        
        # Thread-safe results collection
        results_lock = threading.Lock()
        
        def worker_thread(urls_batch: List[str], worker_id: str):
            """Worker thread for processing properties"""
            
            print(f"🔧 Worker {worker_id} started with {len(urls_batch)} URLs")
            
            # Setup browser
            driver = self._setup_production_browser()
            extractor = DetailedPropertyExtractor(self.config)
            
            worker_results = []
            
            try:
                for i, url in enumerate(urls_batch, 1):
                    try:
                        print(f"🔍 {worker_id}: Processing {i}/{len(urls_batch)} - {url}")
                        
                        # Process single property
                        result = self._process_single_property(driver, extractor, url, worker_id)
                        worker_results.append(result)
                        
                        # Production delay
                        delay = random.uniform(*self.processing_config['request_delay_range'])
                        time.sleep(delay)
                        
                    except Exception as e:
                        print(f"❌ {worker_id}: Error processing {url}: {str(e)}")
                        worker_results.append({
                            'url': url,
                            'status': 'error',
                            'error': str(e),
                            'worker_id': worker_id
                        })
            
            finally:
                driver.quit()
                print(f"🔧 Worker {worker_id} finished")
            
            # Store results thread-safely
            with results_lock:
                self.test_results['property_results'].extend(worker_results)
            
            return worker_results
        
        # Split URLs into batches for workers
        batch_size = len(property_urls) // self.processing_config['max_workers']
        if batch_size == 0:
            batch_size = 1
        
        url_batches = [
            property_urls[i:i + batch_size] 
            for i in range(0, len(property_urls), batch_size)
        ]
        
        # Process with thread pool
        with ThreadPoolExecutor(max_workers=self.processing_config['max_workers']) as executor:
            futures = []
            
            for i, batch in enumerate(url_batches):
                future = executor.submit(worker_thread, batch, f"worker-{i+1}")
                futures.append(future)
            
            # Wait for completion
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"❌ Worker error: {str(e)}")
    
    def _process_single_property(self, driver: webdriver.Chrome, extractor: DetailedPropertyExtractor, 
                                url: str, worker_id: str) -> Dict[str, Any]:
        """Process a single property"""
        
        start_time = time.time()
        
        try:
            # Navigate to property page
            driver.get(url)
            
            # Wait for page load
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait for dynamic content
            time.sleep(3)
            
            # Extract property details
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            property_model = DetailedPropertyModel()
            
            # Extract sections
            priority_sections_extracted = 0
            secondary_sections_extracted = 0
            section_results = {}
            
            # Process priority sections
            for section in self.priority_sections:
                try:
                    success = self._extract_section(extractor, soup, property_model, section)
                    section_results[section] = success
                    if success:
                        priority_sections_extracted += 1
                except Exception:
                    section_results[section] = False
            
            # Process secondary sections
            for section in self.secondary_sections:
                try:
                    success = self._extract_section(extractor, soup, property_model, section)
                    section_results[section] = success
                    if success:
                        secondary_sections_extracted += 1
                except Exception:
                    section_results[section] = False
            
            processing_time = time.time() - start_time
            total_sections = priority_sections_extracted + secondary_sections_extracted
            
            result = {
                'url': url,
                'status': 'success',
                'worker_id': worker_id,
                'processing_time': processing_time,
                'total_sections_extracted': total_sections,
                'priority_sections_extracted': priority_sections_extracted,
                'secondary_sections_extracted': secondary_sections_extracted,
                'section_results': section_results,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ {worker_id}: Extracted {total_sections}/8 sections "
                  f"(P:{priority_sections_extracted}/7, S:{secondary_sections_extracted}/1) "
                  f"in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            return {
                'url': url,
                'status': 'error',
                'worker_id': worker_id,
                'processing_time': processing_time,
                'error': str(e),
                'total_sections_extracted': 0,
                'priority_sections_extracted': 0,
                'secondary_sections_extracted': 0,
                'timestamp': datetime.now().isoformat()
            }
    
    def _extract_section(self, extractor: DetailedPropertyExtractor, soup: BeautifulSoup, 
                        property_model: DetailedPropertyModel, section: str) -> bool:
        """Extract a specific section"""
        
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
        """Setup production-optimized browser"""
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Production optimizations
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-plugins')
        
        # User agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _analyze_results(self):
        """Analyze processing results"""
        
        successful_results = [r for r in self.test_results['property_results'] if r['status'] == 'success']
        failed_results = [r for r in self.test_results['property_results'] if r['status'] == 'error']
        
        self.test_results['total_properties_processed'] = len(self.test_results['property_results'])
        self.test_results['successful_extractions'] = len(successful_results)
        self.test_results['failed_extractions'] = len(failed_results)
        
        if successful_results:
            # Calculate section statistics
            self.test_results['priority_sections_extracted'] = sum(
                r['priority_sections_extracted'] for r in successful_results
            )
            self.test_results['secondary_sections_extracted'] = sum(
                r['secondary_sections_extracted'] for r in successful_results
            )
            
            # Calculate section success rates
            all_sections = self.priority_sections + self.secondary_sections
            for section in all_sections:
                section_successes = sum(
                    1 for r in successful_results 
                    if r.get('section_results', {}).get(section, False)
                )
                self.test_results['section_success_rates'][section] = (
                    section_successes / len(successful_results) * 100
                )
            
            # Processing times
            self.test_results['processing_times'] = [
                r['processing_time'] for r in successful_results
            ]
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate production test report"""
        
        duration = (self.test_results['end_time'] - self.test_results['start_time']).total_seconds()
        
        report = {
            'executive_summary': {
                'total_properties': self.test_results['total_properties_processed'],
                'successful_extractions': self.test_results['successful_extractions'],
                'success_rate': (self.test_results['successful_extractions'] / self.test_results['total_properties_processed'] * 100) if self.test_results['total_properties_processed'] > 0 else 0,
                'throughput_per_minute': (self.test_results['total_properties_processed'] / duration * 60) if duration > 0 else 0
            },
            'section_performance': {
                'priority_sections_avg': (self.test_results['priority_sections_extracted'] / self.test_results['successful_extractions']) if self.test_results['successful_extractions'] > 0 else 0,
                'secondary_sections_avg': (self.test_results['secondary_sections_extracted'] / self.test_results['successful_extractions']) if self.test_results['successful_extractions'] > 0 else 0,
                'section_success_rates': self.test_results['section_success_rates']
            },
            'performance_metrics': {
                'avg_processing_time': sum(self.test_results['processing_times']) / len(self.test_results['processing_times']) if self.test_results['processing_times'] else 0,
                'total_duration': duration
            }
        }
        
        return report
    
    def _print_summary(self):
        """Print test summary"""
        
        print("\n📊 PRODUCTION CSV TEST SUMMARY")
        print("="*50)
        print(f"🔍 Properties Processed: {self.test_results['total_properties_processed']}")
        print(f"✅ Successful: {self.test_results['successful_extractions']}")
        print(f"❌ Failed: {self.test_results['failed_extractions']}")
        
        if self.test_results['total_properties_processed'] > 0:
            success_rate = (self.test_results['successful_extractions'] / self.test_results['total_properties_processed']) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.test_results['successful_extractions'] > 0:
            priority_avg = self.test_results['priority_sections_extracted'] / self.test_results['successful_extractions']
            secondary_avg = self.test_results['secondary_sections_extracted'] / self.test_results['successful_extractions']
            print(f"🎯 Priority Sections Avg: {priority_avg:.1f}/7")
            print(f"🎯 Secondary Sections Avg: {secondary_avg:.1f}/1")
        
        if self.test_results['processing_times']:
            avg_time = sum(self.test_results['processing_times']) / len(self.test_results['processing_times'])
            print(f"⏱️ Avg Processing Time: {avg_time:.2f}s")
        
        duration = (self.test_results['end_time'] - self.test_results['start_time']).total_seconds()
        throughput = (self.test_results['total_properties_processed'] / duration * 60) if duration > 0 else 0
        print(f"⚡ Throughput: {throughput:.1f} properties/minute")


def main():
    """Main test function"""
    
    print("🧪 Production Parallel Processing Test with CSV Data")
    print("Testing production system using existing property data...")
    print()
    
    try:
        # Initialize tester
        tester = ProductionCSVTester()
        
        # Run test
        result = tester.test_production_with_csv()
        
        if result['status'] == 'success':
            print("\n✅ PRODUCTION CSV TEST SUCCESSFUL!")
            
            report = result['report']
            exec_summary = report['executive_summary']
            
            print(f"📊 Processed: {exec_summary['total_properties']} properties")
            print(f"✅ Success Rate: {exec_summary['success_rate']:.1f}%")
            print(f"⚡ Throughput: {exec_summary['throughput_per_minute']:.1f} properties/minute")
            
            section_perf = report['section_performance']
            print(f"🎯 Priority Sections: {section_perf['priority_sections_avg']:.1f}/7")
            print(f"🎯 Secondary Sections: {section_perf['secondary_sections_avg']:.1f}/1")
            
        else:
            print(f"\n❌ PRODUCTION CSV TEST FAILED: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return None


if __name__ == "__main__":
    main()
