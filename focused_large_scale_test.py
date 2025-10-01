#!/usr/bin/env python3
"""
Focused Large-Scale Testing for MagicBricks Scraper
Tests large-scale functionality with proper method calls
"""

import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode

class FocusedLargeScaleTest:
    """Focused testing for large-scale scraping functionality"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for testing"""
        log_filename = f"large_scale_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Large-Scale Testing Started")
        
    def test_large_scale_scraping(self, max_pages: int = 50, city: str = "gurgaon") -> Dict[str, Any]:
        """Test large-scale scraping functionality"""
        self.logger.info(f"Testing Large-Scale Scraping: {max_pages} pages in {city}")
        
        try:
            # Configure for comprehensive testing
            test_config = {
                'individual_delay_min': 1,
                'individual_delay_max': 3,
                'batch_break_delay': 5,
                'batch_size': 10,
                'page_delay_min': 1,
                'page_delay_max': 2,
                'max_retries': 2,
                'concurrent_pages': 3,
                'memory_optimization': True
            }
            
            scraper = IntegratedMagicBricksScraper(custom_config=test_config)
            
            # Test listing page scraping
            start_time = time.time()
            
            self.logger.info(f"Starting listing page scraping...")
            listing_results = scraper.scrape_properties_with_incremental(
                city=city,
                mode=ScrapingMode.FULL,
                max_pages=max_pages,
                include_individual_pages=False,
                export_formats=['csv']
            )
            
            listing_time = time.time() - start_time
            
            # Analyze results
            properties_found = len(listing_results.get('properties', []))
            pages_scraped = listing_results.get('pages_scraped', 0)
            
            self.logger.info(f"Listing scraping complete:")
            self.logger.info(f"   Pages scraped: {pages_scraped}")
            self.logger.info(f"   Properties found: {properties_found}")
            self.logger.info(f"   Time taken: {listing_time:.1f}s")
            self.logger.info(f"   Speed: {properties_found/listing_time:.1f} properties/second")
            
            # Test individual property scraping if we have URLs
            individual_results = None
            if properties_found > 0:
                properties = listing_results.get('properties', [])
                property_urls = [prop.get('property_url') for prop in properties if prop.get('property_url')]
                
                if property_urls:
                    # Test with a sample of URLs
                    sample_size = min(20, len(property_urls))
                    test_urls = property_urls[:sample_size]
                    
                    self.logger.info(f"Testing individual property scraping: {sample_size} properties")
                    
                    individual_start = time.time()
                    detailed_properties = scraper.scrape_individual_property_pages(
                        property_urls=test_urls,
                        batch_size=5,
                        force_rescrape=False
                    )
                    individual_time = time.time() - individual_start
                    
                    success_count = len(detailed_properties)
                    success_rate = (success_count / len(test_urls)) * 100 if test_urls else 0
                    
                    individual_results = {
                        'urls_tested': len(test_urls),
                        'successful_extractions': success_count,
                        'success_rate': success_rate,
                        'time_taken': individual_time,
                        'properties_per_second': success_count/individual_time if individual_time > 0 else 0
                    }
                    
                    self.logger.info(f"Individual property scraping complete:")
                    self.logger.info(f"   URLs tested: {len(test_urls)}")
                    self.logger.info(f"   Successful extractions: {success_count}")
                    self.logger.info(f"   Success rate: {success_rate:.1f}%")
                    self.logger.info(f"   Time taken: {individual_time:.1f}s")
                    self.logger.info(f"   Speed: {success_count/individual_time:.1f} properties/second")
            
            return {
                'success': True,
                'pages_scraped': pages_scraped,
                'properties_found': properties_found,
                'time_taken': listing_time,
                'properties_per_second': properties_found/listing_time if listing_time > 0 else 0,
                'listing_results': listing_results,
                'individual_results': individual_results
            }
            
        except Exception as e:
            self.logger.error(f"Large-scale scraping failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_incremental_functionality(self, city: str = "gurgaon") -> Dict[str, Any]:
        """Test incremental scraping functionality"""
        self.logger.info(f"Testing Incremental Functionality in {city}")
        
        try:
            test_config = {
                'individual_delay_min': 1,
                'individual_delay_max': 2,
                'batch_break_delay': 3,
                'page_delay_min': 1,
                'page_delay_max': 2,
                'max_retries': 2
            }
            
            scraper = IntegratedMagicBricksScraper(custom_config=test_config)
            
            # First run - baseline
            self.logger.info("Running baseline scraping (10 pages)...")
            baseline_start = time.time()
            baseline_results = scraper.scrape_properties_with_incremental(
                city=city,
                mode=ScrapingMode.FULL,
                max_pages=10,
                include_individual_pages=False,
                export_formats=['csv']
            )
            baseline_time = time.time() - baseline_start
            baseline_properties = len(baseline_results.get('properties', []))
            
            # Second run - incremental (should be faster)
            self.logger.info("Running incremental scraping (15 pages)...")
            incremental_start = time.time()
            incremental_results = scraper.scrape_properties_with_incremental(
                city=city,
                mode=ScrapingMode.INCREMENTAL,
                max_pages=15,
                include_individual_pages=False,
                export_formats=['csv']
            )
            incremental_time = time.time() - incremental_start
            incremental_properties = len(incremental_results.get('properties', []))
            
            # Calculate efficiency
            time_efficiency = ((baseline_time - incremental_time) / baseline_time * 100) if baseline_time > 0 else 0
            
            self.logger.info(f"Incremental functionality test complete:")
            self.logger.info(f"   Baseline: {baseline_properties} properties in {baseline_time:.1f}s")
            self.logger.info(f"   Incremental: {incremental_properties} properties in {incremental_time:.1f}s")
            self.logger.info(f"   Time efficiency: {time_efficiency:.1f}%")
            
            return {
                'success': True,
                'baseline_properties': baseline_properties,
                'baseline_time': baseline_time,
                'incremental_properties': incremental_properties,
                'incremental_time': incremental_time,
                'time_efficiency': time_efficiency
            }
            
        except Exception as e:
            self.logger.error(f"Incremental functionality test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_focused_tests(self) -> Dict[str, Any]:
        """Run focused large-scale tests"""
        self.logger.info("Starting Focused Large-Scale Testing")
        
        all_results = {
            'start_time': self.start_time.isoformat(),
            'tests': {}
        }
        
        # Test 1: Large-Scale Scraping
        self.logger.info("\n" + "="*60)
        all_results['tests']['large_scale_scraping'] = self.test_large_scale_scraping(max_pages=30, city="gurgaon")
        
        # Test 2: Incremental Functionality
        self.logger.info("\n" + "="*60)
        all_results['tests']['incremental_functionality'] = self.test_incremental_functionality(city="gurgaon")
        
        # Calculate overall results
        end_time = datetime.now()
        total_time = (end_time - self.start_time).total_seconds()
        
        all_results['end_time'] = end_time.isoformat()
        all_results['total_time_seconds'] = total_time
        all_results['overall_success'] = all(
            test_result.get('success', False) 
            for test_result in all_results['tests'].values()
        )
        
        # Save results
        results_file = f"focused_large_scale_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        self.logger.info(f"\nFocused Testing Complete!")
        self.logger.info(f"   Total time: {total_time:.1f} seconds")
        self.logger.info(f"   Overall success: {'PASS' if all_results['overall_success'] else 'FAIL'}")
        self.logger.info(f"   Results saved to: {results_file}")
        
        return all_results

if __name__ == "__main__":
    test = FocusedLargeScaleTest()
    results = test.run_focused_tests()
    
    # Print summary
    print("\n" + "="*80)
    print("FOCUSED LARGE-SCALE TESTING SUMMARY")
    print("="*80)
    
    for test_name, test_result in results['tests'].items():
        status = "PASS" if test_result.get('success') else "FAIL"
        print(f"{test_name:.<50} {status}")
        
        # Print key metrics
        if test_name == 'large_scale_scraping' and test_result.get('success'):
            print(f"  Properties found: {test_result.get('properties_found', 0)}")
            print(f"  Pages scraped: {test_result.get('pages_scraped', 0)}")
            print(f"  Speed: {test_result.get('properties_per_second', 0):.1f} props/sec")
            
            if test_result.get('individual_results'):
                ind_results = test_result['individual_results']
                print(f"  Individual success rate: {ind_results.get('success_rate', 0):.1f}%")
        
        elif test_name == 'incremental_functionality' and test_result.get('success'):
            print(f"  Time efficiency: {test_result.get('time_efficiency', 0):.1f}%")
    
    print(f"\nOverall Result: {'ALL TESTS PASSED' if results['overall_success'] else 'SOME TESTS FAILED'}")
    print(f"Total Time: {results['total_time_seconds']:.1f} seconds")
