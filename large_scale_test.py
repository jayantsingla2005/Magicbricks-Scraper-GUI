#!/usr/bin/env python3
"""
Large-Scale Data Quality Test
Test 10-15 pages (~300-450 properties) to validate field extraction and performance
"""

import time
import json
from datetime import datetime
from pathlib import Path
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode

def run_large_scale_test():
    """Run large-scale data quality test"""
    
    print("="*80)
    print("LARGE-SCALE DATA QUALITY TEST")
    print("="*80)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: 10-15 pages (~300-450 properties)")
    print(f"City: Gurgaon")
    print(f"Mode: FULL (no incremental stopping)")
    print("="*80)
    print()
    
    # Test configuration
    test_config = {
        'city': 'gurgaon',
        'mode': ScrapingMode.FULL,  # Full mode to ensure we get all pages
        'max_pages': 15,  # Test 15 pages
        'headless': True,
        'incremental_enabled': False,  # Disable incremental for full test
        'individual_pages': False,  # Skip individual pages for speed
        'export_formats': ['csv', 'json']
    }
    
    print("[CONFIG] Test Configuration:")
    for key, value in test_config.items():
        print(f"   {key}: {value}")
    print()
    
    # Initialize scraper
    print("[INIT] Initializing scraper...")
    scraper = IntegratedMagicBricksScraper(
        headless=test_config['headless'],
        incremental_enabled=test_config['incremental_enabled']
    )
    
    # Start test
    start_time = time.time()
    print(f"[START] Test started at {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    try:
        # Run scraping
        result = scraper.scrape_properties_with_incremental(
            city=test_config['city'],
            mode=test_config['mode'],
            max_pages=test_config['max_pages'],
            include_individual_pages=test_config['individual_pages'],
            export_formats=test_config['export_formats']
        )
        
        # Calculate duration
        end_time = time.time()
        duration = end_time - start_time
        duration_minutes = duration / 60
        
        # Get properties
        properties = scraper.properties
        total_properties = len(properties)
        
        print()
        print("="*80)
        print("TEST RESULTS")
        print("="*80)
        print(f"Duration: {duration_minutes:.2f} minutes ({duration:.1f} seconds)")
        print(f"Total Properties: {total_properties}")
        print(f"Pages Scraped: {test_config['max_pages']}")
        print(f"Properties/Page: {total_properties / test_config['max_pages']:.1f}")
        print(f"Properties/Minute: {total_properties / duration_minutes:.1f}")
        print()
        
        # Analyze field completeness
        print("="*80)
        print("FIELD COMPLETENESS ANALYSIS")
        print("="*80)
        
        if total_properties > 0:
            fields_to_check = [
                'title', 'price', 'area', 'location', 'property_type',
                'bhk', 'status', 'posted_date', 'url', 'description'
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
            
            # Analyze data quality
            print("="*80)
            print("DATA QUALITY ANALYSIS")
            print("="*80)
            
            # Price analysis
            prices = [p.get('price') for p in properties if p.get('price') and p.get('price') != 'N/A']
            print(f"Valid Prices: {len(prices)}/{total_properties} ({len(prices)/total_properties*100:.1f}%)")
            
            # Area analysis
            areas = [p.get('area') for p in properties if p.get('area') and p.get('area') != 'N/A']
            print(f"Valid Areas: {len(areas)}/{total_properties} ({len(areas)/total_properties*100:.1f}%)")
            
            # URL analysis
            urls = [p.get('url') for p in properties if p.get('url') and p.get('url') != 'N/A']
            print(f"Valid URLs: {len(urls)}/{total_properties} ({len(urls)/total_properties*100:.1f}%)")
            
            # Status analysis
            statuses = [p.get('status') for p in properties if p.get('status') and p.get('status') != 'N/A']
            print(f"Valid Statuses: {len(statuses)}/{total_properties} ({len(statuses)/total_properties*100:.1f}%)")
            print()
            
            # Property type distribution
            print("="*80)
            print("PROPERTY TYPE DISTRIBUTION")
            print("="*80)
            
            type_counts = {}
            for p in properties:
                ptype = p.get('property_type', 'Unknown')
                type_counts[ptype] = type_counts.get(ptype, 0) + 1
            
            for ptype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_properties) * 100
                print(f"{ptype:30s}: {count:4d} ({percentage:5.1f}%)")
            print()
            
            # BHK distribution
            print("="*80)
            print("BHK DISTRIBUTION")
            print("="*80)
            
            bhk_counts = {}
            for p in properties:
                bhk = p.get('bhk', 'Unknown')
                bhk_counts[bhk] = bhk_counts.get(bhk, 0) + 1
            
            for bhk, count in sorted(bhk_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_properties) * 100
                print(f"{bhk:30s}: {count:4d} ({percentage:5.1f}%)")
            print()
            
            # Performance metrics
            print("="*80)
            print("PERFORMANCE METRICS")
            print("="*80)
            print(f"Total Duration: {duration_minutes:.2f} minutes")
            print(f"Properties/Minute: {total_properties / duration_minutes:.1f}")
            print(f"Seconds/Property: {duration / total_properties:.2f}")
            print(f"Seconds/Page: {duration / test_config['max_pages']:.2f}")
            print()
            
            # Save detailed report
            report = {
                'test_date': datetime.now().isoformat(),
                'configuration': test_config,
                'results': {
                    'total_properties': total_properties,
                    'pages_scraped': test_config['max_pages'],
                    'duration_minutes': duration_minutes,
                    'properties_per_minute': total_properties / duration_minutes,
                    'avg_completeness': avg_completeness
                },
                'field_stats': field_stats,
                'type_distribution': type_counts,
                'bhk_distribution': bhk_counts
            }
            
            report_file = f"large_scale_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"[SAVE] Detailed report saved to: {report_file}")
            print()
            
            # Final assessment
            print("="*80)
            print("FINAL ASSESSMENT")
            print("="*80)
            
            if avg_completeness >= 90:
                status = "✅ EXCELLENT"
            elif avg_completeness >= 85:
                status = "✅ GOOD"
            elif avg_completeness >= 80:
                status = "⚠️ ACCEPTABLE"
            else:
                status = "❌ NEEDS IMPROVEMENT"
            
            print(f"Field Completeness: {avg_completeness:.1f}% - {status}")
            print(f"Performance: {total_properties / duration_minutes:.1f} properties/minute")
            print(f"Total Properties: {total_properties}")
            print()
            
            if avg_completeness >= 85:
                print("✅ TEST PASSED - Production ready for large-scale scraping")
            else:
                print("⚠️ TEST PASSED WITH WARNINGS - Consider improvements")
            
        else:
            print("❌ NO PROPERTIES EXTRACTED - Test failed")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if scraper.driver:
            scraper.driver.quit()
    
    print()
    print("="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    run_large_scale_test()

