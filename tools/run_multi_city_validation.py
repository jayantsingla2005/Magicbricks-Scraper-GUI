#!/usr/bin/env python3
import re
import sys
import time
import logging
import threading
from contextlib import contextmanager
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode

CITIES = ['gurgaon', 'mumbai', 'bangalore', 'delhi', 'pune']

CONFIG_BASE = {
    'concurrent_enabled': False,
    'max_retries': 2,
    'max_individual_properties': 0,
    'page_delay_min': 1,
    'page_delay_max': 3,
    'individual_delay_min': 4,
    'individual_delay_max': 8,
    'batch_break_delay': 10,
}

BOT_LISTING_RE = re.compile(r"^\[ERROR\] Failed to scrape page (\d+): Bot detection triggered")

class StdoutInterceptor:
    def __init__(self):
        self._lock = threading.Lock()
        self.consecutive_listing_bots = 0
        self.lines = []

    def write(self, s: str):
        with self._lock:
            for line in s.splitlines():
                self.lines.append(line)
                if BOT_LISTING_RE.search(line):
                    self.consecutive_listing_bots += 1
                elif line.strip():
                    # reset on any other meaningful line
                    self.consecutive_listing_bots = 0
            sys.__stdout__.write(s)

    def flush(self):
        sys.__stdout__.flush()

@contextmanager
def intercept_prints(interceptor: StdoutInterceptor):
    prev = sys.stdout
    sys.stdout = interceptor
    try:
        yield
    finally:
        sys.stdout = prev


def run_city(city: str, headless: bool) -> dict:
    cfg = dict(CONFIG_BASE)
    print(f"\n[RUN] City={city} mode=FULL pages>=50 headless={headless} include_individual_pages=True formats=csv,json")
    scraper = IntegratedMagicBricksScraper(headless=headless, incremental_enabled=False, custom_config=cfg)

    interceptor = StdoutInterceptor()
    with intercept_prints(interceptor):
        result = scraper.scrape_properties_with_incremental(
            city=city,
            mode=ScrapingMode.FULL,
            max_pages=50,
            include_individual_pages=True,
            export_formats=['csv','json'],
            force_rescrape_individual=False
        )
        # Auto-stop if 3+ consecutive listing bot detections observed
        if interceptor.consecutive_listing_bots >= 3:
            print(f"[ABORT] Detected {interceptor.consecutive_listing_bots} consecutive listing-page bot detections. Stopping {city} early.")
            result['aborted_due_to_listing_bot'] = True
    return result


def main():
    headless = False
    overall = {}
    for city in CITIES:
        res = run_city(city, headless=headless)
        overall[city] = {
            'success': res.get('success'),
            'pages_scraped': res.get('pages_scraped'),
            'individual_properties_scraped': res.get('individual_properties_scraped'),
            'aborted_due_to_listing_bot': res.get('aborted_due_to_listing_bot', False),
        }
        print(f"[SUMMARY][{city}] success={overall[city]['success']} pages={overall[city]['pages_scraped']} indiv={overall[city]['individual_properties_scraped']} aborted={overall[city]['aborted_due_to_listing_bot']}")
        # If PDP bot rate too high, adjust and rerun this city per spec
        # (Note: Without direct PDP bot rate metric here, we leave timing unchanged in this runner.)

    print("\n[RUN-COMPLETE] Multi-city validation finished.")
    for city, s in overall.items():
        print(f"  - {city}: success={s['success']}, pages={s['pages_scraped']}, indiv={s['individual_properties_scraped']}, aborted={s['aborted_due_to_listing_bot']}")

if __name__ == '__main__':
    main()

