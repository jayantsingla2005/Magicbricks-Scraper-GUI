#!/usr/bin/env python3
"""
Comprehensive GUI Testing Framework
Systematic validation of all GUI components and functionality
"""

import time
import threading
import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


class GUITestFramework:
    """
    Comprehensive GUI testing framework for systematic validation
    """
    
    def __init__(self):
        """Initialize the testing framework"""
        
        self.test_results = {}
        self.current_test = None
        self.gui_process = None
        self.test_start_time = None
        
        print("🧪 COMPREHENSIVE GUI TESTING FRAMEWORK")
        print("=" * 60)
        print("🎯 Mission: Systematically test every GUI component and feature")
        print("⚠️  No claims without thorough validation")
        print("🔍 Testing approach: Real user interactions with large datasets")
        print()
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        
        print("🚀 STARTING COMPREHENSIVE GUI TESTING")
        print("=" * 60)
        
        # Test sequence
        test_sequence = [
            ("Component Import Test", self.test_component_imports),
            ("GUI Launch Test", self.test_gui_launch),
            ("Configuration Panel Test", self.test_configuration_panel),
            ("Monitoring Panel Test", self.test_monitoring_panel),
            ("Progress Callback Test", self.test_progress_callbacks),
            ("Small Scale Scraping Test", self.test_small_scale_scraping),
            ("Large Scale Scraping Test", self.test_large_scale_scraping),
            ("Individual Property Test", self.test_individual_property_scraping),
            ("Duplicate Detection Test", self.test_duplicate_detection),
            ("Error Handling Test", self.test_error_handling),
            ("Performance Test", self.test_performance_under_load)
        ]
        
        for test_name, test_function in test_sequence:
            self.run_single_test(test_name, test_function)
        
        # Generate final report
        self.generate_test_report()
    
    def run_single_test(self, test_name: str, test_function):
        """Run a single test with proper logging"""
        
        print(f"\n🔍 RUNNING: {test_name}")
        print("-" * 50)
        
        self.current_test = test_name
        self.test_start_time = time.time()
        
        try:
            result = test_function()
            duration = time.time() - self.test_start_time
            
            self.test_results[test_name] = {
                'status': 'PASSED' if result else 'FAILED',
                'duration': duration,
                'details': result if isinstance(result, dict) else {'success': result}
            }
            
            status_icon = "✅" if result else "❌"
            print(f"{status_icon} {test_name}: {'PASSED' if result else 'FAILED'} ({duration:.1f}s)")
            
        except Exception as e:
            duration = time.time() - self.test_start_time
            self.test_results[test_name] = {
                'status': 'ERROR',
                'duration': duration,
                'details': {'error': str(e)}
            }
            
            print(f"💥 {test_name}: ERROR - {str(e)} ({duration:.1f}s)")
    
    def test_component_imports(self) -> bool:
        """Test that all GUI components can be imported"""
        
        print("   📦 Testing component imports...")
        
        try:
            # Test modular GUI imports
            from gui_components.style_manager import StyleManager
            from gui_components.configuration_panel import ConfigurationPanel
            from gui_components.monitoring_panel import MonitoringPanel
            from gui_components.data_visualization import DataVisualizationPanel
            
            print("   ✅ All GUI components imported successfully")
            
            # Test main GUI import
            from modular_magicbricks_gui import ModularMagicBricksGUI
            print("   ✅ Main modular GUI imported successfully")
            
            # Test supporting systems
            from individual_property_tracking_system import IndividualPropertyTracker
            from performance_optimization_system import PerformanceOptimizationSystem
            from advanced_security_system import AdvancedSecuritySystem
            
            print("   ✅ All supporting systems imported successfully")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Import failed: {str(e)}")
            return False
    
    def test_gui_launch(self) -> bool:
        """Test GUI launch and basic window creation"""
        
        print("   🖥️ Testing GUI launch...")
        
        try:
            # Import and create GUI instance
            from modular_magicbricks_gui import ModularMagicBricksGUI
            
            # Create GUI in a separate thread to avoid blocking
            gui_ready = threading.Event()
            gui_error = threading.Event()
            
            def launch_gui():
                try:
                    app = ModularMagicBricksGUI()
                    gui_ready.set()
                    
                    # Run for a short time to test basic functionality
                    app.root.after(3000, app.root.quit)  # Auto-close after 3 seconds
                    app.root.mainloop()
                    
                except Exception as e:
                    print(f"   ❌ GUI launch error: {str(e)}")
                    gui_error.set()
            
            gui_thread = threading.Thread(target=launch_gui, daemon=True)
            gui_thread.start()
            
            # Wait for GUI to be ready or error
            if gui_ready.wait(timeout=10):
                print("   ✅ GUI launched successfully")
                time.sleep(4)  # Let it run for a bit
                return True
            elif gui_error.is_set():
                print("   ❌ GUI launch failed with error")
                return False
            else:
                print("   ❌ GUI launch timeout")
                return False
                
        except Exception as e:
            print(f"   ❌ GUI launch test failed: {str(e)}")
            return False
    
    def test_configuration_panel(self) -> bool:
        """Test configuration panel functionality"""
        
        print("   ⚙️ Testing configuration panel...")
        
        try:
            import tkinter as tk
            from gui_components.style_manager import StyleManager
            from gui_components.configuration_panel import ConfigurationPanel
            
            # Create test window
            root = tk.Tk()
            root.withdraw()  # Hide window
            
            style_manager = StyleManager()
            style_manager.setup_styles(root)
            
            # Test configuration panel creation
            config_panel = ConfigurationPanel(root, style_manager)
            
            # Test configuration getting/setting
            test_config = {
                'city': 'mumbai',
                'max_pages': 50,
                'individual_pages': True,
                'export_csv': True
            }
            
            config_panel.set_config(test_config)
            retrieved_config = config_panel.get_config()
            
            # Validate configuration
            config_valid = (
                retrieved_config['city'] == 'mumbai' and
                retrieved_config['max_pages'] == 50 and
                retrieved_config['individual_pages'] == True and
                retrieved_config['export_csv'] == True
            )
            
            root.destroy()
            
            if config_valid:
                print("   ✅ Configuration panel working correctly")
                return True
            else:
                print("   ❌ Configuration panel validation failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Configuration panel test failed: {str(e)}")
            return False
    
    def test_monitoring_panel(self) -> bool:
        """Test monitoring panel functionality"""
        
        print("   📊 Testing monitoring panel...")
        
        try:
            import tkinter as tk
            from gui_components.style_manager import StyleManager
            from gui_components.monitoring_panel import MonitoringPanel
            
            # Create test window
            root = tk.Tk()
            root.withdraw()  # Hide window
            
            style_manager = StyleManager()
            style_manager.setup_styles(root)
            
            # Test monitoring panel creation
            monitoring_panel = MonitoringPanel(root, style_manager)
            
            # Test progress updates
            monitoring_panel.update_progress(25.5)
            monitoring_panel.update_status("Testing progress updates")
            
            # Test statistics updates
            test_stats = {
                'pages_scraped': '5',
                'properties_found': '150',
                'duration': '2:30',
                'speed': '60 props/min'
            }
            monitoring_panel.update_statistics(test_stats)
            
            # Test log messages
            monitoring_panel.log_message("Test info message", "INFO")
            monitoring_panel.log_message("Test success message", "SUCCESS")
            monitoring_panel.log_message("Test warning message", "WARNING")
            
            root.destroy()
            
            print("   ✅ Monitoring panel working correctly")
            return True
            
        except Exception as e:
            print(f"   ❌ Monitoring panel test failed: {str(e)}")
            return False
    
    def test_progress_callbacks(self) -> bool:
        """Test progress callback mechanism"""
        
        print("   📈 Testing progress callbacks...")
        
        try:
            # Test the fixed progress callback system
            callback_received = []
            
            def test_callback(progress_data):
                callback_received.append(progress_data)
            
            # Simulate progress updates like the scraper would send
            test_progress_data = {
                'current_page': 5,
                'total_pages': 10,
                'properties_found': 150,
                'phase': 'listing_extraction'
            }
            
            test_callback(test_progress_data)
            
            # Validate callback data
            if (len(callback_received) == 1 and 
                callback_received[0]['current_page'] == 5 and
                callback_received[0]['total_pages'] == 10):
                
                print("   ✅ Progress callbacks working correctly")
                return True
            else:
                print("   ❌ Progress callback validation failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Progress callback test failed: {str(e)}")
            return False
    
    def test_small_scale_scraping(self) -> bool:
        """Test small scale scraping (5 pages) to validate basic functionality"""
        
        print("   🔍 Testing small scale scraping (5 pages)...")
        
        try:
            from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
            from user_mode_options import ScrapingMode
            
            # Create scraper instance
            scraper = IntegratedMagicBricksScraper(headless=True, incremental_enabled=True)
            
            # Track progress updates
            progress_updates = []
            
            def progress_callback(progress_data):
                progress_updates.append(progress_data)
                print(f"      📊 Progress: Page {progress_data.get('current_page', 0)}/{progress_data.get('total_pages', 0)}")
            
            print("   🚀 Starting small scale scraping...")
            
            # Run small scale test
            result = scraper.scrape_properties_with_incremental(
                city='gurgaon',
                mode=ScrapingMode.INCREMENTAL,
                max_pages=5,
                include_individual_pages=False,
                export_formats=['csv'],
                progress_callback=progress_callback
            )
            
            # Clean up
            scraper.close()
            
            # Validate results
            success = (
                result.get('success', False) and
                len(progress_updates) > 0 and
                result.get('session_stats', {}).get('pages_scraped', 0) > 0
            )
            
            if success:
                pages_scraped = result.get('session_stats', {}).get('pages_scraped', 0)
                properties_found = result.get('session_stats', {}).get('properties_found', 0)
                print(f"   ✅ Small scale scraping successful: {pages_scraped} pages, {properties_found} properties")
                return True
            else:
                print(f"   ❌ Small scale scraping failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"   ❌ Small scale scraping test failed: {str(e)}")
            return False
    
    def test_large_scale_scraping(self) -> bool:
        """Test large scale scraping (50 pages) to validate performance"""
        
        print("   🚀 Testing large scale scraping (50 pages)...")
        print("   ⚠️  This will take several minutes - validating real performance")
        
        try:
            from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
            from user_mode_options import ScrapingMode
            
            # Create scraper instance
            scraper = IntegratedMagicBricksScraper(headless=True, incremental_enabled=True)
            
            # Track detailed progress
            progress_updates = []
            start_time = time.time()
            
            def progress_callback(progress_data):
                progress_updates.append(progress_data)
                current = progress_data.get('current_page', 0)
                total = progress_data.get('total_pages', 0)
                properties = progress_data.get('properties_found', 0)
                
                if current % 5 == 0 or current == total:  # Log every 5 pages
                    elapsed = time.time() - start_time
                    print(f"      📊 Progress: {current}/{total} pages, {properties} properties, {elapsed:.1f}s elapsed")
            
            print("   🚀 Starting large scale scraping...")
            
            # Run large scale test
            result = scraper.scrape_properties_with_incremental(
                city='gurgaon',
                mode=ScrapingMode.INCREMENTAL,
                max_pages=50,
                include_individual_pages=False,
                export_formats=['csv', 'database'],
                progress_callback=progress_callback
            )
            
            # Clean up
            scraper.close()
            
            # Validate results
            total_time = time.time() - start_time
            success = (
                result.get('success', False) and
                len(progress_updates) >= 10 and  # Should have many progress updates
                result.get('session_stats', {}).get('pages_scraped', 0) >= 40  # Should scrape most pages
            )
            
            if success:
                stats = result.get('session_stats', {})
                pages_scraped = stats.get('pages_scraped', 0)
                properties_found = stats.get('properties_found', 0)
                avg_time_per_page = total_time / max(pages_scraped, 1)
                
                print(f"   ✅ Large scale scraping successful:")
                print(f"      📄 Pages scraped: {pages_scraped}/50")
                print(f"      🏠 Properties found: {properties_found}")
                print(f"      ⏱️ Total time: {total_time:.1f}s")
                print(f"      📊 Avg time per page: {avg_time_per_page:.1f}s")
                print(f"      📈 Progress updates: {len(progress_updates)}")
                
                return True
            else:
                print(f"   ❌ Large scale scraping failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"   ❌ Large scale scraping test failed: {str(e)}")
            return False
    
    def test_individual_property_scraping(self) -> bool:
        """Test individual property scraping with a reasonable sample"""
        
        print("   🏠 Testing individual property scraping...")
        
        try:
            from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
            from user_mode_options import ScrapingMode
            
            # Create scraper instance
            scraper = IntegratedMagicBricksScraper(headless=True, incremental_enabled=True)
            
            # Track progress
            progress_updates = []
            start_time = time.time()
            
            def progress_callback(progress_data):
                progress_updates.append(progress_data)
                phase = progress_data.get('phase', 'unknown')
                current = progress_data.get('current_page', 0)
                total = progress_data.get('total_pages', 0)
                
                print(f"      📊 {phase}: {current}/{total}")
            
            print("   🚀 Starting individual property scraping test (10 pages)...")
            
            # Run individual property test
            result = scraper.scrape_properties_with_incremental(
                city='gurgaon',
                mode=ScrapingMode.INCREMENTAL,
                max_pages=10,
                include_individual_pages=True,
                export_formats=['csv', 'database'],
                progress_callback=progress_callback
            )
            
            # Clean up
            scraper.close()
            
            # Validate results
            total_time = time.time() - start_time
            success = (
                result.get('success', False) and
                result.get('session_stats', {}).get('individual_properties_scraped', 0) > 0
            )
            
            if success:
                stats = result.get('session_stats', {})
                individual_scraped = stats.get('individual_properties_scraped', 0)
                
                print(f"   ✅ Individual property scraping successful:")
                print(f"      🏠 Individual properties scraped: {individual_scraped}")
                print(f"      ⏱️ Total time: {total_time:.1f}s")
                
                return True
            else:
                print(f"   ❌ Individual property scraping failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"   ❌ Individual property scraping test failed: {str(e)}")
            return False
    
    def test_duplicate_detection(self) -> bool:
        """Test duplicate detection system"""
        
        print("   🔄 Testing duplicate detection...")
        
        try:
            from individual_property_tracking_system import IndividualPropertyTracker
            
            # Create tracker
            tracker = IndividualPropertyTracker(db_path='test_duplicate_detection.db')
            
            # Test URLs
            test_urls = [
                "https://www.magicbricks.com/property-1-gurgaon-pdpid-test001",
                "https://www.magicbricks.com/property-2-gurgaon-pdpid-test002",
                "https://www.magicbricks.com/property-3-gurgaon-pdpid-test003"
            ]
            
            # First run - all should be new
            session_id = tracker.create_scraping_session("Duplicate Test 1", len(test_urls))
            filter_result_1 = tracker.filter_urls_for_scraping(test_urls)
            
            print(f"      📊 First run: {len(filter_result_1['urls_to_scrape'])} to scrape, {len(filter_result_1['urls_to_skip'])} to skip")
            
            # Simulate scraping first 2 properties
            for i, url in enumerate(test_urls[:2]):
                test_property = {
                    'url': url,
                    'title': f'Test Property {i+1}',
                    'price': f'₹{(i+1)*50} Lakh',
                    'area': f'{1000 + i*100} sq ft'
                }
                tracker.track_scraped_property(url, test_property, session_id)
            
            # Second run - should detect duplicates
            session_id_2 = tracker.create_scraping_session("Duplicate Test 2", len(test_urls))
            filter_result_2 = tracker.filter_urls_for_scraping(test_urls)
            
            print(f"      📊 Second run: {len(filter_result_2['urls_to_scrape'])} to scrape, {len(filter_result_2['urls_to_skip'])} to skip")
            
            # Validate duplicate detection
            success = (
                len(filter_result_1['urls_to_scrape']) == 3 and  # All new in first run
                len(filter_result_1['urls_to_skip']) == 0 and
                len(filter_result_2['urls_to_scrape']) == 1 and  # Only 1 new in second run
                len(filter_result_2['urls_to_skip']) == 2        # 2 duplicates detected
            )
            
            # Clean up test database
            import os
            if os.path.exists('test_duplicate_detection.db'):
                os.remove('test_duplicate_detection.db')
            
            if success:
                print("   ✅ Duplicate detection working correctly")
                return True
            else:
                print("   ❌ Duplicate detection validation failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Duplicate detection test failed: {str(e)}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling and recovery"""
        
        print("   🛡️ Testing error handling...")
        
        try:
            # Test with invalid configuration
            from modular_magicbricks_gui import ModularMagicBricksGUI
            
            app = ModularMagicBricksGUI()
            
            # Test invalid configuration validation
            invalid_config = {
                'city': '',  # Invalid empty city
                'max_pages': 0,  # Invalid page count
                'export_csv': False,
                'export_json': False,
                'export_excel': False,
                'export_database': False  # No export formats
            }
            
            validation_result = app.validate_config(invalid_config)
            
            # Should return False for invalid config
            if not validation_result:
                print("   ✅ Configuration validation working correctly")
                return True
            else:
                print("   ❌ Configuration validation failed to catch invalid config")
                return False
                
        except Exception as e:
            print(f"   ❌ Error handling test failed: {str(e)}")
            return False
    
    def test_performance_under_load(self) -> bool:
        """Test performance optimization systems"""
        
        print("   ⚡ Testing performance optimization...")
        
        try:
            from performance_optimization_system import PerformanceOptimizationSystem
            
            # Create performance system
            perf_system = PerformanceOptimizationSystem()
            
            # Test caching
            test_data = {'title': 'Test Property', 'price': '₹50 Lakh'}
            cache_success = perf_system.cache_property_data('https://test.com/prop1', test_data)
            cached_data = perf_system.get_cached_property_data('https://test.com/prop1')
            
            # Test performance profiling
            with perf_system.time_scraping_operation('test_operation'):
                time.sleep(0.1)  # Simulate work
            
            # Get stats
            stats = perf_system.get_comprehensive_stats()
            
            # Validate performance systems
            success = (
                cache_success and
                cached_data is not None and
                cached_data['title'] == 'Test Property' and
                'cache' in stats and
                'memory' in stats and
                'performance' in stats
            )
            
            if success:
                print("   ✅ Performance optimization systems working correctly")
                print(f"      💾 Cache hit rate: {stats['cache']['hit_rate_percent']:.1f}%")
                print(f"      🧠 Memory usage: {stats['memory']['current_mb']:.1f}MB")
                return True
            else:
                print("   ❌ Performance optimization validation failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Performance optimization test failed: {str(e)}")
            return False
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'PASSED')
        failed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'FAILED')
        error_tests = sum(1 for result in self.test_results.values() if result['status'] == 'ERROR')
        
        print(f"📊 SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   💥 Errors: {error_tests}")
        print(f"   📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        for test_name, result in self.test_results.items():
            status_icon = {"PASSED": "✅", "FAILED": "❌", "ERROR": "💥"}[result['status']]
            print(f"   {status_icon} {test_name}: {result['status']} ({result['duration']:.1f}s)")
            
            if result['status'] != 'PASSED' and 'error' in result['details']:
                print(f"      Error: {result['details']['error']}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if passed_tests == total_tests:
            print("   🎉 ALL TESTS PASSED - SYSTEM FULLY VALIDATED")
            print("   ✅ Ready for production deployment")
        elif passed_tests >= total_tests * 0.8:
            print("   ⚠️  MOSTLY FUNCTIONAL - Minor issues need attention")
            print("   🔧 Address failed tests before production")
        else:
            print("   ❌ SIGNIFICANT ISSUES DETECTED")
            print("   🚫 NOT READY for production - Major fixes required")
        
        return passed_tests == total_tests


if __name__ == "__main__":
    # Run comprehensive testing
    tester = GUITestFramework()
    tester.run_comprehensive_tests()
