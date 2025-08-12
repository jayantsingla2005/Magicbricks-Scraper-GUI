#!/usr/bin/env python3
"""
Test script to verify the full scraper works with updated selectors
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper

def test_full_scraper():
    """Test the full scraper with a small run"""
    
    print("🧪 Testing Full Scraper with Updated Selectors")
    print("=" * 60)
    
    try:
        # Initialize scraper with non-headless mode for debugging
        scraper = IntegratedMagicBricksScraper(
            headless=False,  # Keep browser visible for debugging
            incremental_enabled=False  # Disable incremental for testing
        )
        
        print("✅ Scraper initialized successfully")
        
        # Test with a small configuration
        test_config = {
            'cities': ['gurgaon'],  # Single city
            'max_pages': 2,  # Only 2 pages
            'delay_range': [2, 4],  # Reasonable delays
            'output_directory': 'test_output',
            'output_filename': f'test_scrape_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        }
        
        print(f"🎯 Test configuration: {test_config}")
        
        # Run the scraper
        print("\n🚀 Starting test scrape...")
        from user_mode_options import ScrapingMode
        
        results = scraper.scrape_properties_with_incremental(
            city='gurgaon',
            mode=ScrapingMode.FULL,
            max_pages=2
        )
        
        print("\n📊 Test Results:")
        print(f"  Success: {results.get('success', False)}")
        print(f"  Total Properties: {results.get('total_properties', 0)}")
        print(f"  Pages Scraped: {results.get('pages_scraped', 0)}")
        print(f"  Output File: {results.get('output_file', 'N/A')}")
        
        if results.get('success') and results.get('total_properties', 0) > 0:
            print("\n✅ TEST PASSED: Scraper working correctly with updated selectors!")
            
            # Show some sample properties
            if hasattr(scraper, 'properties') and scraper.properties:
                print("\n📋 Sample Properties:")
                for i, prop in enumerate(scraper.properties[:3]):
                    print(f"  {i+1}. {prop.get('title', 'N/A')[:50]}...")
                    print(f"     Price: {prop.get('price', 'N/A')}")
                    print(f"     Area: {prop.get('area', 'N/A')}")
                    print(f"     URL: {prop.get('property_url', 'N/A')[:60]}...")
                    print()
        else:
            print("\n❌ TEST FAILED: No properties scraped")
            if 'error' in results:
                print(f"   Error: {results['error']}")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: Exception occurred")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        try:
            if 'scraper' in locals():
                scraper.close()
                print("\n🧹 Scraper closed successfully")
        except:
            pass
    
    print("\n" + "=" * 60)
    print("✅ Full scraper test completed")

if __name__ == "__main__":
    test_full_scraper()
    print("\n🎉 Test script finished!")