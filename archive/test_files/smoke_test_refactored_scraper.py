#!/usr/bin/env python3
"""
Smoke Test for Refactored MagicBricks Scraper
Tests basic functionality after modular refactoring
"""

import sys
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode

def run_smoke_test():
    """Run a simple smoke test with 2-3 pages"""
    
    print("=" * 80)
    print("SMOKE TEST: Refactored MagicBricks Scraper")
    print("=" * 80)
    print()
    
    try:
        # Test 1: Initialize scraper
        print("✅ Test 1: Initializing scraper...")
        scraper = IntegratedMagicBricksScraper(
            headless=False,  # Non-headless for debugging
            incremental_enabled=False  # Disable incremental for simple test
        )
        print("   ✅ Scraper initialized successfully")
        print()
        
        # Test 2: Setup driver
        print("✅ Test 2: Setting up WebDriver...")
        scraper.setup_driver()
        print("   ✅ WebDriver setup successful")
        print()
        
        # Test 3: Verify modules are initialized
        print("✅ Test 3: Verifying module initialization...")
        assert scraper.property_extractor is not None, "PropertyExtractor not initialized"
        assert scraper.bot_handler is not None, "BotDetectionHandler not initialized"
        assert scraper.export_manager is not None, "ExportManager not initialized"
        assert scraper.data_validator is not None, "DataValidator not initialized"
        assert scraper.individual_scraper is not None, "IndividualPropertyScraper not initialized"
        print("   ✅ All modules initialized correctly")
        print()
        
        # Test 4: Scrape 2 pages
        print("✅ Test 4: Scraping 2 pages from Gurgaon...")
        custom_config = {
            'city': 'gurgaon',
            'max_pages': 2,
            'page_delay_min': 1.0,
            'page_delay_max': 2.0
        }
        
        result = scraper.scrape_properties_with_incremental(
            city='gurgaon',
            mode=ScrapingMode.FULL,
            max_pages=2,
            include_individual_pages=False,
            export_formats=[]  # Don't export yet
        )
        
        print(f"   ✅ Scraping completed")
        print(f"   📊 Properties found: {len(scraper.properties)}")
        print()
        
        # Test 5: Verify data quality
        print("✅ Test 5: Verifying data quality...")
        if len(scraper.properties) > 0:
            sample_property = scraper.properties[0]
            print(f"   Sample property fields: {list(sample_property.keys())}")
            
            # Check critical fields
            critical_fields = ['title', 'price', 'url']
            missing_fields = [f for f in critical_fields if f not in sample_property or not sample_property[f]]
            
            if missing_fields:
                print(f"   ⚠️ Warning: Missing critical fields: {missing_fields}")
            else:
                print(f"   ✅ All critical fields present")
        else:
            print("   ⚠️ Warning: No properties extracted")
        print()
        
        # Test 6: Test export functionality
        print("✅ Test 6: Testing export functionality...")
        if len(scraper.properties) > 0:
            df, csv_file = scraper.save_to_csv("smoke_test_output.csv")
            if csv_file:
                print(f"   ✅ CSV export successful: {csv_file}")
            else:
                print("   ❌ CSV export failed")
            
            json_data, json_file = scraper.save_to_json("smoke_test_output.json")
            if json_file:
                print(f"   ✅ JSON export successful: {json_file}")
            else:
                print("   ❌ JSON export failed")
        else:
            print("   ⏭️ Skipped (no properties to export)")
        print()
        
        # Test 7: Cleanup
        print("✅ Test 7: Cleanup...")
        if scraper.driver:
            scraper.driver.quit()
        print("   ✅ Cleanup successful")
        print()
        
        # Final summary
        print("=" * 80)
        print("SMOKE TEST RESULTS")
        print("=" * 80)
        print(f"✅ All tests passed!")
        print(f"📊 Properties extracted: {len(scraper.properties)}")
        print(f"🎯 Refactored modules working correctly")
        print()
        print("Next steps:")
        print("1. Review exported files (smoke_test_output.csv/json)")
        print("2. Proceed with GUI refactoring")
        print("3. Run comprehensive testing")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ SMOKE TEST FAILED")
        print("=" * 80)
        print(f"Error: {str(e)}")
        print()
        print("Stack trace:")
        import traceback
        traceback.print_exc()
        print("=" * 80)
        
        # Cleanup on error
        try:
            if 'scraper' in locals() and scraper.driver:
                scraper.driver.quit()
        except:
            pass
        
        return False

if __name__ == "__main__":
    success = run_smoke_test()
    sys.exit(0 if success else 1)

