#!/usr/bin/env python3
"""
Minimal end-to-end smoke test for the IntegratedMagicBricksScraper.
Runs 1 listing page and scrapes up to 3 individual PDPs sequentially to
validate the restart pipeline and basic flow without heavy load.

This file is for local testing only and does not modify scraper code.
"""

import time
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode


def main():
    print("\n[SMOKE] Starting minimal end-to-end test (1 page, 3 PDPs, sequential)")
    config = {
        'concurrent_enabled': False,   # sequential PDP scraping to avoid driver contention
        'max_retries': 2,
        'max_individual_properties': 3,
        'page_delay_min': 0.5,
        'page_delay_max': 1.5,
    }

    scraper = IntegratedMagicBricksScraper(headless=True, incremental_enabled=True, custom_config=config)

    result = scraper.scrape_properties_with_incremental(
        city='gurgaon',
        mode=ScrapingMode.INCREMENTAL,
        max_pages=1,
        include_individual_pages=True,
        export_formats=['csv']
    )

    print("\n[SMOKE-RESULT]", {
        'success': result.get('success'),
        'pages_scraped': result.get('pages_scraped'),
        'properties_scraped': result.get('properties_scraped'),
        'individual_properties_scraped': result.get('individual_properties_scraped'),
    })


if __name__ == '__main__':
    main()

