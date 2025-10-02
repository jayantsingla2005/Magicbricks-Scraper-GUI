#!/usr/bin/env python3
"""
Multi-City Deep Testing Script
Tests 5 diverse cities with 100 pages each to validate production readiness
and Phase 4 Priority 1 improvements (status and area extraction)
"""

import time
import json
from datetime import datetime
from pathlib import Path
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode

def run_multi_city_deep_test():
    """Run comprehensive multi-city testing"""
    
    print("="*80)
    print("MULTI-CITY DEEP TESTING")
    print("="*80)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Scope: 5 cities × 100 pages = ~15,000 properties")
    print(f"Mode: Listing pages only (fast, efficient)")
    print("="*80)
    print()
    
    # Test configuration
    cities_to_test = [
        'gurgaon',    # Metro, high volume
        'mumbai',     # Metro, high volume
        'bangalore',  # Metro, high volume
        'pune',       # Tier 1, medium volume
        'hyderabad'   # Tier 1, medium volume
    ]
    
    test_config = {
        'mode': ScrapingMode.FULL,
        'max_pages': 100,
        'headless': True,
        'incremental_enabled': False,
        'individual_pages': False,  # Listing pages only
        'export_formats': ['csv', 'json']
    }
    
    print("[CONFIG] Test Configuration:")
    print(f"   Cities: {', '.join(cities_to_test)}")
    print(f"   Pages per city: {test_config['max_pages']}")
    print(f"   Mode: {test_config['mode']}")
    print(f"   Individual pages: {test_config['individual_pages']}")
    print(f"   Export formats: {test_config['export_formats']}")
    print()
    
    # Results storage
    all_results = {
        'test_date': datetime.now().isoformat(),
        'configuration': test_config,
        'cities': {},
        'summary': {}
    }
    
    overall_start_time = time.time()
    
    # Test each city sequentially
    for city_index, city in enumerate(cities_to_test, 1):
        print("="*80)
        print(f"TESTING CITY {city_index}/5: {city.upper()}")
        print("="*80)
        print()
        
        city_start_time = time.time()
        
        try:
            # Initialize scraper for this city
            print(f"[INIT] Initializing scraper for {city}...")
            scraper = IntegratedMagicBricksScraper(
                headless=test_config['headless'],
                incremental_enabled=test_config['incremental_enabled']
            )
            
            # Run scraping
            print(f"[START] Starting scraping for {city}...")
            print()
            
            result = scraper.scrape_properties_with_incremental(
                city=city,
                mode=test_config['mode'],
                max_pages=test_config['max_pages'],
                include_individual_pages=test_config['individual_pages'],
                export_formats=test_config['export_formats']
            )
            
            # Calculate metrics
            city_end_time = time.time()
            city_duration = city_end_time - city_start_time
            city_duration_minutes = city_duration / 60
            
            # Get properties
            properties = scraper.properties
            total_properties = len(properties)
            
            print()
            print("="*80)
            print(f"CITY RESULTS: {city.upper()}")
            print("="*80)
            print(f"Duration: {city_duration_minutes:.2f} minutes ({city_duration:.1f} seconds)")
            print(f"Total Properties: {total_properties}")
            print(f"Pages Scraped: {test_config['max_pages']}")
            print(f"Properties/Page: {total_properties / test_config['max_pages']:.1f}")
            print(f"Properties/Minute: {total_properties / city_duration_minutes:.1f}")
            print()
            
            # Analyze field completeness
            print("-"*80)
            print("FIELD COMPLETENESS ANALYSIS")
            print("-"*80)
            
            if total_properties > 0:
                fields_to_check = [
                    'title', 'price', 'area', 'locality', 'property_type',
                    'status', 'bathrooms', 'balcony', 'furnishing',
                    'carpet_area', 'builtup_area', 'super_area', 'plot_area'
                ]
                
                field_stats = {}
                for field in fields_to_check:
                    count = sum(1 for p in properties if p.get(field) and p.get(field) != 'N/A')
                    percentage = (count / total_properties) * 100
                    field_stats[field] = {
                        'count': count,
                        'percentage': percentage
                    }
                    print(f"{field:15s}: {count:4d}/{total_properties:4d} ({percentage:5.1f}%)")
                
                # Calculate overall completeness
                total_percentage = sum(stats['percentage'] for stats in field_stats.values())
                avg_completeness = total_percentage / len(fields_to_check)
                print()
                print(f"{'AVERAGE':15s}: {avg_completeness:5.1f}%")
                print()
                
                # Store city results
                all_results['cities'][city] = {
                    'total_properties': total_properties,
                    'pages_scraped': test_config['max_pages'],
                    'duration_minutes': city_duration_minutes,
                    'properties_per_minute': total_properties / city_duration_minutes,
                    'avg_completeness': avg_completeness,
                    'field_stats': field_stats,
                    'success': True
                }
                
            else:
                print("❌ NO PROPERTIES EXTRACTED")
                all_results['cities'][city] = {
                    'success': False,
                    'error': 'No properties extracted'
                }
            
            # Cleanup
            if scraper.driver:
                scraper.driver.quit()
            
            print()
            print(f"✅ {city.upper()} COMPLETE")
            print()
            
        except Exception as e:
            print(f"❌ ERROR testing {city}: {str(e)}")
            all_results['cities'][city] = {
                'success': False,
                'error': str(e)
            }
            import traceback
            traceback.print_exc()
    
    # Calculate overall summary
    overall_end_time = time.time()
    overall_duration = overall_end_time - overall_start_time
    overall_duration_minutes = overall_duration / 60
    
    print("="*80)
    print("OVERALL SUMMARY")
    print("="*80)
    print(f"Total Duration: {overall_duration_minutes:.2f} minutes ({overall_duration/3600:.2f} hours)")
    print(f"Cities Tested: {len(cities_to_test)}")
    print()
    
    # Aggregate statistics
    successful_cities = [city for city, data in all_results['cities'].items() if data.get('success')]
    total_properties_all = sum(data.get('total_properties', 0) for data in all_results['cities'].values() if data.get('success'))
    avg_completeness_all = sum(data.get('avg_completeness', 0) for data in all_results['cities'].values() if data.get('success')) / len(successful_cities) if successful_cities else 0
    
    print(f"Successful Cities: {len(successful_cities)}/{len(cities_to_test)}")
    print(f"Total Properties: {total_properties_all}")
    print(f"Average Completeness: {avg_completeness_all:.1f}%")
    print(f"Overall Properties/Minute: {total_properties_all / overall_duration_minutes:.1f}")
    print()
    
    # Store summary
    all_results['summary'] = {
        'total_duration_minutes': overall_duration_minutes,
        'cities_tested': len(cities_to_test),
        'successful_cities': len(successful_cities),
        'total_properties': total_properties_all,
        'avg_completeness': avg_completeness_all,
        'overall_properties_per_minute': total_properties_all / overall_duration_minutes
    }
    
    # Save detailed report
    report_file = f"multi_city_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"[SAVE] Detailed report saved to: {report_file}")
    print()
    
    # Final assessment
    print("="*80)
    print("FINAL ASSESSMENT")
    print("="*80)
    
    if len(successful_cities) == len(cities_to_test):
        print("✅ ALL CITIES TESTED SUCCESSFULLY")
    else:
        print(f"⚠️ {len(cities_to_test) - len(successful_cities)} CITIES FAILED")
    
    print(f"Field Completeness: {avg_completeness_all:.1f}%")
    print(f"Total Properties: {total_properties_all}")
    print(f"Performance: {total_properties_all / overall_duration_minutes:.1f} properties/minute")
    print()
    
    if avg_completeness_all >= 90:
        print("✅ EXCELLENT - Field completeness target achieved (90%+)")
    elif avg_completeness_all >= 85:
        print("✅ GOOD - Field completeness acceptable (85%+)")
    else:
        print("⚠️ NEEDS IMPROVEMENT - Field completeness below target")
    
    print()
    print("="*80)
    print("TEST COMPLETE")
    print("="*80)
    
    return all_results

if __name__ == "__main__":
    run_multi_city_deep_test()

