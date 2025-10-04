#!/usr/bin/env python3
"""
Short Validation Test: Verify driver restart fix works correctly
1 city (Mumbai), 10 pages, incremental mode, headful, with individual property pages enabled.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.join(__file__, '..'))))
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode


def main():
    print("[SHORT-TEST] Starting Mumbai (10 pages) :: mode=INCREMENTAL, include_individual_pages=True, headful")
    print("[SHORT-TEST] Purpose: Verify driver restart fix resolves connection-refused errors")
    
    scraper = IntegratedMagicBricksScraper(headless=False, incremental_enabled=True)
    try:
        res = scraper.scrape_properties_with_incremental(
            city='mumbai',
            mode=ScrapingMode.INCREMENTAL,
            max_pages=10,
            include_individual_pages=True,
            export_formats=['csv']
        )
        print(f"\n[RESULT] success={res.get('success')} pages={res.get('pages_scraped')} props_found={res.get('properties_found')} props_saved={res.get('properties_saved')}")
        print(f"[RESULT] individual_urls_identified={res.get('individual_urls_identified', 0)} individual_properties_scraped={res.get('individual_properties_scraped', 0)}")
        
        if res.get('success'):
            print("\n✅ [SHORT-TEST] PASSED - No catastrophic failures")
        else:
            print("\n❌ [SHORT-TEST] FAILED - Check logs for errors")
            
        return res
    finally:
        try:
            scraper.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()

