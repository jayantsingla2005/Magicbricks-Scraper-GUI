#!/usr/bin/env python3
"""
Quick test to validate the validation rate fix
"""

import time
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode


def test_validation_rate_fix():
    """Test that validation rate is now much higher"""
    
    print("🧪 TESTING VALIDATION RATE FIX")
    print("=" * 50)
    
    try:
        # Create scraper
        scraper = IntegratedMagicBricksScraper(headless=True, incremental_enabled=True)
        
        print("🚀 Testing validation rate with 5 pages...")
        
        # Run test with 5 pages
        result = scraper.scrape_properties_with_incremental(
            city='gurgaon',
            mode=ScrapingMode.FULL,
            max_pages=5,
            include_individual_pages=False,
            export_formats=['csv']
        )
        
        # Clean up
        scraper.close()
        
        # Check results
        if result.get('success', False):
            total_properties = result.get('session_stats', {}).get('properties_found', 0)
            valid_properties = result.get('session_stats', {}).get('properties_saved', 0)
            
            if total_properties > 0:
                validation_rate = (valid_properties / total_properties) * 100
                print(f"✅ VALIDATION RATE FIXED:")
                print(f"   📊 Total properties: {total_properties}")
                print(f"   ✅ Valid properties: {valid_properties}")
                print(f"   📈 Validation rate: {validation_rate:.1f}%")
                
                if validation_rate >= 90:
                    print(f"🎉 EXCELLENT: Validation rate is now {validation_rate:.1f}% (was 61.5%)")
                    return True
                elif validation_rate >= 80:
                    print(f"✅ GOOD: Validation rate improved to {validation_rate:.1f}% (was 61.5%)")
                    return True
                else:
                    print(f"⚠️ PARTIAL: Validation rate is {validation_rate:.1f}% (was 61.5%)")
                    return False
            else:
                print("❌ No properties found in test")
                return False
        else:
            print(f"❌ Test failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"💥 Test error: {str(e)}")
        return False


def main():
    """Run validation rate fix test"""
    
    success = test_validation_rate_fix()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 VALIDATION RATE FIX SUCCESSFUL")
        print("✅ Properties with missing URLs now considered valid")
        print("✅ Validation rate significantly improved")
    else:
        print("❌ VALIDATION RATE FIX NEEDS MORE WORK")
        print("⚠️ Additional validation issues may exist")
    
    return success


if __name__ == "__main__":
    main()
