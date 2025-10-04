#!/usr/bin/env python3
"""
PDP Smoke Test: run 1 page incremental scrape and force re-scrape up to
3 individual property pages sequentially. Validates navigation and restart
path under PDP load without concurrency.
"""

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode


def main():
    config = {
        'concurrent_enabled': False,  # sequential PDP scraping
        'max_retries': 2,
        'max_individual_properties': 3,
        'page_delay_min': 0.5,
        'page_delay_max': 1.5,
    }

    scraper = IntegratedMagicBricksScraper(headless=True, incremental_enabled=True, custom_config=config)
    res = scraper.scrape_properties_with_incremental(
        city='gurgaon',
        mode=ScrapingMode.INCREMENTAL,
        max_pages=1,
        include_individual_pages=True,
        export_formats=['csv'],
        force_rescrape_individual=True,
    )
    summary = {
        'success': res.get('success'),
        'pages_scraped': res.get('pages_scraped'),
        'properties_scraped': res.get('properties_scraped'),
        'individual_properties_scraped': res.get('individual_properties_scraped'),
    }
    print("[PDP-SMOKE-RESULT]", summary)


if __name__ == '__main__':
    main()

