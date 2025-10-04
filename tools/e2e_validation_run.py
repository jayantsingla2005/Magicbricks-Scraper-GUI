#!/usr/bin/env python3
"""
E2E Validation Runner: 2 cities x 100 pages each, incremental mode, headful, with individual property pages enabled.
Writes progress to stdout and leverages integrated logger for detailed logs (integrated_scraper.log).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.join(__file__, '..'))))
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode


def run_city(city: str) -> dict:
    print(f"[RUN] Starting {city.title()} (100 pages) :: mode=INCREMENTAL, include_individual_pages=True, headful")
    scraper = IntegratedMagicBricksScraper(headless=False, incremental_enabled=True)
    try:
        res = scraper.scrape_properties_with_incremental(
            city=city,
            mode=ScrapingMode.INCREMENTAL,
            max_pages=100,
            include_individual_pages=True,
            export_formats=['csv']
        )
        print(f"[RESULT][{city.upper()}] success={res.get('success')} pages={res.get('pages_scraped')} props_found={res.get('properties_found')} props_saved={res.get('properties_saved')}")
        return res
    finally:
        try:
            scraper.close()
        except Exception:
            pass


def main():
    g = run_city('gurgaon')
    m = run_city('mumbai')
    print('[SUMMARY] Gurgaon:', g)
    print('[SUMMARY] Mumbai :', m)


if __name__ == '__main__':
    main()

