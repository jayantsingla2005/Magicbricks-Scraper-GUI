#!/usr/bin/env python3
"""
Test script to investigate property exclusions
Runs a small scrape with debug logging to see excluded properties
"""

import sys
import os
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper, ScrapingMode

def test_property_exclusions():
    """
    Run a small test scrape to see what properties are being excluded
    """
    print("🔍 Testing property exclusions with debug logging...")
    print("=" * 60)
    
    # Initialize scraper with debug logging enabled
    scraper = IntegratedMagicBricksScraper(
        headless=True,
        incremental_enabled=False
    )
    
    try:
        # Run a small scrape - just 2 pages to see exclusions
        print("📊 Running test scrape (2 pages max)...")
        
        result = scraper.scrape_properties_with_incremental(
            city="gurgaon",
            max_pages=2,  # Only 2 pages for testing
            mode=ScrapingMode.FULL,
            export_formats=['csv'],
            include_individual_pages=False
        )
        
        if result['success']:
            print("\n✅ Test scrape completed successfully!")
            print(f"📊 Results:")
            print(f"   - Pages scraped: {result.get('pages_scraped', 0)}")
            print(f"   - Properties found: {result.get('properties_found', 0)}")
            print(f"   - Properties saved: {result.get('properties_saved', 0)}")
            
            # Check filter stats if available
            if hasattr(scraper, '_filter_stats'):
                stats = scraper.get_filtered_properties_count()
                print(f"\n🔍 Filter Statistics:")
                print(f"   - Total processed: {stats.get('total', 0)}")
                print(f"   - Passed filters: {stats.get('filtered', 0)}")
                print(f"   - Excluded by filters: {stats.get('excluded', 0)}")
                
                if stats.get('excluded', 0) > 0:
                    exclusion_rate = (stats['excluded'] / stats['total']) * 100
                    print(f"   - Exclusion rate: {exclusion_rate:.1f}%")
            
            print(f"\n📁 Output file: {result.get('output_file', 'N/A')}")
            print("\n💡 Check the 'integrated_scraper.log' file for detailed debug messages about excluded properties.")
            
        else:
            print(f"❌ Test scrape failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        
    finally:
        # Clean up
        try:
            scraper.close()
        except:
            pass
    
    print("\n" + "=" * 60)
    print("🔍 Test completed. Check the log file for exclusion details.")

if __name__ == "__main__":
    test_property_exclusions()