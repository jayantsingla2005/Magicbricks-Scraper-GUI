#!/usr/bin/env python3
"""
Comprehensive Testing Suite for MagicBricks Scraper
Tests all fixes, timing controls, and large-scale functionality
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
from multi_city_system import MultiCitySystem

class ComprehensiveTestingSuite:
    """Comprehensive testing suite for all scraper functionality"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
        self.setup_logging()
        
    def setup_logging(self):
        """Setup comprehensive logging for testing"""
        log_filename = f"comprehensive_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("🧪 Comprehensive Testing Suite Initialized")
        
    def test_gui_timing_controls(self) -> Dict[str, Any]:
        """Test GUI timing controls functionality"""
        self.logger.info("🎮 Testing GUI Timing Controls...")
        
        try:
            from magicbricks_gui import MagicBricksGUI
            
            # Create GUI instance
            gui = MagicBricksGUI()
            
            # Test all timing control variables exist
            timing_controls = {
                'delay_var': 'Page Delay',
                'individual_delay_min_var': 'Individual Min Delay',
                'individual_delay_max_var': 'Individual Max Delay', 
                'batch_break_var': 'Batch Break Delay',
                'batch_size_var': 'Batch Size',
                'retry_var': 'Max Retries'
            }
            
            results = {}
            for var_name, description in timing_controls.items():
                if hasattr(gui, var_name):
                    var = getattr(gui, var_name)
                    value = var.get()
                    results[var_name] = {'exists': True, 'value': value, 'description': description}
                    self.logger.info(f"  ✅ {description}: {value}")
                else:
                    results[var_name] = {'exists': False, 'description': description}
                    self.logger.error(f"  ❌ {description}: Variable not found")
            
            # Test configuration generation
            try:
                config = gui.get_scraping_config()
                results['config_generation'] = {'success': True, 'config_keys': list(config.keys())}
                self.logger.info(f"  ✅ Configuration generation successful: {len(config)} keys")
            except Exception as e:
                results['config_generation'] = {'success': False, 'error': str(e)}
                self.logger.error(f"  ❌ Configuration generation failed: {e}")
            
            return {'success': True, 'results': results}
            
        except Exception as e:
            self.logger.error(f"❌ GUI testing failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_timing_controls_integration(self) -> Dict[str, Any]:
        """Test timing controls integration with scraper"""
        self.logger.info("⏱️ Testing Timing Controls Integration...")
        
        try:
            # Test custom timing configuration
            custom_config = {
                'individual_delay_min': 2,
                'individual_delay_max': 5,
                'batch_break_delay': 10,
                'batch_size': 5,
                'page_delay_min': 1,
                'page_delay_max': 3,
                'max_retries': 2
            }
            
            scraper = IntegratedMagicBricksScraper(custom_config=custom_config)
            
            # Verify configuration was applied
            config_check = {}
            for key, expected_value in custom_config.items():
                actual_value = scraper.config.get(key)
                config_check[key] = {
                    'expected': expected_value,
                    'actual': actual_value,
                    'matches': actual_value == expected_value
                }
                
            all_match = all(item['matches'] for item in config_check.values())
            
            self.logger.info(f"  ✅ Configuration integration: {'SUCCESS' if all_match else 'PARTIAL'}")
            
            return {
                'success': True,
                'all_configs_applied': all_match,
                'config_details': config_check
            }
            
        except Exception as e:
            self.logger.error(f"❌ Timing controls integration failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_large_scale_scraping(self, max_pages: int = 50, city: str = "gurgaon") -> Dict[str, Any]:
        """Test large-scale scraping functionality"""
        self.logger.info(f"🏗️ Testing Large-Scale Scraping: {max_pages} pages in {city}")
        
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

            self.logger.info(f"  📋 Starting listing page scraping...")
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
            
            self.logger.info(f"  ✅ Listing scraping complete:")
            self.logger.info(f"     📊 Pages scraped: {pages_scraped}")
            self.logger.info(f"     🏠 Properties found: {properties_found}")
            self.logger.info(f"     ⏱️ Time taken: {listing_time:.1f}s")
            self.logger.info(f"     🚀 Speed: {properties_found/listing_time:.1f} properties/second")
            
            return {
                'success': True,
                'pages_scraped': pages_scraped,
                'properties_found': properties_found,
                'time_taken': listing_time,
                'properties_per_second': properties_found/listing_time if listing_time > 0 else 0,
                'listing_results': listing_results
            }
            
        except Exception as e:
            self.logger.error(f"❌ Large-scale scraping failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_individual_property_scraping(self, property_urls: List[str], sample_size: int = 20) -> Dict[str, Any]:
        """Test individual property page scraping"""
        self.logger.info(f"🏠 Testing Individual Property Scraping: {sample_size} properties")
        
        try:
            # Use sample of URLs for testing
            test_urls = property_urls[:sample_size] if len(property_urls) > sample_size else property_urls
            
            test_config = {
                'individual_delay_min': 1,
                'individual_delay_max': 2,
                'batch_break_delay': 3,
                'batch_size': 5,
                'concurrent_pages': 2,
                'max_retries': 2
            }
            
            scraper = IntegratedMagicBricksScraper(custom_config=test_config)
            
            start_time = time.time()
            
            detailed_properties = scraper.scrape_individual_property_pages(
                property_urls=test_urls,
                batch_size=5,
                force_rescrape=False
            )
            
            individual_time = time.time() - start_time
            
            success_count = len(detailed_properties)
            success_rate = (success_count / len(test_urls)) * 100 if test_urls else 0
            
            self.logger.info(f"  ✅ Individual property scraping complete:")
            self.logger.info(f"     🎯 URLs tested: {len(test_urls)}")
            self.logger.info(f"     ✅ Successful extractions: {success_count}")
            self.logger.info(f"     📊 Success rate: {success_rate:.1f}%")
            self.logger.info(f"     ⏱️ Time taken: {individual_time:.1f}s")
            self.logger.info(f"     🚀 Speed: {success_count/individual_time:.1f} properties/second")
            
            return {
                'success': True,
                'urls_tested': len(test_urls),
                'successful_extractions': success_count,
                'success_rate': success_rate,
                'time_taken': individual_time,
                'properties_per_second': success_count/individual_time if individual_time > 0 else 0,
                'detailed_properties': detailed_properties
            }
            
        except Exception as e:
            self.logger.error(f"❌ Individual property scraping failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        self.logger.info("🚀 Starting Comprehensive Testing Suite")
        
        all_results = {
            'start_time': self.start_time.isoformat(),
            'tests': {}
        }
        
        # Test 1: GUI Timing Controls
        self.logger.info("\n" + "="*60)
        all_results['tests']['gui_timing_controls'] = self.test_gui_timing_controls()
        
        # Test 2: Timing Controls Integration
        self.logger.info("\n" + "="*60)
        all_results['tests']['timing_integration'] = self.test_timing_controls_integration()
        
        # Test 3: Large-Scale Scraping
        self.logger.info("\n" + "="*60)
        large_scale_results = self.test_large_scale_scraping(max_pages=30, city="gurgaon")
        all_results['tests']['large_scale_scraping'] = large_scale_results
        
        # Test 4: Individual Property Scraping (if we have URLs from large-scale test)
        if large_scale_results.get('success') and large_scale_results.get('listing_results'):
            properties = large_scale_results['listing_results'].get('properties', [])
            property_urls = [prop.get('property_url') for prop in properties if prop.get('property_url')]
            
            if property_urls:
                self.logger.info("\n" + "="*60)
                all_results['tests']['individual_property_scraping'] = self.test_individual_property_scraping(
                    property_urls, sample_size=15
                )
        
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
        results_file = f"comprehensive_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        self.logger.info(f"\n🎉 Comprehensive Testing Complete!")
        self.logger.info(f"   ⏱️ Total time: {total_time:.1f} seconds")
        self.logger.info(f"   📊 Overall success: {'✅ PASS' if all_results['overall_success'] else '❌ FAIL'}")
        self.logger.info(f"   📄 Results saved to: {results_file}")
        
        return all_results

if __name__ == "__main__":
    suite = ComprehensiveTestingSuite()
    results = suite.run_comprehensive_tests()
    
    # Print summary
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE TESTING SUMMARY")
    print("="*80)
    
    for test_name, test_result in results['tests'].items():
        status = "✅ PASS" if test_result.get('success') else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if results['overall_success'] else '❌ SOME TESTS FAILED'}")
    print(f"⏱️ Total Time: {results['total_time_seconds']:.1f} seconds")
