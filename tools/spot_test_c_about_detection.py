"""
Spot Test C - Bot Detection Recovery on 'About Magicbricks' Content
- Scrape 3-5 historically-problematic PDP URLs (may serve About-page content)
- Verify detection triggers and recovery actions occur; scraper continues
"""
import sys, os, time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper

PROBLEM_URLS = [
    # Representative URLs from prior logs (Santacruz/Goregaon cluster)
    "https://www.magicbricks.com/aspen-park-goregaon-east-mumbai-pdpid-4d4235303838363733",
    "https://www.magicbricks.com/kamala-natraj-santacruz-east-mumbai-pdpid-4d4235303635303535",
    "https://www.magicbricks.com/roy-mansion-santacruz-east-mumbai-pdpid-4d4235303635313339",
    "https://www.magicbricks.com/new-vinay-chs-ltd-vidya-nagari-mumbai-pdpid-4d4235303635313039",
    "https://www.magicbricks.com/resham-apartment-santacruz-east-mumbai-pdpid-4d4235303635313335",
]

def main():
    print("="*80)
    print("SPOT TEST C - ABOUT PAGE DETECTION & RECOVERY")
    print("="*80)
    config = {
        'smart_filtering': False,   # test raw behavior
        'page_load_strategy': 'eager',
        'block_third_party_resources': True,
        'realistic_headers': True,
        'randomize_viewport': True,
        'concurrent_enabled': False,
    }
    scraper = IntegratedMagicBricksScraper(headless=False, custom_config=config)

    start = time.time()
    try:
        # Ensure driver ready and set referer to a valid listing URL
        scraper.setup_driver()
        listing_referer = 'https://www.magicbricks.com/property-for-sale-in-mumbai-pppfs'
        scraper.individual_scraper.set_listing_page_url(listing_referer)

        urls = PROBLEM_URLS[:5]
        print(f"[INFO] Testing {len(urls)} URLs for About-page detection & recovery")
        scraper.scrape_individual_property_pages(urls, batch_size=5, force_rescrape=True)
        print("[RESULT] Test C completed")
    except Exception as e:
        print("[ERROR][TEST C]", e)
    finally:
        try:
            scraper.close()
        except Exception:
            pass
    print(f"[DURATION] {time.time()-start:.1f}s")

if __name__ == '__main__':
    main()

