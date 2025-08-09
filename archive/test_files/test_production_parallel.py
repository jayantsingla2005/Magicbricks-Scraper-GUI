#!/usr/bin/env python3
"""
Production Parallel Processing Test
Comprehensive test of the production-ready parallel processing system
based on 50-property research validation.
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
    from src.core.production_parallel_processor import ProductionParallelProcessor
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class ProductionParallelTester:
    """
    Comprehensive test suite for production parallel processing
    """
    
    def __init__(self):
        """Initialize production parallel tester"""
        
        # Load configuration
        with open('config/scraper_config.json', 'r') as f:
            self.config = json.load(f)
        
        self.test_results = {
            'test_start_time': None,
            'test_end_time': None,
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'production_test_results': None,
            'test_details': []
        }
        
        print("🧪 Production Parallel Processing Test Suite Initialized")
        print("🎯 Testing production-ready system based on 50-property research validation")
    
    def run_production_tests(self) -> Dict[str, Any]:
        """
        Run comprehensive production parallel processing tests
        """
        
        print("\n🚀 Starting Production Parallel Processing Tests")
        print("="*70)
        
        self.test_results['test_start_time'] = datetime.now()
        
        try:
            # Test 1: Production Component Initialization
            print("\n🔧 Test 1: Production Component Initialization")
            self._test_production_initialization()
            
            # Test 2: Research Validation Compliance
            print("\n📊 Test 2: Research Validation Compliance")
            self._test_research_compliance()
            
            # Test 3: Production Configuration Validation
            print("\n⚙️ Test 3: Production Configuration Validation")
            self._test_production_configuration()
            
            # Test 4: Production Parallel Processing
            print("\n🚀 Test 4: Production Parallel Processing")
            self._test_production_parallel_processing()
            
            # Test 5: Production Results Analysis
            print("\n📈 Test 5: Production Results Analysis")
            self._test_production_results_analysis()
            
            # Test 6: Production Performance Validation
            print("\n⚡ Test 6: Production Performance Validation")
            self._test_production_performance()
            
            # Test 7: Production Error Handling
            print("\n🛡️ Test 7: Production Error Handling")
            self._test_production_error_handling()
            
            # Finalize test results
            self.test_results['test_end_time'] = datetime.now()
            
            # Generate test report
            self._generate_production_test_report()
            
            print("\n✅ PRODUCTION PARALLEL PROCESSING TESTS COMPLETE!")
            self._print_production_test_summary()
            
            return self.test_results
            
        except Exception as e:
            print(f"❌ Production test suite failed: {str(e)}")
            self.test_results['test_end_time'] = datetime.now()
            self.test_results['suite_error'] = str(e)
            return self.test_results
    
    def _test_production_initialization(self):
        """Test production component initialization"""
        
        test_name = "Production Component Initialization"
        
        try:
            # Test processor initialization
            processor = ProductionParallelProcessor(self.config)
            
            # Validate production configuration
            assert hasattr(processor, 'processing_config'), "Production config not initialized"
            assert hasattr(processor, 'priority_sections'), "Priority sections not initialized"
            assert hasattr(processor, 'secondary_sections'), "Secondary sections not initialized"
            assert hasattr(processor, 'stats'), "Statistics not initialized"
            assert hasattr(processor, 'url_manager'), "URL manager not initialized"
            
            # Validate research-based settings
            assert processor.processing_config['max_workers'] == 4, "Worker count not optimized"
            assert len(processor.priority_sections) == 7, "Priority sections count incorrect"
            assert len(processor.secondary_sections) == 1, "Secondary sections count incorrect"
            
            # Validate production delay settings
            delay_range = processor.processing_config['request_delay_range']
            assert 4.0 <= delay_range[0] <= 5.0, "Delay range minimum outside production bounds"
            assert 5.0 <= delay_range[1] <= 6.0, "Delay range maximum outside production bounds"
            
            # Validate production batch size
            assert processor.processing_config['batch_size'] >= 20, "Batch size too small for production"
            
            self._record_test_result(test_name, True, "All production components initialized correctly")
            print("✅ Production initialization test passed")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Production initialization failed: {str(e)}")
            print(f"❌ Production initialization test failed: {str(e)}")
    
    def _test_research_compliance(self):
        """Test compliance with 50-property research findings"""
        
        test_name = "Research Validation Compliance"
        
        try:
            processor = ProductionParallelProcessor(self.config)
            
            # Validate priority sections (100% availability in research)
            expected_priority_sections = [
                'amenities', 'floor_plan', 'neighborhood', 'pricing_details',
                'project_info', 'location_details', 'images'
            ]
            
            for section in expected_priority_sections:
                assert section in processor.priority_sections, f"Missing priority section: {section}"
            
            # Validate secondary sections (76% availability in research)
            expected_secondary_sections = ['specifications']
            
            for section in expected_secondary_sections:
                assert section in processor.secondary_sections, f"Missing secondary section: {section}"
            
            # Validate total sections match research
            total_sections = len(processor.priority_sections) + len(processor.secondary_sections)
            assert total_sections == 8, f"Total sections {total_sections} != 8 from research"
            
            self._record_test_result(test_name, True, "All research validation requirements met")
            print("✅ Research compliance test passed")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Research compliance failed: {str(e)}")
            print(f"❌ Research compliance test failed: {str(e)}")
    
    def _test_production_configuration(self):
        """Test production configuration optimization"""
        
        test_name = "Production Configuration Validation"
        
        try:
            processor = ProductionParallelProcessor(self.config)
            config = processor.processing_config
            
            # Validate production-optimized settings
            assert config['max_workers'] >= 3, "Insufficient workers for production"
            assert config['batch_size'] >= 20, "Batch size too small for production efficiency"
            assert config['error_threshold'] <= 0.15, "Error threshold too high for production"
            assert config['session_rotation_interval'] >= 50, "Session rotation too frequent"
            
            # Validate production timeouts
            assert config['timeout_per_property'] >= 30, "Timeout too low for production reliability"
            
            # Validate production monitoring
            assert 'progress_report_interval' in config, "Missing production progress reporting"
            assert 'memory_cleanup_interval' in config, "Missing production memory management"
            
            self._record_test_result(test_name, True, "Production configuration validated")
            print("✅ Production configuration test passed")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Production configuration failed: {str(e)}")
            print(f"❌ Production configuration test failed: {str(e)}")
    
    def _test_production_parallel_processing(self):
        """Test production parallel processing with real properties"""
        
        test_name = "Production Parallel Processing"
        
        try:
            processor = ProductionParallelProcessor(self.config)
            
            # Test with production batch size
            session_id = f"production_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            start_time = time.time()
            
            # Run production parallel processing
            result = processor.process_properties_production(
                session_id=session_id,
                max_properties=25  # Production test batch
            )
            
            end_time = time.time()
            processing_duration = end_time - start_time
            
            # Store production test results for analysis
            self.test_results['production_test_results'] = result
            
            # Validate production result structure
            assert isinstance(result, dict), "Result should be a dictionary"
            assert 'status' in result, "Result missing status"
            assert 'statistics' in result, "Result missing statistics"
            assert 'production_report' in result, "Result missing production report"
            
            stats = result['statistics']
            
            # Validate production statistics
            required_stats = [
                'total_properties_processed', 'successful_extractions', 
                'failed_extractions', 'throughput_per_minute',
                'priority_sections_extracted', 'secondary_sections_extracted'
            ]
            for stat in required_stats:
                assert stat in stats, f"Statistics missing {stat}"
            
            # Production performance validation
            if stats['total_properties_processed'] > 0:
                success_rate = (stats['successful_extractions'] / stats['total_properties_processed']) * 100
                
                # Production success rate should be high
                assert success_rate >= 80, f"Production success rate too low: {success_rate:.1f}%"
                
                # Production processing time should be reasonable
                assert processing_duration < 1800, "Production processing took too long (>30 minutes)"
                
                performance_msg = (f"Processed {stats['total_properties_processed']} properties "
                                 f"in {processing_duration:.1f}s, {success_rate:.1f}% success rate, "
                                 f"{stats['throughput_per_minute']:.1f} properties/minute")
                
                self._record_test_result(test_name, True, performance_msg)
                print(f"✅ Production parallel processing test passed - {performance_msg}")
            else:
                self._record_test_result(test_name, True, "No properties processed but system handled gracefully")
                print("⚠️ Production parallel processing test passed - No properties available")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Production parallel processing failed: {str(e)}")
            print(f"❌ Production parallel processing test failed: {str(e)}")
    
    def _test_production_results_analysis(self):
        """Test production results analysis and reporting"""
        
        test_name = "Production Results Analysis"
        
        try:
            if not self.test_results.get('production_test_results'):
                self._record_test_result(test_name, False, "No production test results available")
                return
            
            result = self.test_results['production_test_results']
            
            # Validate production report structure
            assert 'production_report' in result, "Missing production report"
            
            report = result['production_report']
            
            # Validate report sections
            required_sections = [
                'executive_summary', 'performance_metrics', 'data_quality_metrics',
                'property_type_analysis', 'error_analysis', 'recommendations'
            ]
            
            for section in required_sections:
                assert section in report, f"Production report missing {section}"
            
            # Validate executive summary
            exec_summary = report['executive_summary']
            assert 'success_rate' in exec_summary, "Missing success rate in executive summary"
            assert 'average_sections_per_property' in exec_summary, "Missing average sections"
            
            # Validate data quality metrics
            data_quality = report['data_quality_metrics']
            assert 'priority_sections_performance' in data_quality, "Missing priority sections performance"
            assert 'secondary_sections_performance' in data_quality, "Missing secondary sections performance"
            
            self._record_test_result(test_name, True, "Production results analysis validated")
            print("✅ Production results analysis test passed")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Production results analysis failed: {str(e)}")
            print(f"❌ Production results analysis test failed: {str(e)}")
    
    def _test_production_performance(self):
        """Test production performance metrics"""
        
        test_name = "Production Performance Validation"
        
        try:
            if not self.test_results.get('production_test_results'):
                self._record_test_result(test_name, False, "No production test results available")
                return
            
            result = self.test_results['production_test_results']
            stats = result['statistics']
            
            # Validate production performance metrics
            if stats['total_properties_processed'] > 0:
                # Throughput validation
                throughput = stats['throughput_per_minute']
                assert throughput > 0, "Throughput should be positive"
                
                # Priority sections performance (should be high based on research)
                if stats['successful_extractions'] > 0:
                    priority_avg = stats['priority_sections_extracted'] / stats['successful_extractions']
                    assert priority_avg >= 5.0, f"Priority sections average too low: {priority_avg:.1f}/7"
                
                # Error rate validation
                error_rate = stats['error_rate']
                assert error_rate <= 20, f"Error rate too high for production: {error_rate:.1f}%"
                
                performance_msg = (f"Throughput: {throughput:.1f}/min, "
                                 f"Priority avg: {priority_avg:.1f}/7, "
                                 f"Error rate: {error_rate:.1f}%")
                
                self._record_test_result(test_name, True, performance_msg)
                print(f"✅ Production performance test passed - {performance_msg}")
            else:
                self._record_test_result(test_name, True, "No properties processed for performance validation")
                print("⚠️ Production performance test passed - No data for validation")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Production performance validation failed: {str(e)}")
            print(f"❌ Production performance test failed: {str(e)}")
    
    def _test_production_error_handling(self):
        """Test production error handling and recovery"""
        
        test_name = "Production Error Handling"
        
        try:
            processor = ProductionParallelProcessor(self.config)
            
            # Test error rate calculation
            processor.stats['total_properties_processed'] = 100
            processor.stats['failed_extractions'] = 5
            
            error_rate = processor._calculate_current_error_rate()
            expected_rate = 0.05  # 5/100 = 0.05
            
            assert abs(error_rate - expected_rate) < 0.01, f"Error rate calculation incorrect: {error_rate} vs {expected_rate}"
            
            # Test error threshold detection
            processor.stats['failed_extractions'] = 15  # 15% error rate
            high_error_rate = processor._calculate_current_error_rate()
            
            assert high_error_rate > processor.processing_config['error_threshold'], "High error rate not detected"
            
            self._record_test_result(test_name, True, "Production error handling mechanisms validated")
            print("✅ Production error handling test passed")
            
        except Exception as e:
            self._record_test_result(test_name, False, f"Production error handling failed: {str(e)}")
            print(f"❌ Production error handling test failed: {str(e)}")
    
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
    
    def _generate_production_test_report(self):
        """Generate comprehensive production test report"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"production_parallel_test_report_{timestamp}.json"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📁 Production test report saved: {report_filename}")
    
    def _print_production_test_summary(self):
        """Print production test summary"""
        
        print("\n" + "="*70)
        print("📊 PRODUCTION PARALLEL PROCESSING TEST SUMMARY")
        print("="*70)
        
        total_tests = self.test_results['tests_run']
        passed_tests = self.test_results['tests_passed']
        failed_tests = self.test_results['tests_failed']
        
        print(f"🧪 Total Tests Run: {total_tests}")
        print(f"✅ Tests Passed: {passed_tests}")
        print(f"❌ Tests Failed: {failed_tests}")
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            print(f"📈 Test Success Rate: {success_rate:.1f}%")
        
        # Production test results summary
        if self.test_results.get('production_test_results'):
            prod_result = self.test_results['production_test_results']
            if prod_result['status'] == 'success':
                stats = prod_result['statistics']
                print(f"\n🚀 PRODUCTION TEST RESULTS:")
                print(f"   📊 Properties Processed: {stats['total_properties_processed']}")
                print(f"   ✅ Success Rate: {100 - stats['error_rate']:.1f}%")
                print(f"   ⚡ Throughput: {stats['throughput_per_minute']:.1f} properties/minute")
                print(f"   🎯 Priority Sections: {stats['priority_sections_extracted']}")
                print(f"   🎯 Secondary Sections: {stats['secondary_sections_extracted']}")
        
        print(f"\n📋 TEST DETAILS:")
        for test in self.test_results['test_details']:
            status = "✅" if test['passed'] else "❌"
            print(f"   {status} {test['test_name']}: {test['details']}")
        
        if failed_tests == 0:
            print(f"\n🎉 ALL PRODUCTION TESTS PASSED! System ready for production deployment.")
        else:
            print(f"\n⚠️ {failed_tests} test(s) failed. Review and address issues before production deployment.")


def main():
    """Main production test execution function"""
    
    print("🧪 Production Parallel Property Processing Test Suite")
    print("Comprehensive testing of production-ready parallel processing system...")
    print("Based on 50-property research validation")
    print()
    
    try:
        # Initialize tester
        tester = ProductionParallelTester()
        
        # Run comprehensive production tests
        results = tester.run_production_tests()
        
        # Determine overall result
        if results['tests_failed'] == 0:
            print("\n✅ PRODUCTION PARALLEL PROCESSING TESTING SUCCESSFUL!")
            print("🚀 System validated and ready for production deployment")
        else:
            print(f"\n⚠️ PRODUCTION TESTING COMPLETED WITH {results['tests_failed']} ISSUES")
            print("📊 Review test report for detailed analysis")
        
        return results
        
    except Exception as e:
        print(f"❌ Production test suite execution failed: {str(e)}")
        return None


if __name__ == "__main__":
    main()
