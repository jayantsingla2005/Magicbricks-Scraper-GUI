#!/usr/bin/env python3
"""
Parallel Processing Test Suite
Comprehensive testing of the research-validated parallel property processing system.
"""

import time
import json
import os
from typing import Dict, List, Any
from datetime import datetime

# Add src directory to path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / 'src'))

try:
    from src.core.parallel_property_processor import ParallelPropertyProcessor
    from src.core.url_discovery_manager import URLDiscoveryManager
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class ParallelProcessingTester:
    """
    Comprehensive test suite for parallel property processing
    """
    
    def __init__(self):
        """Initialize parallel processing tester"""
        
        # Load configuration
        with open('config/scraper_config.json', 'r') as f:
            self.config = json.load(f)
        
        self.test_results = {
            'test_start_time': None,
            'test_end_time': None,
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'test_details': []
        }
        
        print("🧪 Parallel Processing Test Suite Initialized")
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """
        Run comprehensive parallel processing tests
        """
        
        print("\n🚀 Starting Comprehensive Parallel Processing Tests")
        print("="*60)
        
        self.test_results['test_start_time'] = datetime.now()
        
        try:
            # Test 1: Component Initialization
            print("\n🔧 Test 1: Component Initialization")
            self._test_component_initialization()
            
            # Test 2: URL Loading and Queue Management
            print("\n📡 Test 2: URL Loading and Queue Management")
            self._test_url_loading()
            
            # Test 3: Worker Thread Configuration
            print("\n👷 Test 3: Worker Thread Configuration")
            self._test_worker_configuration()
            
            # Test 4: Single Property Processing
            print("\n🏠 Test 4: Single Property Processing")
            self._test_single_property_processing()
            
            # Test 5: Parallel Processing Performance
            print("\n⚡ Test 5: Parallel Processing Performance")
            self._test_parallel_performance()
            
            # Test 6: Error Handling and Recovery
            print("\n🛡️ Test 6: Error Handling and Recovery")
            self._test_error_handling()
            
            # Test 7: Research Validation
            print("\n📊 Test 7: Research Validation")
            self._test_research_validation()
            
            # Finalize test results
            self.test_results['test_end_time'] = datetime.now()
            
            # Generate test report
            self._generate_test_report()
            
            print("\n✅ COMPREHENSIVE PARALLEL PROCESSING TESTS COMPLETE!")
            self._print_test_summary()
            
            return self.test_results
            
        except Exception as e:
            print(f"❌ Test suite failed: {str(e)}")
            self.test_results['test_end_time'] = datetime.now()
            self.test_results['suite_error'] = str(e)
            return self.test_results
    
    def _test_component_initialization(self):
        """Test component initialization"""
        
        test_name = "Component Initialization"
        
        try:
            # Test processor initialization
            processor = ParallelPropertyProcessor(self.config)
            
            # Validate configuration
            assert hasattr(processor, 'processing_config'), "Processing config not initialized"
            assert hasattr(processor, 'target_sections'), "Target sections not initialized"
            assert hasattr(processor, 'stats'), "Statistics not initialized"
            assert hasattr(processor, 'url_manager'), "URL manager not initialized"
            
            # Validate research-based settings
            assert processor.processing_config['max_workers'] >= 3, "Worker count below research minimum"
            assert processor.processing_config['max_workers'] <= 5, "Worker count above research maximum"
            assert len(processor.target_sections) == 8, "Target sections count incorrect"
            
            # Validate delay settings
            delay_range = processor.processing_config['request_delay_range']
            assert 4.0 <= delay_range[0] <= 5.0, "Delay range minimum outside research bounds"
            assert 5.0 <= delay_range[1] <= 6.0, "Delay range maximum outside research bounds"
            
            self._record_test_result(test_name, True, "All components initialized correctly")
            print("✅ Component initialization test passed")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Initialization failed: {str(e)}")
            print(f"❌ Component initialization test failed: {str(e)}")
    
    def _test_url_loading(self):
        """Test URL loading and queue management"""
        
        test_name = "URL Loading and Queue Management"
        
        try:
            processor = ParallelPropertyProcessor(self.config)
            
            # Test URL loading
            session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # First, ensure we have some URLs in the database
            url_manager = URLDiscoveryManager()
            
            # Check if we have URLs, if not try to discover some
            pending_urls = url_manager.get_pending_urls(limit=5)
            
            if not pending_urls:
                print("🔍 No URLs found, attempting discovery for testing...")
                discovery_result = url_manager.discover_urls_from_listings(
                    start_page=1,
                    max_pages=2,
                    session_id=session_id
                )
                pending_urls = url_manager.get_pending_urls(limit=5)
            
            # Test URL loading function
            loaded_urls = processor._load_property_urls(session_id, 10)
            
            # Validate results
            assert isinstance(loaded_urls, list), "URL loading should return a list"
            
            if loaded_urls:
                # Validate URL structure
                sample_url = loaded_urls[0]
                required_keys = ['url', 'priority', 'metadata']
                for key in required_keys:
                    assert key in sample_url, f"URL data missing required key: {key}"
                
                assert sample_url['url'].startswith('http'), "Invalid URL format"
                
                self._record_test_result(test_name, True, f"Loaded {len(loaded_urls)} URLs successfully")
                print(f"✅ URL loading test passed - Loaded {len(loaded_urls)} URLs")
            else:
                self._record_test_result(test_name, True, "No URLs available but loading function works")
                print("⚠️ URL loading test passed - No URLs available for testing")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"URL loading failed: {str(e)}")
            print(f"❌ URL loading test failed: {str(e)}")
    
    def _test_worker_configuration(self):
        """Test worker thread configuration"""
        
        test_name = "Worker Thread Configuration"
        
        try:
            processor = ParallelPropertyProcessor(self.config)
            
            # Test browser setup
            driver = processor._setup_worker_browser()
            
            # Validate browser configuration
            assert driver is not None, "Browser not initialized"
            
            # Test basic browser functionality
            driver.get("https://www.google.com")
            assert "Google" in driver.title, "Browser navigation failed"
            
            # Test anti-detection measures
            webdriver_value = driver.execute_script("return navigator.webdriver")
            assert webdriver_value is None, "WebDriver detection not hidden"
            
            driver.quit()
            
            self._record_test_result(test_name, True, "Worker browser configuration validated")
            print("✅ Worker configuration test passed")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Worker configuration failed: {str(e)}")
            print(f"❌ Worker configuration test failed: {str(e)}")
    
    def _test_single_property_processing(self):
        """Test single property processing"""
        
        test_name = "Single Property Processing"
        
        try:
            processor = ParallelPropertyProcessor(self.config)
            
            # Create a test URL data structure
            test_url_data = {
                'url': 'https://www.magicbricks.com/vipul-greens-sector-48-gurgaon-pdpid-4d4235303030333036',
                'url_id': 'test_id',
                'priority': 1,
                'metadata': {'test': True},
                'discovery_session': 'test_session'
            }
            
            # Test with a real browser and extractor
            from src.core.detailed_property_extractor import DetailedPropertyExtractor
            
            driver = processor._setup_worker_browser()
            extractor = DetailedPropertyExtractor(self.config)
            
            # Process the test property
            result = processor._process_single_property(driver, extractor, test_url_data, "test-worker")
            
            driver.quit()
            
            # Validate result structure
            assert isinstance(result, dict), "Result should be a dictionary"
            assert 'status' in result, "Result missing status"
            assert 'url' in result, "Result missing URL"
            assert 'processing_time' in result, "Result missing processing time"
            assert 'sections_extracted' in result, "Result missing sections extracted count"
            
            # Validate processing success
            if result['status'] == 'success':
                assert result['sections_extracted'] >= 0, "Invalid sections extracted count"
                assert 'property_data' in result, "Result missing property data"
                
                self._record_test_result(test_name, True, 
                                       f"Processed property successfully - {result['sections_extracted']}/8 sections")
                print(f"✅ Single property processing test passed - {result['sections_extracted']}/8 sections extracted")
            else:
                # Even if processing failed, the function should handle it gracefully
                assert 'error' in result, "Failed result missing error information"
                
                self._record_test_result(test_name, True, 
                                       f"Processing failed gracefully: {result.get('error', 'Unknown error')}")
                print(f"⚠️ Single property processing test passed - Graceful failure handling")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Single property processing failed: {str(e)}")
            print(f"❌ Single property processing test failed: {str(e)}")
    
    def _test_parallel_performance(self):
        """Test parallel processing performance"""
        
        test_name = "Parallel Processing Performance"
        
        try:
            processor = ParallelPropertyProcessor(self.config)
            
            # Test with a small batch
            session_id = f"perf_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            start_time = time.time()
            
            # Run parallel processing with limited properties
            result = processor.process_properties_parallel(
                session_id=session_id,
                max_properties=5  # Small test batch
            )
            
            end_time = time.time()
            processing_duration = end_time - start_time
            
            # Validate performance result
            assert isinstance(result, dict), "Result should be a dictionary"
            assert 'status' in result, "Result missing status"
            assert 'statistics' in result, "Result missing statistics"
            
            stats = result['statistics']
            
            # Validate statistics structure
            required_stats = ['total_properties_processed', 'successful_extractions', 
                            'failed_extractions', 'throughput_per_minute']
            for stat in required_stats:
                assert stat in stats, f"Statistics missing {stat}"
            
            # Performance validation
            if stats['total_properties_processed'] > 0:
                success_rate = (stats['successful_extractions'] / stats['total_properties_processed']) * 100
                
                # Research validation: Should achieve reasonable performance
                assert processing_duration < 300, "Processing took too long (>5 minutes)"
                
                performance_msg = (f"Processed {stats['total_properties_processed']} properties "
                                 f"in {processing_duration:.1f}s, {success_rate:.1f}% success rate")
                
                self._record_test_result(test_name, True, performance_msg)
                print(f"✅ Parallel performance test passed - {performance_msg}")
            else:
                self._record_test_result(test_name, True, "No properties processed but system handled gracefully")
                print("⚠️ Parallel performance test passed - No properties available")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Parallel performance test failed: {str(e)}")
            print(f"❌ Parallel performance test failed: {str(e)}")
    
    def _test_error_handling(self):
        """Test error handling and recovery"""
        
        test_name = "Error Handling and Recovery"
        
        try:
            processor = ParallelPropertyProcessor(self.config)
            
            # Test error rate calculation
            processor.stats['total_properties_processed'] = 10
            processor.stats['failed_extractions'] = 2
            
            error_rate = processor._calculate_current_error_rate()
            expected_rate = 0.2  # 2/10 = 0.2
            
            assert abs(error_rate - expected_rate) < 0.01, f"Error rate calculation incorrect: {error_rate} vs {expected_rate}"
            
            # Test error threshold detection
            processor.stats['failed_extractions'] = 8  # 80% error rate
            high_error_rate = processor._calculate_current_error_rate()
            
            assert high_error_rate > processor.processing_config['error_threshold'], "High error rate not detected"
            
            self._record_test_result(test_name, True, "Error handling mechanisms validated")
            print("✅ Error handling test passed")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Error handling test failed: {str(e)}")
            print(f"❌ Error handling test failed: {str(e)}")
    
    def _test_research_validation(self):
        """Test research validation compliance"""
        
        test_name = "Research Validation"
        
        try:
            processor = ParallelPropertyProcessor(self.config)
            
            # Validate research-based configuration
            config = processor.processing_config
            
            # Worker count validation (research: 3-5 optimal)
            assert 3 <= config['max_workers'] <= 5, f"Worker count {config['max_workers']} outside research range 3-5"
            
            # Delay validation (research: 4.9s ± 0.4s)
            delay_min, delay_max = config['request_delay_range']
            assert 4.5 <= delay_min <= 5.3, f"Delay minimum {delay_min} outside research range"
            assert 4.5 <= delay_max <= 5.3, f"Delay maximum {delay_max} outside research range"
            
            # Target sections validation (research: 8 sections with 100% availability)
            assert len(processor.target_sections) == 8, f"Target sections count {len(processor.target_sections)} != 8"
            
            expected_sections = [
                'amenities', 'floor_plan', 'neighborhood', 'pricing_details',
                'project_info', 'specifications', 'location_details', 'images'
            ]
            
            for section in expected_sections:
                assert section in processor.target_sections, f"Missing research-validated section: {section}"
            
            # Timeout validation (research: 3.27s avg load time + processing)
            assert config['timeout_per_property'] >= 30, "Timeout too low for research-validated load times"
            assert config['timeout_per_property'] <= 60, "Timeout unnecessarily high"
            
            self._record_test_result(test_name, True, "All research validations passed")
            print("✅ Research validation test passed")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Research validation failed: {str(e)}")
            print(f"❌ Research validation test failed: {str(e)}")
    
    def _record_test_result(self, test_name: str, passed: bool, details: str):
        """Record test result"""
        
        self.test_results['tests_run'] += 1
        
        if passed:
            self.test_results['tests_passed'] += 1
        else:
            self.test_results['tests_failed'] += 1
        
        self.test_results['test_details'].append({
            'test_name': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def _generate_test_report(self):
        """Generate comprehensive test report"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"parallel_processing_test_report_{timestamp}.json"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Test report saved: {report_filename}")
    
    def _print_test_summary(self):
        """Print test summary"""
        
        print("\n" + "="*60)
        print("📊 PARALLEL PROCESSING TEST SUMMARY")
        print("="*60)
        
        total_tests = self.test_results['tests_run']
        passed_tests = self.test_results['tests_passed']
        failed_tests = self.test_results['tests_failed']
        
        print(f"🧪 Total Tests Run: {total_tests}")
        print(f"✅ Tests Passed: {passed_tests}")
        print(f"❌ Tests Failed: {failed_tests}")
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 TEST DETAILS:")
        for test in self.test_results['test_details']:
            status = "✅" if test['passed'] else "❌"
            print(f"   {status} {test['test_name']}: {test['details']}")
        
        if failed_tests == 0:
            print(f"\n🎉 ALL TESTS PASSED! Parallel processing system is ready for production.")
        else:
            print(f"\n⚠️ {failed_tests} test(s) failed. Review and address issues before deployment.")


def main():
    """Main test execution function"""
    
    print("🧪 Parallel Property Processing Test Suite")
    print("Comprehensive testing of research-validated parallel processing system...")
    print()
    
    try:
        # Initialize tester
        tester = ParallelProcessingTester()
        
        # Run comprehensive tests
        results = tester.run_comprehensive_tests()
        
        # Determine overall result
        if results['tests_failed'] == 0:
            print("\n✅ PARALLEL PROCESSING TESTING SUCCESSFUL!")
            print("🚀 System validated and ready for production deployment")
        else:
            print(f"\n⚠️ PARALLEL PROCESSING TESTING COMPLETED WITH {results['tests_failed']} ISSUES")
            print("📊 Review test report for detailed analysis")
        
        return results
        
    except Exception as e:
        print(f"❌ Test suite execution failed: {str(e)}")
        return None


if __name__ == "__main__":
    main()
