#!/usr/bin/env python3
"""
Functional test for refactored systems
Tests end-to-end functionality with small scraping session
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_small_scraping_session():
    """Test small scraping session (2 pages) to verify refactored code works"""
    
    print("\n" + "="*80)
    print("FUNCTIONAL TEST: Small Scraping Session (2 pages)")
    print("="*80 + "\n")
    
    try:
        # Import the main scraper
        from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
        
        print("✅ Successfully imported IntegratedMagicBricksScraper")
        
        # Initialize scraper with custom config
        custom_config = {
            'city': 'gurgaon',
            'max_pages': 2,
            'include_individual_pages': False
        }

        scraper = IntegratedMagicBricksScraper(
            headless=True,
            incremental_enabled=False,
            custom_config=custom_config
        )

        print("✅ Successfully initialized scraper")
        print(f"   - City: gurgaon")
        print(f"   - Max pages: 2")
        print(f"   - Headless: True")
        print(f"   - Individual pages: False")

        # Run scraping
        print("\n🚀 Starting scraping session...")
        start_time = datetime.now()
        
        results = scraper.scrape()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n✅ Scraping completed in {duration:.2f} seconds")
        
        # Validate results
        if results and len(results) > 0:
            print(f"\n📊 RESULTS:")
            print(f"   - Properties scraped: {len(results)}")
            print(f"   - Average per page: {len(results)/2:.1f}")
            print(f"   - Properties per minute: {(len(results)/duration)*60:.1f}")
            
            # Check first property structure
            first_prop = results[0]
            required_fields = ['title', 'price', 'location', 'property_url']
            missing_fields = [f for f in required_fields if f not in first_prop or not first_prop[f]]
            
            if missing_fields:
                print(f"\n⚠️  WARNING: Missing fields in first property: {missing_fields}")
            else:
                print(f"\n✅ All required fields present in properties")
            
            # Calculate data quality
            total_fields = 0
            filled_fields = 0
            for prop in results:
                for key, value in prop.items():
                    total_fields += 1
                    if value and value != 'N/A' and value != '':
                        filled_fields += 1
            
            quality_score = (filled_fields / total_fields * 100) if total_fields > 0 else 0
            print(f"   - Data quality score: {quality_score:.1f}%")
            
            # Test passed
            print(f"\n{'='*80}")
            print("✅ FUNCTIONAL TEST PASSED")
            print(f"{'='*80}\n")
            return True
            
        else:
            print(f"\n❌ FUNCTIONAL TEST FAILED: No properties scraped")
            return False
            
    except Exception as e:
        print(f"\n❌ FUNCTIONAL TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        try:
            if 'scraper' in locals():
                scraper.close()
                print("✅ Scraper closed successfully")
        except:
            pass


if __name__ == "__main__":
    success = test_small_scraping_session()
    sys.exit(0 if success else 1)

