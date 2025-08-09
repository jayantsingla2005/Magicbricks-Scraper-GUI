#!/usr/bin/env python3
"""
Production Optimization Testing Script
Tests the production-ready optimized scraper for reliable performance improvements.
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
    from src.core.production_optimized_scraper import ProductionOptimizedScraper
except ImportError:
    print("❌ Import error - check module paths")
    sys.exit(1)

def test_production_optimization():
    """Test production-ready optimization improvements"""
    
    print("⚡ Production Optimization Testing")
    print("Testing reliable performance improvements")
    print("="*60)
    
    # Test configuration
    test_pages = 5  # Larger test for better measurement
    test_url = "https://www.magicbricks.com/flats-in-gurgaon-for-sale-pppfs"
    
    results = {
        "test_config": {
            "pages_tested": test_pages,
            "test_url": test_url,
            "timestamp": datetime.now().isoformat()
        },
        "baseline": {},
        "optimized": {},
        "comparison": {}
    }
    
    # Test 1: Baseline Performance
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
    
    # Test 2: Production Optimized Performance
    print("\n⚡ Test 2: Production Optimized Performance")
    print("-" * 50)
    
    try:
        # Create config with optimizations enabled
        optimized_config = create_test_config(test_url, performance_enabled=True)
        optimized_scraper = ProductionOptimizedScraper(optimized_config)
        
        start_time = time.time()
        optimized_result = optimized_scraper.scrape_all_pages_optimized(start_page=1, max_pages=test_pages)
        optimized_time = time.time() - start_time
        
        results["optimized"] = {
            "total_time": optimized_time,
            "properties_extracted": optimized_result.get('total_properties', 0),
            "pages_processed": optimized_result.get('pages_processed', 0),
            "avg_page_time": optimized_time / test_pages if test_pages > 0 else 0,
            "success": optimized_result.get('success', False),
            "time_saved": optimized_result.get('time_saved', 0),
            "improvement_percentage": optimized_result.get('improvement_percentage', '0%')
        }
        
        print(f"✅ Optimized completed in {optimized_time:.1f}s")
        print(f"   📊 Properties: {results['optimized']['properties_extracted']}")
        print(f"   📄 Pages: {results['optimized']['pages_processed']}")
        print(f"   ⏱️  Avg/Page: {results['optimized']['avg_page_time']:.1f}s")
        print(f"   🚀 Improvement: {results['optimized']['improvement_percentage']}")
        
        # Cleanup
        if os.path.exists(optimized_config):
            os.remove(optimized_config)
            
    except Exception as e:
        print(f"❌ Optimized test failed: {str(e)}")
        results["optimized"]["error"] = str(e)
    
    # Calculate comparison
    if "error" not in results["baseline"] and "error" not in results["optimized"]:
        baseline_time = results["baseline"]["total_time"]
        optimized_time = results["optimized"]["total_time"]
        
        time_saved = baseline_time - optimized_time
        improvement = (time_saved / baseline_time) * 100 if baseline_time > 0 else 0
        
        results["comparison"] = {
            "time_saved": time_saved,
            "improvement_percentage": f"{improvement:.1f}%",
            "faster": optimized_time < baseline_time,
            "properties_match": results["baseline"]["properties_extracted"] == results["optimized"]["properties_extracted"]
        }
    
    # Generate summary report
    print("\n" + "="*60)
    print("📊 PRODUCTION OPTIMIZATION SUMMARY")
    print("="*60)
    
    if "error" not in results["baseline"]:
        print(f"🔄 Baseline: {results['baseline']['total_time']:.1f}s ({results['baseline']['avg_page_time']:.1f}s/page)")
    
    if "error" not in results["optimized"]:
        print(f"⚡ Optimized: {results['optimized']['total_time']:.1f}s ({results['optimized']['avg_page_time']:.1f}s/page)")
        if "comparison" in results:
            improvement = results["comparison"]["improvement_percentage"]
            properties_match = results["comparison"]["properties_match"]
            print(f"   📈 Speed Improvement: {improvement}")
            print(f"   ✔️  Data Quality: {'Maintained' if properties_match else 'Changed'}")
    
    # Validate target achievement
    target_improvement = 30  # 30% improvement target
    if "comparison" in results:
        actual_improvement = float(results["comparison"]["improvement_percentage"].replace('%', ''))
        target_met = actual_improvement >= target_improvement
        
        print(f"\n🎯 TARGET ANALYSIS:")
        print(f"   Target: {target_improvement}% improvement")
        print(f"   Actual: {actual_improvement:.1f}% improvement")
        print(f"   Status: {'✅ TARGET MET' if target_met else '⚠️ TARGET NOT MET'}")
    
    # Save detailed results
    output_file = f"production_optimization_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    print("🎯 Production Optimization Testing Complete!")
    
    return results

def create_test_config(test_url: str, performance_enabled: bool = True) -> str:
    """Create temporary configuration file for testing"""
    
    # Load base config
    with open("config/scraper_config.json", 'r') as f:
        base_config = json.load(f)
    
    # Update for test
    base_config['website']['base_url'] = test_url
    base_config['performance']['enable_optimization'] = performance_enabled
    
    # Create temporary config file
    temp_config_path = f"temp_production_config_{int(time.time())}.json"
    with open(temp_config_path, 'w') as f:
        json.dump(base_config, f, indent=2)
    
    return temp_config_path

if __name__ == "__main__":
    print("🚀 Production Optimization Testing Script")
    print("Testing reliable performance improvements...")
    print()
    
    try:
        results = test_production_optimization()
        
        # Determine overall success
        baseline_success = "error" not in results.get("baseline", {})
        optimized_success = "error" not in results.get("optimized", {})
        
        if baseline_success and optimized_success:
            comparison = results.get("comparison", {})
            improvement = float(comparison.get("improvement_percentage", "0%").replace('%', ''))
            properties_match = comparison.get("properties_match", False)
            
            if improvement >= 20 and properties_match:  # 20% minimum improvement with data quality maintained
                print("\n✅ PRODUCTION OPTIMIZATION PASSED!")
                print("🎯 Reliable performance improvements achieved")
            else:
                print("\n⚠️ PRODUCTION OPTIMIZATION NEEDS IMPROVEMENT")
                print("📊 Either insufficient improvement or data quality issues")
        else:
            print("\n❌ PRODUCTION OPTIMIZATION FAILED")
            print("📊 One or more tests failed - check results for details")
        
        print(f"📄 Check results file for detailed analysis")
        
    except Exception as e:
        print(f"❌ Production optimization testing failed: {str(e)}")
        sys.exit(1)
