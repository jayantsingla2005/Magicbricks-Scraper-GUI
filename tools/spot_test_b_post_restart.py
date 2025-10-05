"""
Spot Test B - Post-Restart Navigation
- Fetch 1 listing page (Mumbai), collect first 6 PDP URLs
- Scrape first 3 PDPs
- Force a driver restart
- Scrape next 3 PDPs
- Verify session ID changes and navigation continues successfully
"""
import sys, os, time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode

def main():
    print("="*80)
    print("SPOT TEST B - POST-RESTART NAVIGATION")
    print("="*80)
    config = {
        'smart_filtering': True,
        'page_load_strategy': 'eager',
        'block_third_party_resources': True,
        'realistic_headers': True,
        'randomize_viewport': True,
        'concurrent_enabled': False,
    }
    scraper = IntegratedMagicBricksScraper(headless=False, custom_config=config)

    def get_session():
        try:
            return getattr(scraper.driver, 'session_id', 'unknown')
        except Exception:
            return 'unknown'

    start = time.time()
    try:
        # Run listing phase only to populate properties
        res = scraper.scrape_properties_with_incremental(
            city='mumbai',
            mode=ScrapingMode.INCREMENTAL,
            max_pages=1,
            include_individual_pages=False,
            export_formats=[]
        )
        props = getattr(scraper, 'properties', []) or []
        urls = [p.get('property_url') for p in props if p.get('property_url')][:6]
        print(f"[INFO] Collected {len(urls)} PDP URLs from first page")
        if not urls:
            print("[WARN] No URLs collected; aborting Test B")
            return
        # Set referer to base page
        listing_referer = scraper.base_url if hasattr(scraper, 'base_url') else 'https://www.magicbricks.com/property-for-sale-in-mumbai-pppfs'
        scraper.individual_scraper.set_listing_page_url(listing_referer)

        before_session = get_session()
        print(f"[SESSION][BEFORE] {before_session}")

        # Scrape first 3
        print("[STEP] Scraping first 3 PDPs...")
        scraper.scrape_individual_property_pages(urls[:3], batch_size=3, force_rescrape=True)

        # Force restart
        print("[STEP] Forcing driver restart...")
        scraper._restart_browser_session()

        after_session = get_session()
        print(f"[SESSION][AFTER]  {after_session}")

        # Scrape next 3 using new session
        print("[STEP] Scraping next 3 PDPs after restart...")
        scraper.scrape_individual_property_pages(urls[3:6], batch_size=3, force_rescrape=True)

        print("[RESULT] Test B completed")
    except Exception as e:
        print("[ERROR][TEST B]", e)
    finally:
        try:
            scraper.close()
        except Exception:
            pass
    print(f"[DURATION] {time.time()-start:.1f}s")

if __name__ == '__main__':
    main()

