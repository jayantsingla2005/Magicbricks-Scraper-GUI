#!/usr/bin/env python3
"""
Final Testing & Bug Fixes Suite
Comprehensive final testing, validation, and optimization for production release.
"""

import os
import sys
import time
import json
import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import psutil
import threading

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our systems
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode
from multi_city_system import MultiCitySystem
from error_handling_system import ErrorHandlingSystem
from multi_city_parallel_processor import MultiCityParallelProcessor


class TestSeverity(Enum):
    """Test severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class TestCategory(Enum):
    """Test categories"""
    FUNCTIONALITY = "functionality"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    USABILITY = "usability"
    SECURITY = "security"
    COMPATIBILITY = "compatibility"


@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    category: TestCategory
    severity: TestSeverity
    passed: bool
    execution_time: float
    details: str
    error_message: Optional[str] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None


class FinalTestingSuite:
    """
    Comprehensive final testing and validation suite
    """
    
    def __init__(self, output_directory: str = '.'):
        """Initialize final testing suite"""
        
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
        
        # Test results storage
        self.test_results = []
        self.critical_issues = []
        self.performance_issues = []
        self.recommendations = []
        
        # System monitoring
        self.system_monitor = SystemMonitor()
        
        print("🔬 Final Testing Suite Initialized")
        print(f"   📁 Output directory: {self.output_directory}")
        print(f"   🎯 Target: Production readiness validation")
    
    def run_critical_functionality_tests(self) -> List[TestResult]:
        """Run critical functionality tests"""
        
        print("\n🔥 CRITICAL FUNCTIONALITY TESTS")
        print("="*50)
        
        tests = []
        
        # Test 1: Basic Scraping Functionality
        test_result = self._test_basic_scraping()
        tests.append(test_result)
        self.test_results.append(test_result)
        
        # Test 2: Incremental Scraping
        test_result = self._test_incremental_scraping()
        tests.append(test_result)
        self.test_results.append(test_result)
        
        # Test 3: Multi-City Processing
        test_result = self._test_multi_city_processing()
        tests.append(test_result)
        self.test_results.append(test_result)
        
        # Test 4: Error Handling
        test_result = self._test_error_handling()
        tests.append(test_result)
        self.test_results.append(test_result)
        
        # Test 5: Data Export
        test_result = self._test_data_export()
        tests.append(test_result)
        self.test_results.append(test_result)
        
        return tests
    
    def _test_basic_scraping(self) -> TestResult:
        """Test basic scraping functionality"""
        
        print("🧪 Testing basic scraping functionality...")
        start_time = time.time()
        
        try:
            # Initialize scraper
            scraper = IntegratedMagicBricksScraper(headless=True)
            
            # Test scraping
            result = scraper.scrape_properties_with_incremental(
                city='mumbai',
                mode=ScrapingMode.FULL,
                max_pages=2
            )
            
            # Validate results
            properties_found = result.get('session_stats', {}).get('properties_found', 0)
            pages_scraped = result.get('pages_scraped', 0)

            success = (
                result['success'] and
                properties_found > 0 and
                pages_scraped > 0
            )

            execution_time = time.time() - start_time

            # Performance metrics
            properties_per_minute = (properties_found / execution_time) * 60
            
            performance_metrics = {
                'properties_found': properties_found,
                'pages_scraped': pages_scraped,
                'properties_per_minute': properties_per_minute,
                'execution_time': execution_time
            }

            details = f"Found {properties_found} properties in {pages_scraped} pages"
            
            # Clean up
            scraper.close()
            
            return TestResult(
                test_name="Basic Scraping Functionality",
                category=TestCategory.FUNCTIONALITY,
                severity=TestSeverity.CRITICAL,
                passed=success,
                execution_time=execution_time,
                details=details,
                performance_metrics=performance_metrics,
                recommendations=["Ensure stable internet connection"] if not success else None
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name="Basic Scraping Functionality",
                category=TestCategory.FUNCTIONALITY,
                severity=TestSeverity.CRITICAL,
                passed=False,
                execution_time=execution_time,
                details="Failed to complete basic scraping",
                error_message=str(e),
                recommendations=["Check system requirements", "Verify internet connection", "Update Chrome browser"]
            )
    
    def _test_incremental_scraping(self) -> TestResult:
        """Test incremental scraping functionality"""
        
        print("🧪 Testing incremental scraping...")
        start_time = time.time()
        
        try:
            scraper = IntegratedMagicBricksScraper(headless=True, incremental_enabled=True)
            
            # First run (full)
            result1 = scraper.scrape_properties_with_incremental(
                city='mumbai',
                mode=ScrapingMode.INCREMENTAL,
                max_pages=3
            )
            
            # Wait a moment
            time.sleep(2)
            
            # Second run (incremental)
            result2 = scraper.scrape_properties_with_incremental(
                city='mumbai',
                mode=ScrapingMode.INCREMENTAL,
                max_pages=3
            )
            
            execution_time = time.time() - start_time
            
            # Get properties from session stats
            props1 = result1.get('session_stats', {}).get('properties_found', 0)
            props2 = result2.get('session_stats', {}).get('properties_found', 0)
            pages1 = result1.get('pages_scraped', 0)
            pages2 = result2.get('pages_scraped', 0)

            # Validate incremental behavior
            success = (
                result1['success'] and result2['success'] and
                pages2 <= pages1  # Should be fewer or equal pages
            )

            time_savings = 0
            if result1['session_stats'] and result2['session_stats']:
                time1 = result1['session_stats'].get('duration_seconds', 0)
                time2 = result2['session_stats'].get('duration_seconds', 0)
                if time1 > 0:
                    time_savings = ((time1 - time2) / time1) * 100

            performance_metrics = {
                'first_run_properties': props1,
                'second_run_properties': props2,
                'time_savings_percent': time_savings,
                'incremental_working': pages2 <= pages1
            }
            
            details = f"Incremental mode saved {time_savings:.1f}% time"
            
            scraper.close()
            
            return TestResult(
                test_name="Incremental Scraping",
                category=TestCategory.FUNCTIONALITY,
                severity=TestSeverity.HIGH,
                passed=success,
                execution_time=execution_time,
                details=details,
                performance_metrics=performance_metrics
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name="Incremental Scraping",
                category=TestCategory.FUNCTIONALITY,
                severity=TestSeverity.HIGH,
                passed=False,
                execution_time=execution_time,
                details="Incremental scraping failed",
                error_message=str(e)
            )
    
    def _test_multi_city_processing(self) -> TestResult:
        """Test multi-city parallel processing"""
        
        print("🧪 Testing multi-city processing...")
        start_time = time.time()
        
        try:
            # Progress tracking
            progress_updates = []
            def progress_callback(data):
                progress_updates.append(data)
            
            # Initialize processor
            processor = MultiCityParallelProcessor(max_workers=2, progress_callback=progress_callback)
            
            # Test configuration
            config = {
                'mode': ScrapingMode.INCREMENTAL,
                'max_pages': 2,
                'headless': True,
                'incremental_enabled': True,
                'output_directory': str(self.output_directory)
            }
            
            # Start processing
            cities = ['MUM', 'DEL']  # Use correct 3-letter city codes
            success = processor.start_parallel_processing(cities, config)
            
            # Wait for completion
            time.sleep(20)
            
            # Get results
            summary = processor.get_processing_summary()
            
            execution_time = time.time() - start_time
            
            # Validate results
            test_success = (
                success and
                summary['statistics']['total_properties_saved'] > 0 and
                len(progress_updates) > 0
            )
            
            performance_metrics = {
                'cities_processed': len(cities),
                'total_properties': summary['statistics']['total_properties_saved'],
                'parallel_efficiency': summary['statistics']['total_properties_saved'] / execution_time,
                'progress_updates': len(progress_updates)
            }
            
            details = f"Processed {len(cities)} cities with {summary['statistics']['total_properties_saved']} total properties"
            
            # Stop processing
            processor.stop_processing()
            
            return TestResult(
                test_name="Multi-City Parallel Processing",
                category=TestCategory.FUNCTIONALITY,
                severity=TestSeverity.HIGH,
                passed=test_success,
                execution_time=execution_time,
                details=details,
                performance_metrics=performance_metrics
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name="Multi-City Parallel Processing",
                category=TestCategory.FUNCTIONALITY,
                severity=TestSeverity.HIGH,
                passed=False,
                execution_time=execution_time,
                details="Multi-city processing failed",
                error_message=str(e)
            )
    
    def _test_error_handling(self) -> TestResult:
        """Test error handling system"""
        
        print("🧪 Testing error handling...")
        start_time = time.time()
        
        try:
            # Initialize error handler
            error_handler = ErrorHandlingSystem()
            
            # Test different error types
            test_errors = [
                ConnectionError("Test network error"),
                ValueError("Test validation error"),
                Exception("Test general error")
            ]
            
            handled_errors = 0
            for error in test_errors:
                try:
                    error_info = error_handler.handle_error(error, {'test': True}, 'testing')
                    if error_info and error_info.category:
                        handled_errors += 1
                except:
                    pass
            
            execution_time = time.time() - start_time
            
            # Test error log functionality
            error_summary = error_handler.get_error_summary()
            export_file = error_handler.export_error_log()
            
            success = (
                handled_errors == len(test_errors) and
                error_summary['total_errors'] >= len(test_errors) and
                export_file is not None
            )
            
            performance_metrics = {
                'errors_handled': handled_errors,
                'total_errors_logged': error_summary['total_errors'],
                'export_successful': export_file is not None
            }
            
            details = f"Successfully handled {handled_errors}/{len(test_errors)} test errors"
            
            return TestResult(
                test_name="Error Handling System",
                category=TestCategory.RELIABILITY,
                severity=TestSeverity.HIGH,
                passed=success,
                execution_time=execution_time,
                details=details,
                performance_metrics=performance_metrics
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name="Error Handling System",
                category=TestCategory.RELIABILITY,
                severity=TestSeverity.HIGH,
                passed=False,
                execution_time=execution_time,
                details="Error handling test failed",
                error_message=str(e)
            )
    
    def _test_data_export(self) -> TestResult:
        """Test data export functionality"""
        
        print("🧪 Testing data export...")
        start_time = time.time()
        
        try:
            # Create test data
            test_data = [
                {
                    'title': 'Test Property 1',
                    'price': '50 Lac',
                    'location': 'Test Location',
                    'area': '1000 sqft'
                },
                {
                    'title': 'Test Property 2',
                    'price': '75 Lac',
                    'location': 'Test Location 2',
                    'area': '1200 sqft'
                }
            ]
            
            # Test CSV export
            import pandas as pd
            df = pd.DataFrame(test_data)
            
            csv_file = self.output_directory / 'test_export.csv'
            excel_file = self.output_directory / 'test_export.xlsx'
            json_file = self.output_directory / 'test_export.json'
            
            # Export to different formats
            exports_successful = 0
            
            try:
                df.to_csv(csv_file, index=False)
                if csv_file.exists():
                    exports_successful += 1
            except:
                pass
            
            try:
                df.to_excel(excel_file, index=False)
                if excel_file.exists():
                    exports_successful += 1
            except:
                pass
            
            try:
                with open(json_file, 'w') as f:
                    json.dump(test_data, f, indent=2)
                if json_file.exists():
                    exports_successful += 1
            except:
                pass
            
            execution_time = time.time() - start_time
            
            success = exports_successful == 3
            
            performance_metrics = {
                'csv_export': csv_file.exists(),
                'excel_export': excel_file.exists(),
                'json_export': json_file.exists(),
                'total_successful': exports_successful
            }
            
            details = f"Successfully exported to {exports_successful}/3 formats"
            
            # Clean up test files
            for file in [csv_file, excel_file, json_file]:
                if file.exists():
                    file.unlink()
            
            return TestResult(
                test_name="Data Export Functionality",
                category=TestCategory.FUNCTIONALITY,
                severity=TestSeverity.MEDIUM,
                passed=success,
                execution_time=execution_time,
                details=details,
                performance_metrics=performance_metrics
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name="Data Export Functionality",
                category=TestCategory.FUNCTIONALITY,
                severity=TestSeverity.MEDIUM,
                passed=False,
                execution_time=execution_time,
                details="Data export test failed",
                error_message=str(e)
            )
    
    def run_performance_tests(self) -> List[TestResult]:
        """Run performance and optimization tests"""
        
        print("\n⚡ PERFORMANCE TESTS")
        print("="*50)
        
        tests = []
        
        # Test 1: Memory Usage
        test_result = self._test_memory_usage()
        tests.append(test_result)
        self.test_results.append(test_result)
        
        # Test 2: CPU Usage
        test_result = self._test_cpu_usage()
        tests.append(test_result)
        self.test_results.append(test_result)
        
        # Test 3: Scraping Speed
        test_result = self._test_scraping_speed()
        tests.append(test_result)
        self.test_results.append(test_result)
        
        return tests
    
    def _test_memory_usage(self) -> TestResult:
        """Test memory usage under load"""
        
        print("🧪 Testing memory usage...")
        start_time = time.time()
        
        try:
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Run memory-intensive operation
            scraper = IntegratedMagicBricksScraper(headless=True)
            
            # Monitor memory during scraping
            max_memory = initial_memory
            
            def monitor_memory():
                nonlocal max_memory
                while True:
                    try:
                        current_memory = process.memory_info().rss / 1024 / 1024
                        max_memory = max(max_memory, current_memory)
                        time.sleep(0.5)
                    except:
                        break
            
            monitor_thread = threading.Thread(target=monitor_memory, daemon=True)
            monitor_thread.start()
            
            # Perform scraping
            result = scraper.scrape_properties_with_incremental(
                city='mumbai',
                mode=ScrapingMode.FULL,
                max_pages=3
            )
            
            scraper.close()
            time.sleep(1)  # Allow monitoring to complete
            
            execution_time = time.time() - start_time
            memory_increase = max_memory - initial_memory
            
            # Memory usage should be reasonable (< 500MB increase)
            success = memory_increase < 500
            
            performance_metrics = {
                'initial_memory_mb': initial_memory,
                'max_memory_mb': max_memory,
                'memory_increase_mb': memory_increase,
                'properties_processed': result.get('properties_found', 0)
            }
            
            details = f"Memory increased by {memory_increase:.1f} MB during scraping"
            
            return TestResult(
                test_name="Memory Usage Test",
                category=TestCategory.PERFORMANCE,
                severity=TestSeverity.MEDIUM,
                passed=success,
                execution_time=execution_time,
                details=details,
                performance_metrics=performance_metrics,
                recommendations=["Consider memory optimization"] if not success else None
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name="Memory Usage Test",
                category=TestCategory.PERFORMANCE,
                severity=TestSeverity.MEDIUM,
                passed=False,
                execution_time=execution_time,
                details="Memory usage test failed",
                error_message=str(e)
            )
    
    def _test_cpu_usage(self) -> TestResult:
        """Test CPU usage during operation"""
        
        print("🧪 Testing CPU usage...")
        start_time = time.time()
        
        try:
            process = psutil.Process()
            cpu_samples = []
            
            def monitor_cpu():
                for _ in range(10):  # Sample for 10 seconds
                    cpu_samples.append(process.cpu_percent())
                    time.sleep(1)
            
            monitor_thread = threading.Thread(target=monitor_cpu, daemon=True)
            monitor_thread.start()
            
            # Perform CPU-intensive operation
            scraper = IntegratedMagicBricksScraper(headless=True)
            result = scraper.scrape_properties_with_incremental(
                city='mumbai',
                mode=ScrapingMode.FULL,
                max_pages=2
            )
            scraper.close()
            
            monitor_thread.join(timeout=15)
            execution_time = time.time() - start_time
            
            avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
            max_cpu = max(cpu_samples) if cpu_samples else 0
            
            # CPU usage should be reasonable (< 80% average)
            success = avg_cpu < 80
            
            performance_metrics = {
                'average_cpu_percent': avg_cpu,
                'max_cpu_percent': max_cpu,
                'cpu_samples': len(cpu_samples),
                'properties_processed': result.get('properties_found', 0)
            }
            
            details = f"Average CPU usage: {avg_cpu:.1f}%, Max: {max_cpu:.1f}%"
            
            return TestResult(
                test_name="CPU Usage Test",
                category=TestCategory.PERFORMANCE,
                severity=TestSeverity.MEDIUM,
                passed=success,
                execution_time=execution_time,
                details=details,
                performance_metrics=performance_metrics
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name="CPU Usage Test",
                category=TestCategory.PERFORMANCE,
                severity=TestSeverity.MEDIUM,
                passed=False,
                execution_time=execution_time,
                details="CPU usage test failed",
                error_message=str(e)
            )
    
    def _test_scraping_speed(self) -> TestResult:
        """Test scraping speed and efficiency"""
        
        print("🧪 Testing scraping speed...")
        start_time = time.time()
        
        try:
            scraper = IntegratedMagicBricksScraper(headless=True)
            
            # Measure scraping speed
            result = scraper.scrape_properties_with_incremental(
                city='mumbai',
                mode=ScrapingMode.FULL,
                max_pages=3
            )
            
            execution_time = time.time() - start_time
            
            properties_found = result.get('session_stats', {}).get('properties_found', 0)
            pages_scraped = result.get('pages_scraped', 0)
            
            # Calculate performance metrics
            properties_per_minute = (properties_found / execution_time) * 60 if execution_time > 0 else 0
            pages_per_minute = (pages_scraped / execution_time) * 60 if execution_time > 0 else 0
            
            # Speed should be reasonable (> 30 properties/minute)
            success = properties_per_minute > 30
            
            performance_metrics = {
                'properties_found': properties_found,
                'pages_scraped': pages_scraped,
                'execution_time': execution_time,
                'properties_per_minute': properties_per_minute,
                'pages_per_minute': pages_per_minute
            }
            
            details = f"Speed: {properties_per_minute:.1f} properties/minute, {pages_per_minute:.1f} pages/minute"
            
            scraper.close()
            
            return TestResult(
                test_name="Scraping Speed Test",
                category=TestCategory.PERFORMANCE,
                severity=TestSeverity.MEDIUM,
                passed=success,
                execution_time=execution_time,
                details=details,
                performance_metrics=performance_metrics,
                recommendations=["Optimize delays and selectors"] if not success else None
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name="Scraping Speed Test",
                category=TestCategory.PERFORMANCE,
                severity=TestSeverity.MEDIUM,
                passed=False,
                execution_time=execution_time,
                details="Scraping speed test failed",
                error_message=str(e)
            )
    
    def run_compatibility_tests(self) -> List[TestResult]:
        """Run compatibility and system tests"""
        
        print("\n🔧 COMPATIBILITY TESTS")
        print("="*50)
        
        tests = []
        
        # Test 1: System Requirements
        test_result = self._test_system_requirements()
        tests.append(test_result)
        self.test_results.append(test_result)
        
        # Test 2: Dependencies
        test_result = self._test_dependencies()
        tests.append(test_result)
        self.test_results.append(test_result)
        
        return tests
    
    def _test_system_requirements(self) -> TestResult:
        """Test system requirements compliance"""
        
        print("🧪 Testing system requirements...")
        start_time = time.time()
        
        try:
            import platform
            
            # Check system specifications
            system_info = {
                'os': platform.system(),
                'os_version': platform.version(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'python_version': platform.python_version()
            }
            
            # Check memory
            memory = psutil.virtual_memory()
            total_memory_gb = memory.total / (1024**3)
            
            # Check disk space
            disk = psutil.disk_usage('.')
            free_space_gb = disk.free / (1024**3)
            
            execution_time = time.time() - start_time
            
            # Validate requirements
            python_version_parts = system_info['python_version'].split('.')
            python_major = int(python_version_parts[0])
            python_minor = int(python_version_parts[1])
            python_version_ok = python_major > 3 or (python_major == 3 and python_minor >= 8)

            requirements_met = (
                system_info['os'] == 'Windows' and
                total_memory_gb >= 4 and
                free_space_gb >= 0.5 and
                python_version_ok
            )
            
            performance_metrics = {
                'total_memory_gb': total_memory_gb,
                'free_disk_space_gb': free_space_gb,
                'os_compatible': system_info['os'] == 'Windows',
                'python_version_ok': python_version_ok
            }
            
            details = f"OS: {system_info['os']}, RAM: {total_memory_gb:.1f}GB, Free Space: {free_space_gb:.1f}GB"
            
            return TestResult(
                test_name="System Requirements",
                category=TestCategory.COMPATIBILITY,
                severity=TestSeverity.HIGH,
                passed=requirements_met,
                execution_time=execution_time,
                details=details,
                performance_metrics=performance_metrics,
                recommendations=["Upgrade system to meet minimum requirements"] if not requirements_met else None
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name="System Requirements",
                category=TestCategory.COMPATIBILITY,
                severity=TestSeverity.HIGH,
                passed=False,
                execution_time=execution_time,
                details="System requirements check failed",
                error_message=str(e)
            )
    
    def _test_dependencies(self) -> TestResult:
        """Test dependency availability and versions"""
        
        print("🧪 Testing dependencies...")
        start_time = time.time()
        
        try:
            required_packages = [
                'selenium',
                'pandas',
                'openpyxl',
                'bs4',  # beautifulsoup4 imports as bs4
                'requests',
                'psutil'
            ]
            
            available_packages = 0
            package_versions = {}
            
            for package in required_packages:
                try:
                    module = __import__(package)
                    version = getattr(module, '__version__', 'unknown')
                    package_versions[package] = version
                    available_packages += 1
                except ImportError:
                    package_versions[package] = 'missing'
            
            execution_time = time.time() - start_time
            
            success = available_packages == len(required_packages)
            
            performance_metrics = {
                'total_packages': len(required_packages),
                'available_packages': available_packages,
                'package_versions': package_versions
            }
            
            details = f"Dependencies: {available_packages}/{len(required_packages)} available"
            
            return TestResult(
                test_name="Dependency Check",
                category=TestCategory.COMPATIBILITY,
                severity=TestSeverity.HIGH,
                passed=success,
                execution_time=execution_time,
                details=details,
                performance_metrics=performance_metrics,
                recommendations=["Install missing dependencies"] if not success else None
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name="Dependency Check",
                category=TestCategory.COMPATIBILITY,
                severity=TestSeverity.HIGH,
                passed=False,
                execution_time=execution_time,
                details="Dependency check failed",
                error_message=str(e)
            )
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze all test results and generate summary"""
        
        if not self.test_results:
            return {}
        
        # Categorize results
        passed_tests = [t for t in self.test_results if t.passed]
        failed_tests = [t for t in self.test_results if not t.passed]
        critical_failures = [t for t in failed_tests if t.severity == TestSeverity.CRITICAL]
        
        # Calculate metrics
        total_tests = len(self.test_results)
        pass_rate = len(passed_tests) / total_tests if total_tests > 0 else 0
        
        # Performance analysis
        avg_execution_time = sum(t.execution_time for t in self.test_results) / total_tests
        
        # Category analysis
        category_results = {}
        for category in TestCategory:
            category_tests = [t for t in self.test_results if t.category == category]
            if category_tests:
                category_pass_rate = len([t for t in category_tests if t.passed]) / len(category_tests)
                category_results[category.value] = {
                    'total': len(category_tests),
                    'passed': len([t for t in category_tests if t.passed]),
                    'pass_rate': category_pass_rate
                }
        
        # Collect recommendations
        all_recommendations = []
        for test in failed_tests:
            if test.recommendations:
                all_recommendations.extend(test.recommendations)
        
        return {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': len(passed_tests),
                'failed_tests': len(failed_tests),
                'critical_failures': len(critical_failures),
                'pass_rate': pass_rate,
                'avg_execution_time': avg_execution_time
            },
            'category_results': category_results,
            'critical_failures': [
                {
                    'test_name': t.test_name,
                    'error': t.error_message,
                    'recommendations': t.recommendations
                } for t in critical_failures
            ],
            'recommendations': list(set(all_recommendations)),
            'production_ready': len(critical_failures) == 0 and pass_rate >= 0.8
        }
    
    def generate_final_report(self, analysis: Dict[str, Any]) -> str:
        """Generate comprehensive final testing report"""
        
        report = []
        report.append("🔬 FINAL TESTING & VALIDATION REPORT")
        report.append("="*60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Test Suite Version: 1.0")
        report.append("")
        
        # Executive Summary
        summary = analysis['summary']
        report.append("📊 EXECUTIVE SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Tests: {summary['total_tests']}")
        report.append(f"Passed: {summary['passed_tests']}")
        report.append(f"Failed: {summary['failed_tests']}")
        report.append(f"Critical Failures: {summary['critical_failures']}")
        report.append(f"Pass Rate: {summary['pass_rate']:.1%}")
        report.append(f"Average Execution Time: {summary['avg_execution_time']:.2f}s")
        report.append("")
        
        # Production Readiness
        production_ready = analysis['production_ready']
        status = "✅ PRODUCTION READY" if production_ready else "❌ NOT PRODUCTION READY"
        report.append(f"🚀 PRODUCTION STATUS: {status}")
        report.append("")
        
        # Category Results
        report.append("📋 CATEGORY BREAKDOWN")
        report.append("-" * 40)
        for category, results in analysis['category_results'].items():
            report.append(f"{category.title()}: {results['passed']}/{results['total']} ({results['pass_rate']:.1%})")
        report.append("")
        
        # Critical Failures
        if analysis['critical_failures']:
            report.append("🚨 CRITICAL FAILURES")
            report.append("-" * 40)
            for failure in analysis['critical_failures']:
                report.append(f"❌ {failure['test_name']}")
                if failure['error']:
                    report.append(f"   Error: {failure['error']}")
                if failure['recommendations']:
                    report.append(f"   Recommendations: {', '.join(failure['recommendations'])}")
            report.append("")
        
        # Recommendations
        if analysis['recommendations']:
            report.append("💡 RECOMMENDATIONS")
            report.append("-" * 40)
            for i, rec in enumerate(analysis['recommendations'], 1):
                report.append(f"{i}. {rec}")
            report.append("")
        
        # Individual Test Results
        report.append("🧪 DETAILED TEST RESULTS")
        report.append("-" * 40)
        for test in self.test_results:
            status = "✅ PASS" if test.passed else "❌ FAIL"
            report.append(f"{status} {test.test_name} ({test.execution_time:.2f}s)")
            report.append(f"   Category: {test.category.value}, Severity: {test.severity.value}")
            report.append(f"   Details: {test.details}")
            if test.error_message:
                report.append(f"   Error: {test.error_message}")
            if test.performance_metrics:
                report.append(f"   Metrics: {test.performance_metrics}")
            report.append("")
        
        # Next Steps
        report.append("🎯 NEXT STEPS")
        report.append("-" * 40)
        if production_ready:
            report.append("1. ✅ System is ready for production deployment")
            report.append("2. 📦 Proceed with final packaging and distribution")
            report.append("3. 📚 Complete user documentation and training materials")
            report.append("4. 🚀 Deploy to production environment")
        else:
            report.append("1. ❌ Address critical failures before deployment")
            report.append("2. 🔧 Implement recommended fixes and optimizations")
            report.append("3. 🧪 Re-run testing suite after fixes")
            report.append("4. 📋 Validate all tests pass before proceeding")
        
        return "\n".join(report)
    
    def run_comprehensive_final_testing(self) -> Dict[str, Any]:
        """Run complete final testing suite"""
        
        print("🔬 STARTING COMPREHENSIVE FINAL TESTING")
        print("="*60)
        
        # Run all test categories
        self.run_critical_functionality_tests()
        self.run_performance_tests()
        self.run_compatibility_tests()
        
        # Analyze results
        analysis = self.analyze_results()
        
        # Generate report
        report = self.generate_final_report(analysis)
        print("\n" + report)
        
        # Save report
        report_file = self.output_directory / f'final_testing_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n📄 Final testing report saved: {report_file}")
        
        return analysis


class SystemMonitor:
    """System resource monitoring utility"""
    
    def __init__(self):
        self.monitoring = False
        self.metrics = []
    
    def start_monitoring(self):
        """Start system monitoring"""
        self.monitoring = True
        self.metrics = []
        
        def monitor():
            while self.monitoring:
                try:
                    self.metrics.append({
                        'timestamp': datetime.now(),
                        'cpu_percent': psutil.cpu_percent(),
                        'memory_percent': psutil.virtual_memory().percent,
                        'disk_usage': psutil.disk_usage('.').percent
                    })
                    time.sleep(1)
                except:
                    break
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
        return self.metrics


def main():
    """Run final testing suite"""
    
    try:
        print("🔬 MAGICBRICKS SCRAPER FINAL TESTING")
        print("="*60)
        
        # Initialize testing suite
        testing_suite = FinalTestingSuite()
        
        # Run comprehensive testing
        analysis = testing_suite.run_comprehensive_final_testing()
        
        # Summary
        print(f"\n✅ Final testing completed!")
        print(f"📊 Pass rate: {analysis['summary']['pass_rate']:.1%}")
        print(f"🚀 Production ready: {analysis['production_ready']}")
        
        if analysis['production_ready']:
            print("🎉 System is ready for production deployment!")
        else:
            print("⚠️ Address critical issues before deployment")
        
        return analysis['production_ready']
        
    except Exception as e:
        print(f"❌ Final testing failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
