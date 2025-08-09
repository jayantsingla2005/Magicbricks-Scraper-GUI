#!/usr/bin/env python3
"""
Performance Optimization Testing Script
Tests optimized scraper against baseline to measure performance improvements.
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

try:
    from src.core.modern_scraper import ModernMagicBricksScraper
    from src.core.optimized_scraper import OptimizedMagicBricksScraper
except ImportError:
    print("❌ Import error - check module paths")
    sys.exit(1)

def test_performance_comparison():
    """Compare performance between standard and optimized scrapers"""
    
    print("🔬 Performance Optimization Testing")
    print("Comparing standard vs optimized scraper performance")
    print("="*70)
    
    # Test configuration
    test_pages = 3  # Small test for quick comparison
    test_url = "https://www.magicbricks.com/flats-in-gurgaon-for-sale-pppfs"
    
    results = {
        "test_config": {
            "pages_tested": test_pages,
            "test_url": test_url,
            "timestamp": datetime.now().isoformat()
        },
        "baseline": {},
        "optimized": {},
        "parallel": {},
        "comparison": {}
    }
    
    # Test 1: Baseline Performance (Standard Scraper)
    print("\n🔄 Test 1: Baseline Performance (Standard Scraper)")
    print("-" * 50)
    
    try:
        # Create temporary config for baseline test
        baseline_config = create_test_config(test_url, performance_enabled=False)
        baseline_scraper = ModernMagicBricksScraper(baseline_config)
        
        start_time = time.time()
        baseline_result = baseline_scraper.scrape_all_pages(start_page=1, max_pages=test_pages)
        baseline_time = time.time() - start_time
        
        results["baseline"] = {
            "total_time": baseline_time,
            "properties_extracted": baseline_result.get('total_properties', 0),
            "pages_processed": baseline_result.get('pages_processed', 0),
            "avg_page_time": baseline_time / test_pages if test_pages > 0 else 0,
            "success": baseline_result.get('success', False)
        }
        
        print(f"✅ Baseline completed in {baseline_time:.1f}s")
        print(f"   📊 Properties: {results['baseline']['properties_extracted']}")
        print(f"   📄 Pages: {results['baseline']['pages_processed']}")
        print(f"   ⏱️  Avg/Page: {results['baseline']['avg_page_time']:.1f}s")
        
        # Cleanup
        if os.path.exists(baseline_config):
            os.remove(baseline_config)
            
    except Exception as e:
        print(f"❌ Baseline test failed: {str(e)}")
        results["baseline"]["error"] = str(e)
    
    # Test 2: Optimized Performance (Browser Optimizations Only)
    print("\n⚡ Test 2: Optimized Performance (Browser Optimizations)")
    print("-" * 50)
    
    try:
        # Create config with optimizations but no parallel processing
        optimized_config = create_test_config(test_url, performance_enabled=True, parallel_enabled=False)
        optimized_scraper = OptimizedMagicBricksScraper(optimized_config)
        
        start_time = time.time()
        optimized_result = optimized_scraper.scrape_all_pages(start_page=1, max_pages=test_pages)
        optimized_time = time.time() - start_time
        
        results["optimized"] = {
            "total_time": optimized_time,
            "properties_extracted": optimized_result.get('total_properties', 0),
            "pages_processed": optimized_result.get('pages_processed', 0),
            "avg_page_time": optimized_time / test_pages if test_pages > 0 else 0,
            "success": optimized_result.get('success', False)
        }
        
        print(f"✅ Optimized completed in {optimized_time:.1f}s")
        print(f"   📊 Properties: {results['optimized']['properties_extracted']}")
        print(f"   📄 Pages: {results['optimized']['pages_processed']}")
        print(f"   ⏱️  Avg/Page: {results['optimized']['avg_page_time']:.1f}s")
        
        # Cleanup
        if os.path.exists(optimized_config):
            os.remove(optimized_config)
            
    except Exception as e:
        print(f"❌ Optimized test failed: {str(e)}")
        results["optimized"]["error"] = str(e)
    
    # Test 3: Parallel Processing Performance
    print("\n🚀 Test 3: Parallel Processing Performance")
    print("-" * 50)
    
    try:
        # Create config with parallel processing enabled
        parallel_config = create_test_config(test_url, performance_enabled=True, parallel_enabled=True)
        parallel_scraper = OptimizedMagicBricksScraper(parallel_config)
        
        start_time = time.time()
        parallel_result = parallel_scraper.scrape_with_parallel_processing(start_page=1, max_pages=test_pages)
        parallel_time = time.time() - start_time
        
        results["parallel"] = {
            "total_time": parallel_time,
            "properties_extracted": parallel_result.get('total_properties', 0),
            "pages_processed": parallel_result.get('pages_processed', 0),
            "avg_page_time": parallel_time / test_pages if test_pages > 0 else 0,
            "success": parallel_result.get('success', False),
            "time_saved": parallel_result.get('time_saved', 0),
            "speed_improvement": parallel_result.get('speed_improvement', '0%')
        }
        
        print(f"✅ Parallel completed in {parallel_time:.1f}s")
        print(f"   📊 Properties: {results['parallel']['properties_extracted']}")
        print(f"   📄 Pages: {results['parallel']['pages_processed']}")
        print(f"   ⏱️  Avg/Page: {results['parallel']['avg_page_time']:.1f}s")
        print(f"   🚀 Speed Improvement: {results['parallel']['speed_improvement']}")
        
        # Cleanup
        if os.path.exists(parallel_config):
            os.remove(parallel_config)
            
    except Exception as e:
        print(f"❌ Parallel test failed: {str(e)}")
        results["parallel"]["error"] = str(e)
    
    # Calculate comparisons
    if "error" not in results["baseline"] and "error" not in results["optimized"]:
        baseline_time = results["baseline"]["total_time"]
        optimized_time = results["optimized"]["total_time"]
        
        results["comparison"]["optimized_vs_baseline"] = {
            "time_saved": baseline_time - optimized_time,
            "speed_improvement": f"{((baseline_time - optimized_time) / baseline_time) * 100:.1f}%",
            "faster": optimized_time < baseline_time
        }
    
    if "error" not in results["baseline"] and "error" not in results["parallel"]:
        baseline_time = results["baseline"]["total_time"]
        parallel_time = results["parallel"]["total_time"]
        
        results["comparison"]["parallel_vs_baseline"] = {
            "time_saved": baseline_time - parallel_time,
            "speed_improvement": f"{((baseline_time - parallel_time) / baseline_time) * 100:.1f}%",
            "faster": parallel_time < baseline_time
        }
    
    # Generate summary report
    print("\n" + "="*70)
    print("📊 PERFORMANCE OPTIMIZATION SUMMARY")
    print("="*70)
    
    if "error" not in results["baseline"]:
        print(f"🔄 Baseline: {results['baseline']['total_time']:.1f}s ({results['baseline']['avg_page_time']:.1f}s/page)")
    
    if "error" not in results["optimized"]:
        print(f"⚡ Optimized: {results['optimized']['total_time']:.1f}s ({results['optimized']['avg_page_time']:.1f}s/page)")
        if "optimized_vs_baseline" in results["comparison"]:
            improvement = results["comparison"]["optimized_vs_baseline"]["speed_improvement"]
            print(f"   📈 Improvement: {improvement}")
    
    if "error" not in results["parallel"]:
        print(f"🚀 Parallel: {results['parallel']['total_time']:.1f}s ({results['parallel']['avg_page_time']:.1f}s/page)")
        if "parallel_vs_baseline" in results["comparison"]:
            improvement = results["comparison"]["parallel_vs_baseline"]["speed_improvement"]
            print(f"   📈 Improvement: {improvement}")
    
    # Save detailed results
    output_file = f"performance_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    print("🎯 Performance Testing Complete!")
    
    return results

def create_test_config(test_url: str, performance_enabled: bool = True, parallel_enabled: bool = False) -> str:
    """Create temporary configuration file for testing"""
    
    # Load base config
    with open("config/scraper_config.json", 'r') as f:
        base_config = json.load(f)
    
    # Update for test
    base_config['website']['base_url'] = test_url
    base_config['performance']['enable_optimization'] = performance_enabled
    base_config['performance']['parallel_processing']['enabled'] = parallel_enabled
    
    # Create temporary config file
    temp_config_path = f"temp_test_config_{int(time.time())}.json"
    with open(temp_config_path, 'w') as f:
        json.dump(base_config, f, indent=2)
    
    return temp_config_path

if __name__ == "__main__":
    print("🚀 Performance Optimization Testing Script")
    print("Testing browser optimizations and parallel processing...")
    print()
    
    try:
        results = test_performance_comparison()
        
        # Determine overall success
        baseline_success = "error" not in results.get("baseline", {})
        optimized_success = "error" not in results.get("optimized", {})
        parallel_success = "error" not in results.get("parallel", {})
        
        if baseline_success and (optimized_success or parallel_success):
            print("\n✅ PERFORMANCE TESTING PASSED!")
            print("🎯 Optimizations show measurable improvements")
        else:
            print("\n⚠️ PERFORMANCE TESTING INCOMPLETE")
            print("📊 Some tests failed - check results for details")
        
        print(f"📄 Check {[f for f in os.listdir('.') if f.startswith('performance_test_results_')][-1]} for detailed analysis")
        
    except Exception as e:
        print(f"❌ Performance testing failed: {str(e)}")
        sys.exit(1)
