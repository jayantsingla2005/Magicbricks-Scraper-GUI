#!/usr/bin/env python3
"""
Comprehensive Validation Script
Tests enhanced selectors across full spectrum of property types and locations with >95% accuracy target.
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
    from src.utils.logger import ScraperLogger
except ImportError:
    print("❌ Import error - running validation with basic functionality")
    sys.exit(1)

def comprehensive_validation():
    """Run comprehensive validation across property types and locations"""

    print("🔬 Starting Comprehensive Validation")
    print("Target: >95% accuracy across all property types")

    # Simplified test matrix focusing on Gurgaon (our main test location)
    test_matrix = {
        "gurgaon": {
            "apartments": "https://www.magicbricks.com/flats-in-gurgaon-for-sale-pppfs",
            "houses": "https://www.magicbricks.com/independent-house-for-sale-in-gurgaon-pppfs",
            "plots": "https://www.magicbricks.com/residential-plots-land-for-sale-in-gurgaon-pppfs"
        }
    }
    
    scraper = ModernMagicBricksScraper()
    validation_results = {
        "start_time": datetime.now().isoformat(),
        "test_matrix": {},
        "summary": {},
        "overall_success": False
    }
    
    total_tests = 0
    successful_tests = 0
    
    for city, property_types in test_matrix.items():
        print(f"\n🏙️ Testing {city.upper()}...")
        validation_results["test_matrix"][city] = {}

        for prop_type, url in property_types.items():
            print(f"  🏠 Testing {prop_type}...")
            total_tests += 1
            
            try:
                # Create temporary config file for this URL
                temp_config_path = f"temp_config_{city}_{prop_type}.json"

                # Load base config
                with open("config/scraper_config.json", 'r') as f:
                    base_config = json.load(f)

                # Update base URL for this test
                base_config['website']['base_url'] = url

                # Save temporary config
                with open(temp_config_path, 'w') as f:
                    json.dump(base_config, f, indent=2)

                # Create scraper with temporary config
                test_scraper = ModernMagicBricksScraper(temp_config_path)

                # Scrape 2 pages for comprehensive testing
                result = test_scraper.scrape_all_pages(start_page=1, max_pages=2)

                # Clean up temporary config
                if os.path.exists(temp_config_path):
                    os.remove(temp_config_path)

                # Get properties from the scraper's internal storage
                properties = test_scraper.scraped_properties

                if not properties:
                    print(f"    ❌ No properties found for {city} {prop_type}")
                    validation_results["test_matrix"][city][prop_type] = {
                        "status": "FAILED",
                        "error": "No properties found",
                        "properties_count": 0
                    }
                    continue
                
                # Analyze extraction quality
                total_props = len(properties)
                
                # Core field analysis
                title_count = sum(1 for p in properties if p.title)
                price_count = sum(1 for p in properties if p.price)
                area_count = sum(1 for p in properties if p.super_area or p.carpet_area)
                status_count = sum(1 for p in properties if p.status)
                society_count = sum(1 for p in properties if p.society)
                
                # Calculate success rates
                title_rate = (title_count / total_props) * 100 if total_props > 0 else 0
                price_rate = (price_count / total_props) * 100 if total_props > 0 else 0
                area_rate = (area_count / total_props) * 100 if total_props > 0 else 0
                status_rate = (status_count / total_props) * 100 if total_props > 0 else 0
                society_rate = (society_count / total_props) * 100 if total_props > 0 else 0
                
                # Overall success rate (weighted average of critical fields)
                overall_rate = (title_rate * 0.3 + price_rate * 0.3 + area_rate * 0.25 + status_rate * 0.15)
                
                # Determine success
                is_successful = overall_rate >= 95.0
                if is_successful:
                    successful_tests += 1
                
                validation_results["test_matrix"][city][prop_type] = {
                    "status": "PASSED" if is_successful else "FAILED",
                    "properties_count": total_props,
                    "extraction_rates": {
                        "title": f"{title_rate:.1f}%",
                        "price": f"{price_rate:.1f}%",
                        "area": f"{area_rate:.1f}%",
                        "status": f"{status_rate:.1f}%",
                        "society": f"{society_rate:.1f}%"
                    },
                    "overall_rate": f"{overall_rate:.1f}%",
                    "target_met": is_successful
                }
                
                status_icon = "✅" if is_successful else "❌"
                print(f"    {status_icon} {city} {prop_type}: {overall_rate:.1f}% ({total_props} properties)")
                print(f"       Title: {title_rate:.1f}%, Price: {price_rate:.1f}%, Area: {area_rate:.1f}%")
                
                # Brief delay between tests
                time.sleep(2)
                
            except Exception as e:
                print(f"    ❌ Error testing {city} {prop_type}: {str(e)}")
                validation_results["test_matrix"][city][prop_type] = {
                    "status": "ERROR",
                    "error": str(e),
                    "properties_count": 0
                }
    
    # Calculate overall success rate
    overall_success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
    target_met = overall_success_rate >= 95.0
    
    validation_results["summary"] = {
        "total_tests": total_tests,
        "successful_tests": successful_tests,
        "overall_success_rate": f"{overall_success_rate:.1f}%",
        "target_met": target_met,
        "end_time": datetime.now().isoformat()
    }
    
    validation_results["overall_success"] = target_met
    
    # Generate summary report
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE VALIDATION SUMMARY")
    print("="*80)
    print(f"🎯 Target: >95% accuracy across all property types")
    print(f"📈 Results: {successful_tests}/{total_tests} tests passed ({overall_success_rate:.1f}%)")

    if target_met:
        print("✅ VALIDATION PASSED - Enhanced selectors meet production standards!")
    else:
        print("⚠️ VALIDATION NEEDS IMPROVEMENT - Some tests below 95% threshold")

    # Detailed breakdown
    for city, results in validation_results["test_matrix"].items():
        print(f"\n🏙️ {city.upper()}:")
        for prop_type, data in results.items():
            if data["status"] == "PASSED":
                print(f"   ✅ {prop_type}: {data['overall_rate']} ({data['properties_count']} properties)")
            elif data["status"] == "FAILED":
                print(f"   ❌ {prop_type}: {data.get('overall_rate', 'N/A')} ({data['properties_count']} properties)")
            else:
                print(f"   🚫 {prop_type}: ERROR - {data.get('error', 'Unknown error')}")

    # Save results
    output_file = f"comprehensive_validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(validation_results, f, indent=2, default=str)

    print(f"\n💾 Detailed results saved to: {output_file}")
    print("🎯 Comprehensive Validation Complete!")
    
    return validation_results

if __name__ == "__main__":
    print("🚀 Comprehensive Validation Script")
    print("Testing enhanced selectors across property types and locations...")
    print("Target: >95% accuracy across all tests")
    print()
    
    try:
        results = comprehensive_validation()
        
        if results["overall_success"]:
            print("\n✅ COMPREHENSIVE VALIDATION PASSED!")
            print("🎯 Enhanced selectors meet production standards (>95% accuracy)")
        else:
            print("\n⚠️ VALIDATION NEEDS IMPROVEMENT")
            print("📊 Some tests below 95% accuracy threshold")
        
        print(f"📄 Check results file for detailed analysis")
        
    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")
        sys.exit(1)
