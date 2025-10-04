#!/usr/bin/env python3
"""
Multi-city runner for 50 listing pages per city (listing pages only).
Safe defaults: headless, incremental disabled, no PDP scraping.

Outputs:
- Per-city CSV/JSON files written by the scraper's ExportManager
- A compact summary JSON file (multi_city_run_summary.json)
"""

import json
import time
from datetime import datetime
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode


def main():
    cities = [
        'gurgaon',
        'mumbai',
        'bangalore',
        'pune',
        'hyderabad',
    ]

    max_pages = 50
    include_individual_pages = False  # listing pages only

    print("=" * 80)
    print("MULTI-CITY RUN (50 pages per city)")
    print("=" * 80)
    print(f"Start: {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"Cities: {', '.join(cities)}")
    print(f"Pages per city: {max_pages}")
    print(f"Include individual pages: {include_individual_pages}")
    print()

    summary = {
        'started_at': datetime.now().isoformat(),
        'cities': {},
    }

    for idx, city in enumerate(cities, 1):
        city_start = time.time()
        print("-" * 80)
        print(f"CITY {idx}/{len(cities)}: {city.upper()}")
        print("-" * 80)
        try:
            scraper = IntegratedMagicBricksScraper(headless=True, incremental_enabled=False)
            result = scraper.scrape_properties_with_incremental(
                city=city,
                mode=ScrapingMode.FULL,
                max_pages=max_pages,
                include_individual_pages=include_individual_pages,
                export_formats=['csv', 'json']
            )
            city_time = round(time.time() - city_start)
            summary['cities'][city] = {
                'success': bool(result.get('success')),
                'pages_scraped': result.get('pages_scraped'),
                'properties_scraped': result.get('properties_scraped'),
                'duration_seconds': city_time,
            }
            print(f"[DONE] {city} in {city_time}s | pages={result.get('pages_scraped')} props={result.get('properties_scraped')}")
        except Exception as e:
            city_time = round(time.time() - city_start)
            summary['cities'][city] = {
                'success': False,
                'error': str(e),
                'duration_seconds': city_time,
            }
            print(f"[ERROR] {city} failed after {city_time}s: {e}")

    summary['finished_at'] = datetime.now().isoformat()
    with open('multi_city_run_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("\n[SUMMARY] Saved to multi_city_run_summary.json")


if __name__ == '__main__':
    main()

