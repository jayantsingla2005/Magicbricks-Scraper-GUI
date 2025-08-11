#!/usr/bin/env python3
"""
Performance Testing & Optimization System
Comprehensive performance testing, benchmarking, and optimization for MagicBricks scraper.
"""

import time
import psutil
import threading
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import sqlite3
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our systems
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode
from multi_city_system import MultiCitySystem
from multi_city_parallel_processor import MultiCityParallelProcessor


@dataclass
class PerformanceMetrics:
    """Performance metrics data class"""
    test_name: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    pages_scraped: int
    properties_found: int
    properties_per_minute: float
    pages_per_minute: float
    memory_usage_mb: float
    cpu_usage_percent: float
    success_rate: float
    error_count: int
    time_savings_percent: Optional[float] = None


class PerformanceTestingSuite:
    """
    Comprehensive performance testing and optimization system
    """
    
    def __init__(self, output_directory: str = '.'):
        """Initialize performance testing suite"""
        
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
        
        # Test results storage
        self.test_results = []
        self.baseline_metrics = {}
        
        # System monitoring
        self.process = psutil.Process()
        self.monitoring_active = False
        self.monitoring_data = []
        
        # Test configurations
        self.test_configs = self._initialize_test_configurations()
        
        print("🚀 Performance Testing Suite Initialized")
        print(f"   📁 Output directory: {self.output_directory}")
        print(f"   🧪 Test configurations: {len(self.test_configs)}")
    
    def _initialize_test_configurations(self) -> Dict[str, Dict[str, Any]]:
        """Initialize test configurations"""
        
        return {
            'baseline_incremental': {
                'name': 'Baseline Incremental Scraping',
                'mode': ScrapingMode.INCREMENTAL,
                'max_pages': 5,
                'city': 'mumbai',
                'headless': True,
                'incremental_enabled': True,
                'description': 'Standard incremental scraping performance'
            },
            'baseline_full': {
                'name': 'Baseline Full Scraping',
                'mode': ScrapingMode.FULL,
                'max_pages': 5,
                'city': 'mumbai',
                'headless': True,
                'incremental_enabled': False,
                'description': 'Standard full scraping performance'
            },
            'conservative_mode': {
                'name': 'Conservative Mode Performance',
                'mode': ScrapingMode.CONSERVATIVE,
                'max_pages': 5,
                'city': 'mumbai',
                'headless': True,
                'incremental_enabled': True,
                'description': 'Conservative incremental scraping'
            },
            'multi_city_parallel': {
                'name': 'Multi-City Parallel Processing',
                'cities': ['mumbai', 'delhi', 'bangalore'],
                'mode': ScrapingMode.INCREMENTAL,
                'max_pages': 3,
                'headless': True,
                'incremental_enabled': True,
                'description': 'Parallel processing of multiple cities'
            },
            'large_dataset': {
                'name': 'Large Dataset Performance',
                'mode': ScrapingMode.INCREMENTAL,
                'max_pages': 20,
                'city': 'mumbai',
                'headless': True,
                'incremental_enabled': True,
                'description': 'Performance with larger datasets'
            },
            'memory_stress': {
                'name': 'Memory Stress Test',
                'mode': ScrapingMode.FULL,
                'max_pages': 15,
                'city': 'mumbai',
                'headless': True,
                'incremental_enabled': False,
                'description': 'Memory usage under stress'
            }
        }
    
    def start_system_monitoring(self):
        """Start system resource monitoring"""
        
        self.monitoring_active = True
        self.monitoring_data = []
        
        def monitor_resources():
            while self.monitoring_active:
                try:
                    # Get system metrics
                    memory_info = self.process.memory_info()
                    cpu_percent = self.process.cpu_percent()
                    
                    # Get system-wide metrics
                    system_memory = psutil.virtual_memory()
                    system_cpu = psutil.cpu_percent()
                    
                    self.monitoring_data.append({
                        'timestamp': datetime.now(),
                        'process_memory_mb': memory_info.rss / 1024 / 1024,
                        'process_cpu_percent': cpu_percent,
                        'system_memory_percent': system_memory.percent,
                        'system_cpu_percent': system_cpu
                    })
                    
                    time.sleep(1)  # Monitor every second
                    
                except Exception as e:
                    print(f"⚠️ Monitoring error: {str(e)}")
                    break
        
        # Start monitoring thread
        monitoring_thread = threading.Thread(target=monitor_resources, daemon=True)
        monitoring_thread.start()
        
        print("📊 System monitoring started")
    
    def stop_system_monitoring(self) -> Dict[str, float]:
        """Stop system monitoring and return summary"""
        
        self.monitoring_active = False
        
        if not self.monitoring_data:
            return {}
        
        # Calculate summary statistics
        memory_values = [d['process_memory_mb'] for d in self.monitoring_data]
        cpu_values = [d['process_cpu_percent'] for d in self.monitoring_data]
        
        summary = {
            'avg_memory_mb': statistics.mean(memory_values),
            'max_memory_mb': max(memory_values),
            'avg_cpu_percent': statistics.mean(cpu_values),
            'max_cpu_percent': max(cpu_values),
            'monitoring_duration': len(self.monitoring_data)
        }
        
        print("📊 System monitoring stopped")
        return summary
    
    def run_single_scraper_test(self, config: Dict[str, Any]) -> PerformanceMetrics:
        """Run a single scraper performance test"""
        
        print(f"\n🧪 Running test: {config['name']}")
        print(f"   📋 Description: {config['description']}")
        
        # Start monitoring
        self.start_system_monitoring()
        
        # Initialize metrics
        start_time = datetime.now()
        error_count = 0
        pages_scraped = 0
        properties_found = 0
        
        try:
            # Create scraper
            scraper = IntegratedMagicBricksScraper(
                headless=config.get('headless', True),
                incremental_enabled=config.get('incremental_enabled', True)
            )
            
            # Run scraping
            result = scraper.scrape_properties_with_incremental(
                city=config['city'],
                mode=config['mode'],
                max_pages=config['max_pages']
            )
            
            if result['success']:
                pages_scraped = result.get('pages_scraped', 0)
                properties_found = result.get('session_stats', {}).get('properties_found', 0)
                print(f"   ✅ Success: {pages_scraped} pages, {properties_found} properties")
            else:
                error_count = 1
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
            
            # Clean up
            scraper.close()
            
        except Exception as e:
            error_count = 1
            print(f"   ❌ Exception: {str(e)}")
        
        # Stop monitoring and get metrics
        end_time = datetime.now()
        monitoring_summary = self.stop_system_monitoring()
        
        # Calculate performance metrics
        duration_seconds = (end_time - start_time).total_seconds()
        properties_per_minute = (properties_found / duration_seconds) * 60 if duration_seconds > 0 else 0
        pages_per_minute = (pages_scraped / duration_seconds) * 60 if duration_seconds > 0 else 0
        success_rate = 1.0 if error_count == 0 else 0.0
        
        # Create metrics object
        metrics = PerformanceMetrics(
            test_name=config['name'],
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,
            pages_scraped=pages_scraped,
            properties_found=properties_found,
            properties_per_minute=properties_per_minute,
            pages_per_minute=pages_per_minute,
            memory_usage_mb=monitoring_summary.get('avg_memory_mb', 0),
            cpu_usage_percent=monitoring_summary.get('avg_cpu_percent', 0),
            success_rate=success_rate,
            error_count=error_count
        )
        
        print(f"   📊 Performance: {properties_per_minute:.1f} props/min, {pages_per_minute:.1f} pages/min")
        print(f"   💾 Memory: {metrics.memory_usage_mb:.1f} MB, CPU: {metrics.cpu_usage_percent:.1f}%")
        
        return metrics
    
    def run_parallel_processing_test(self, config: Dict[str, Any]) -> PerformanceMetrics:
        """Run parallel processing performance test"""
        
        print(f"\n🧪 Running parallel test: {config['name']}")
        print(f"   🏙️ Cities: {config['cities']}")
        
        # Start monitoring
        self.start_system_monitoring()
        
        start_time = datetime.now()
        total_properties = 0
        total_pages = 0
        error_count = 0
        
        try:
            # Progress tracking
            progress_updates = []
            def progress_callback(data):
                progress_updates.append(data)
            
            # Create parallel processor
            processor = MultiCityParallelProcessor(max_workers=3, progress_callback=progress_callback)
            
            # Configure for test
            test_config = {
                'mode': config['mode'],
                'max_pages': config['max_pages'],
                'headless': config.get('headless', True),
                'incremental_enabled': config.get('incremental_enabled', True),
                'output_directory': str(self.output_directory)
            }
            
            # Start parallel processing
            success = processor.start_parallel_processing(config['cities'], test_config)
            
            if success:
                # Wait for completion (simplified for testing)
                time.sleep(30)  # Allow time for processing
                
                # Get summary
                summary = processor.get_processing_summary()
                total_properties = summary['statistics']['total_properties_saved']
                total_pages = summary['statistics']['total_pages_scraped']
                error_count = summary['statistics']['failed_cities']
                
                print(f"   ✅ Parallel processing: {total_properties} properties, {total_pages} pages")
            else:
                error_count = len(config['cities'])
                print("   ❌ Failed to start parallel processing")
            
            # Stop processing
            processor.stop_processing()
            
        except Exception as e:
            error_count = len(config['cities'])
            print(f"   ❌ Exception: {str(e)}")
        
        # Stop monitoring and calculate metrics
        end_time = datetime.now()
        monitoring_summary = self.stop_system_monitoring()
        
        duration_seconds = (end_time - start_time).total_seconds()
        properties_per_minute = (total_properties / duration_seconds) * 60 if duration_seconds > 0 else 0
        pages_per_minute = (total_pages / duration_seconds) * 60 if duration_seconds > 0 else 0
        success_rate = 1.0 - (error_count / len(config['cities']))
        
        metrics = PerformanceMetrics(
            test_name=config['name'],
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,
            pages_scraped=total_pages,
            properties_found=total_properties,
            properties_per_minute=properties_per_minute,
            pages_per_minute=pages_per_minute,
            memory_usage_mb=monitoring_summary.get('avg_memory_mb', 0),
            cpu_usage_percent=monitoring_summary.get('avg_cpu_percent', 0),
            success_rate=success_rate,
            error_count=error_count
        )
        
        print(f"   📊 Parallel performance: {properties_per_minute:.1f} props/min, {pages_per_minute:.1f} pages/min")
        
        return metrics
    
    def run_comprehensive_performance_tests(self) -> List[PerformanceMetrics]:
        """Run all performance tests"""
        
        print("🚀 STARTING COMPREHENSIVE PERFORMANCE TESTS")
        print("="*60)
        
        all_results = []
        
        # Run single scraper tests
        for test_name, config in self.test_configs.items():
            if test_name == 'multi_city_parallel':
                continue  # Handle separately
            
            try:
                metrics = self.run_single_scraper_test(config)
                all_results.append(metrics)
                self.test_results.append(metrics)
                
                # Small delay between tests
                time.sleep(5)
                
            except Exception as e:
                print(f"❌ Test {test_name} failed: {str(e)}")
        
        # Run parallel processing test
        try:
            parallel_config = self.test_configs['multi_city_parallel']
            parallel_metrics = self.run_parallel_processing_test(parallel_config)
            all_results.append(parallel_metrics)
            self.test_results.append(parallel_metrics)
        except Exception as e:
            print(f"❌ Parallel test failed: {str(e)}")
        
        print("\n" + "="*60)
        print("📊 PERFORMANCE TESTING COMPLETE")
        
        return all_results
    
    def calculate_time_savings(self) -> Dict[str, float]:
        """Calculate time savings between different modes"""
        
        # Find baseline full scraping metrics
        full_metrics = None
        incremental_metrics = None
        
        for metrics in self.test_results:
            if 'Full Scraping' in metrics.test_name:
                full_metrics = metrics
            elif 'Incremental Scraping' in metrics.test_name:
                incremental_metrics = metrics
        
        time_savings = {}
        
        if full_metrics and incremental_metrics:
            # Calculate time savings
            if full_metrics.duration_seconds > 0:
                savings_percent = ((full_metrics.duration_seconds - incremental_metrics.duration_seconds) / 
                                 full_metrics.duration_seconds) * 100
                time_savings['incremental_vs_full'] = savings_percent
                
                # Update metrics
                incremental_metrics.time_savings_percent = savings_percent
        
        return time_savings
    
    def generate_performance_report(self) -> str:
        """Generate comprehensive performance report"""
        
        if not self.test_results:
            return "No test results available"
        
        # Calculate time savings
        time_savings = self.calculate_time_savings()
        
        # Generate report
        report = []
        report.append("🚀 MAGICBRICKS SCRAPER PERFORMANCE REPORT")
        report.append("="*60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total tests: {len(self.test_results)}")
        report.append("")
        
        # Summary statistics
        avg_properties_per_min = statistics.mean([m.properties_per_minute for m in self.test_results if m.properties_per_minute > 0])
        avg_memory_usage = statistics.mean([m.memory_usage_mb for m in self.test_results if m.memory_usage_mb > 0])
        overall_success_rate = statistics.mean([m.success_rate for m in self.test_results])
        
        report.append("📊 OVERALL PERFORMANCE SUMMARY")
        report.append("-" * 40)
        report.append(f"Average Properties/Minute: {avg_properties_per_min:.1f}")
        report.append(f"Average Memory Usage: {avg_memory_usage:.1f} MB")
        report.append(f"Overall Success Rate: {overall_success_rate:.1%}")
        report.append("")
        
        # Time savings
        if time_savings:
            report.append("⚡ TIME SAVINGS ANALYSIS")
            report.append("-" * 40)
            for comparison, savings in time_savings.items():
                report.append(f"{comparison}: {savings:.1f}% time savings")
            report.append("")
        
        # Individual test results
        report.append("🧪 INDIVIDUAL TEST RESULTS")
        report.append("-" * 40)
        
        for metrics in self.test_results:
            report.append(f"\n📋 {metrics.test_name}")
            report.append(f"   Duration: {metrics.duration_seconds:.1f}s")
            report.append(f"   Properties: {metrics.properties_found} ({metrics.properties_per_minute:.1f}/min)")
            report.append(f"   Pages: {metrics.pages_scraped} ({metrics.pages_per_minute:.1f}/min)")
            report.append(f"   Memory: {metrics.memory_usage_mb:.1f} MB")
            report.append(f"   CPU: {metrics.cpu_usage_percent:.1f}%")
            report.append(f"   Success Rate: {metrics.success_rate:.1%}")
            if metrics.time_savings_percent:
                report.append(f"   Time Savings: {metrics.time_savings_percent:.1f}%")
        
        # Performance recommendations
        report.append("\n🎯 PERFORMANCE RECOMMENDATIONS")
        report.append("-" * 40)
        
        if avg_properties_per_min > 100:
            report.append("✅ Excellent scraping speed - system is well optimized")
        elif avg_properties_per_min > 50:
            report.append("✅ Good scraping speed - minor optimizations possible")
        else:
            report.append("⚠️ Consider optimizing selectors and reducing delays")
        
        if avg_memory_usage < 200:
            report.append("✅ Efficient memory usage")
        else:
            report.append("⚠️ Consider memory optimization for large datasets")
        
        if overall_success_rate > 0.95:
            report.append("✅ Excellent reliability")
        else:
            report.append("⚠️ Consider improving error handling and recovery")
        
        return "\n".join(report)
    
    def export_results(self, filename: str = None) -> str:
        """Export performance results to JSON file"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_results_{timestamp}.json"
        
        output_path = self.output_directory / filename
        
        # Prepare data for export
        export_data = {
            'test_metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_tests': len(self.test_results),
                'test_suite_version': '1.0'
            },
            'test_results': []
        }
        
        for metrics in self.test_results:
            export_data['test_results'].append({
                'test_name': metrics.test_name,
                'start_time': metrics.start_time.isoformat(),
                'end_time': metrics.end_time.isoformat(),
                'duration_seconds': metrics.duration_seconds,
                'pages_scraped': metrics.pages_scraped,
                'properties_found': metrics.properties_found,
                'properties_per_minute': metrics.properties_per_minute,
                'pages_per_minute': metrics.pages_per_minute,
                'memory_usage_mb': metrics.memory_usage_mb,
                'cpu_usage_percent': metrics.cpu_usage_percent,
                'success_rate': metrics.success_rate,
                'error_count': metrics.error_count,
                'time_savings_percent': metrics.time_savings_percent
            })
        
        # Save to file
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"📁 Performance results exported to {output_path}")
        return str(output_path)


def main():
    """Run performance testing suite"""
    
    try:
        print("🚀 MAGICBRICKS SCRAPER PERFORMANCE TESTING")
        print("="*60)
        
        # Initialize performance testing
        perf_tester = PerformanceTestingSuite()
        
        # Run comprehensive tests
        results = perf_tester.run_comprehensive_performance_tests()
        
        # Generate and display report
        report = perf_tester.generate_performance_report()
        print("\n" + report)
        
        # Export results
        export_file = perf_tester.export_results()
        
        print(f"\n✅ Performance testing completed successfully!")
        print(f"📊 {len(results)} tests completed")
        print(f"📁 Results exported to: {export_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance testing failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
