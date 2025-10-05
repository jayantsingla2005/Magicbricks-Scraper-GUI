"""
Spot Test A - Basic Navigation Validation
- 1 listing page (Mumbai)
- First 5 individual PDPs only
- Verify [NAVIGATE]/[AFTER-NAV] logs show Magicbricks (no Google redirects)
- Verify no stale-driver errors
- Verify URL sanitization works
"""
import sys, os, time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode

def main():
    print("="*80)
    print("SPOT TEST A - BASIC NAVIGATION VALIDATION")
    print("="*80)
    config = {
        'smart_filtering': True,
        'page_load_strategy': 'eager',
        'block_third_party_resources': True,
        'realistic_headers': True,
        'randomize_viewport': True,
        'concurrent_enabled': False,
        'include_individual_pages': True,
        'max_individual_properties': 5,  # limit PDPs to 5
    }
    scraper = IntegratedMagicBricksScraper(headless=False, custom_config=config)
    start = time.time()
    try:
        res = scraper.scrape_properties_with_incremental(
            city='mumbai',
            mode=ScrapingMode.INCREMENTAL,
            max_pages=1,
            include_individual_pages=True,
            export_formats=[]
        )
        print("[RESULT] Listing phase success:", bool(res))
    except Exception as e:
        print("[ERROR][TEST A]", e)
    finally:
        try:
            scraper.close()
        except Exception:
            pass
    print(f"[DURATION] {time.time()-start:.1f}s")

if __name__ == '__main__':
    main()

