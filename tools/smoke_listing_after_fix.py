#!/usr/bin/env python3
import sys
import time
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode

if __name__ == '__main__':
    config = {
        'concurrent_enabled': False,
        'max_retries': 2,
        'max_individual_properties': 0,
        'page_delay_min': 1,
        'page_delay_max': 3,
        'individual_delay_min': 4,
        'individual_delay_max': 8,
        'batch_break_delay': 10,
    }

    print('[SMOKE] Starting 1-page Gurgaon listing (headful, no PDPs) to validate anti-bot fixes...')
    scraper = IntegratedMagicBricksScraper(headless=False, incremental_enabled=False, custom_config=config)
    result = scraper.scrape_properties_with_incremental(
        city='gurgaon',
        mode=ScrapingMode.FULL,
        max_pages=1,
        include_individual_pages=False,
        export_formats=['csv','json'],
        force_rescrape_individual=False
    )
    print('\n[SMOKE-SUMMARY]', result.get('success'), result.get('pages_scraped'), result.get('individual_properties_scraped'))
    sys.exit(0 if result.get('success') else 1)

