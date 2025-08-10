#!/usr/bin/env python3
"""
Integrated MagicBricks Scraper with Incremental System
Combines the production scraper with the evidence-based incremental scraping system.
Provides 60-75% time savings with high reliability.
"""

import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import logging
import json
from pathlib import Path

# Import our incremental scraping system
from incremental_scraping_system import IncrementalScrapingSystem
from user_mode_options import ScrapingMode
from date_parsing_system import DateParsingSystem
from smart_stopping_logic import SmartStoppingLogic
from url_tracking_system import URLTrackingSystem


class IntegratedMagicBricksScraper:
    """
    Production MagicBricks scraper with integrated incremental scraping system
    """
    
    def __init__(self, headless: bool = True, incremental_enabled: bool = True):
        """Initialize integrated scraper"""
        
        # Core scraper setup
        self.headless = headless
        self.driver = None
        self.properties = []
        
        # Incremental scraping system
        self.incremental_enabled = incremental_enabled
        if incremental_enabled:
            self.incremental_system = IncrementalScrapingSystem()
            self.date_parser = DateParsingSystem()
            self.stopping_logic = SmartStoppingLogic()
            self.url_tracker = URLTrackingSystem()
        
        # Session tracking
        self.session_stats = {
            'session_id': None,
            'start_time': None,
            'end_time': None,
            'mode': 'full',
            'pages_scraped': 0,
            'properties_found': 0,
            'properties_saved': 0,
            'incremental_stopped': False,
            'stop_reason': None
        }
        
        # Setup logging
        self.setup_logging()

        # Setup date parser (always needed for comprehensive data)
        from date_parsing_system import DateParsingSystem
        self.date_parser = DateParsingSystem()

        # Setup incremental system if enabled
        if self.incremental_enabled:
            self.setup_incremental_system()
        
        print("🚀 Integrated MagicBricks Scraper Initialized")
        print(f"   📊 Incremental scraping: {'Enabled' if incremental_enabled else 'Disabled'}")
    
    def setup_logging(self):
        """Setup logging for the scraper"""
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('integrated_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_incremental_system(self):
        """Setup the incremental scraping system"""
        
        try:
            print("🔧 Setting up incremental scraping system...")
            success = self.incremental_system.setup_system()
            
            if success:
                print("✅ Incremental scraping system ready")
            else:
                print("⚠️ Incremental system setup failed - falling back to full scraping")
                self.incremental_enabled = False
                
        except Exception as e:
            print(f"❌ Error setting up incremental system: {str(e)}")
            self.incremental_enabled = False
    
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Anti-detection measures
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("Chrome WebDriver initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise
    
    def start_scraping_session(self, city: str, mode: ScrapingMode = ScrapingMode.INCREMENTAL,
                             custom_config: Dict[str, Any] = None) -> bool:
        """Start a new scraping session with incremental support"""
        
        self.session_stats['start_time'] = datetime.now()
        self.session_stats['mode'] = mode.value if hasattr(mode, 'value') else str(mode)
        
        if self.incremental_enabled:
            # Start incremental session
            session_result = self.incremental_system.start_incremental_scraping(city, mode, custom_config)
            
            if session_result['success']:
                self.session_stats['session_id'] = session_result['session_id']
                self.session_stats['last_scrape_date'] = session_result.get('last_scrape_date')
                
                mode_str = mode.value if hasattr(mode, 'value') else str(mode)
                print(f"✅ Started {mode_str} scraping session for {city}")
                print(f"   📋 Session ID: {session_result['session_id']}")
                
                if session_result.get('last_scrape_date'):
                    print(f"   📅 Last scrape: {session_result['last_scrape_date']}")
                else:
                    print("   📅 No previous scrape found - performing full scrape")
                
                return True
            else:
                print(f"❌ Failed to start incremental session: {session_result['error']}")
                return False
        else:
            # Non-incremental session
            print(f"✅ Started full scraping session for {city}")
            return True
    
    def scrape_properties_with_incremental(self, city: str, mode: ScrapingMode = ScrapingMode.INCREMENTAL,
                                         max_pages: int = None) -> Dict[str, Any]:
        """Main scraping method with incremental support"""
        
        try:
            # Setup driver
            self.setup_driver()
            
            # Start session
            if not self.start_scraping_session(city, mode):
                return {'success': False, 'error': 'Failed to start session'}
            
            # Build base URL with chronological sorting for incremental mode
            base_url = f"https://www.magicbricks.com/property-for-sale-in-{city}-pppfs"
            
            if mode in [ScrapingMode.INCREMENTAL, ScrapingMode.CONSERVATIVE, ScrapingMode.DATE_RANGE]:
                base_url += "?sort=date_desc"  # Force chronological sorting
            
            print(f"🔗 Base URL: {base_url}")
            
            # Scraping loop
            page_number = 1
            consecutive_old_pages = 0
            
            while True:
                # Check page limits
                if max_pages and page_number > max_pages:
                    print(f"🛑 Reached maximum page limit: {max_pages}")
                    break
                
                # Build page URL
                if page_number == 1:
                    page_url = base_url
                else:
                    separator = '&' if '?' in base_url else '?'
                    page_url = f"{base_url}{separator}page={page_number}"
                
                print(f"\n📄 Scraping page {page_number}: {page_url}")
                
                # Scrape page
                page_result = self.scrape_single_page(page_url, page_number)
                
                if not page_result['success']:
                    print(f"❌ Failed to scrape page {page_number}: {page_result['error']}")
                    break
                
                # Update statistics
                self.session_stats['pages_scraped'] += 1
                self.session_stats['properties_found'] += page_result['properties_found']
                self.session_stats['properties_saved'] += page_result['properties_saved']
                
                # Incremental decision making
                if self.incremental_enabled and mode != ScrapingMode.FULL:
                    should_stop = self.make_incremental_decision(
                        page_result['property_texts'], 
                        page_number
                    )
                    
                    if should_stop['should_stop']:
                        self.session_stats['incremental_stopped'] = True
                        self.session_stats['stop_reason'] = should_stop['reason']
                        print(f"🛑 Incremental stopping: {should_stop['reason']}")
                        break
                
                # Random delay between pages
                delay = random.uniform(2, 5)
                print(f"⏱️ Waiting {delay:.1f} seconds before next page...")
                time.sleep(delay)
                
                page_number += 1
            
            # Finalize session
            self.finalize_scraping_session()

            # Save to CSV and get filename
            df, output_file = self.save_to_csv()

            return {
                'success': True,
                'session_stats': self.session_stats,
                'properties_scraped': len(self.properties),
                'pages_scraped': self.session_stats['pages_scraped'],
                'output_file': output_file
            }
            
        except Exception as e:
            self.logger.error(f"Scraping failed: {str(e)}")
            return {'success': False, 'error': str(e)}
        
        finally:
            self.close()
    
    def scrape_single_page(self, page_url: str, page_number: int) -> Dict[str, Any]:
        """Scrape a single page and extract properties"""

        try:
            # Set rotating user agent for anti-detection
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": random.choice(user_agents)
            })

            # Navigate to page
            self.driver.get(page_url)

            # Wait for content to load using proven selectors
            has_container = self._wait_for_listing_container()
            if not has_container:
                return {'success': False, 'error': 'Listing container not found'}

            # Parse page content
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Find property cards using proven selectors
            property_cards = self._find_property_cards(soup)

            if not property_cards:
                return {'success': False, 'error': 'No property cards found'}
            
            # Extract properties
            page_properties = []
            property_texts = []
            
            for i, card in enumerate(property_cards):
                try:
                    property_data = self.extract_property_data(card, page_number, i + 1)
                    if property_data:
                        page_properties.append(property_data)
                        property_texts.append(card.get_text())
                        
                except Exception as e:
                    self.logger.error(f"Error extracting property {i+1} on page {page_number}: {str(e)}")
                    continue
            
            # Store properties
            self.properties.extend(page_properties)
            
            print(f"   ✅ Extracted {len(page_properties)} properties from page {page_number}")
            
            return {
                'success': True,
                'properties_found': len(property_cards),
                'properties_saved': len(page_properties),
                'property_texts': property_texts
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _wait_for_listing_container(self) -> bool:
        """Wait for listing container to load using proven selectors"""

        selectors = [
            '[class*="mb-srp"]',
            '[class*="propertyCard"]',
            '[class*="property-card"]',
            '[class*="SRPTuple"]',
            '[class*="result"]',
            'div[data-id]',
        ]

        for selector in selectors:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                return True
            except TimeoutException:
                continue

        return False

    def _find_property_cards(self, soup) -> List:
        """Find property cards using proven selectors"""

        # Proven selectors from working scraper
        selectors = [
            'li.mb-srp__list__item',
            'div.mb-srp__card',
            'div.SRPTuple__cardWrap',
            'div.SRPTuple__card',
            'div.SRPTuple__tupleWrap',
            'article[class*="SRPTuple"]',
            'div[data-id][data-listingid]',
        ]

        for selector in selectors:
            cards = soup.select(selector)
            # Choose the first selector that yields a reasonable number of cards
            if cards and len(cards) >= 10:
                print(f"   🎯 Found {len(cards)} properties using selector: {selector}")
                return cards

        # Last resort: broader query
        property_cards = soup.select('div.mb-srp__card, div.SRPTuple__card, li.mb-srp__list__item')

        if not property_cards:
            import re
            property_cards = soup.find_all("div", class_=re.compile(r"mb-srp|property|card", re.I))

        if property_cards:
            print(f"   🎯 Found {len(property_cards)} properties using fallback selectors")

        return property_cards

    def extract_property_data(self, card, page_number: int, property_index: int) -> Optional[Dict[str, Any]]:
        """Extract data from a single property card using robust selectors"""

        try:
            # Extract title using multiple selectors
            title = self._extract_with_fallback(card, [
                'h2.mb-srp__card--title',
                'h2[class*="title"]',
                'h3[class*="title"]',
                'a[class*="title"]',
                '.mb-srp__card--title'
            ], 'N/A')

            # Extract price using multiple selectors
            price = self._extract_with_fallback(card, [
                'div.mb-srp__card__price--amount',
                'span[class*="price"]',
                'div[class*="price"]',
                '.mb-srp__card__price--amount'
            ], 'N/A')

            # Extract area using multiple selectors
            area = self._extract_with_fallback(card, [
                'div.mb-srp__card__summary--value',
                'span[class*="area"]',
                'div[class*="area"]',
                '.mb-srp__card__summary--value'
            ], 'N/A')

            # Extract property URL for validation
            property_url = self._extract_property_url(card)

            # Only proceed if we have a valid property URL (avoids wrapper duplicates)
            if not property_url:
                return None

            # Extract posting date (always extract for comprehensive data)
            card_text = card.get_text()
            date_info = self.date_parser.parse_posting_date(card_text)

            # Build property data
            property_data = {
                'title': title,
                'price': price,
                'area': area,
                'property_url': property_url,
                'page_number': page_number,
                'property_index': property_index,
                'scraped_at': datetime.now(),
                'posting_date_text': date_info.get('raw_text') if date_info and date_info['success'] else None,
                'parsed_posting_date': date_info.get('parsed_datetime') if date_info and date_info['success'] else None
            }

            return property_data

        except Exception as e:
            self.logger.error(f"Error extracting property data: {str(e)}")
            return None

    def _extract_with_fallback(self, card, selectors: List[str], default: str = 'N/A') -> str:
        """Extract text using fallback selectors"""

        for selector in selectors:
            try:
                elem = card.select_one(selector)
                if elem:
                    text = elem.get_text(strip=True)
                    if text:
                        return text
            except Exception:
                continue

        return default

    def _extract_property_url(self, card) -> Optional[str]:
        """Extract property URL from card"""

        url_selectors = [
            'a[href*="/propertydetail/"]',
            'a[href*="/property-details/"]',
            'a[href*="magicbricks.com"]',
            'a[href]'
        ]

        for selector in url_selectors:
            try:
                link = card.select_one(selector)
                if link and link.get('href'):
                    href = link.get('href')
                    if 'magicbricks.com' in href or href.startswith('/'):
                        return href
            except Exception:
                continue

        return None
    
    def make_incremental_decision(self, property_texts: List[str], page_number: int) -> Dict[str, Any]:
        """Make incremental scraping decision based on property data"""
        
        if not self.incremental_enabled or not self.session_stats.get('last_scrape_date'):
            return {'should_stop': False, 'reason': 'Incremental not enabled or no last scrape date'}
        
        try:
            # Analyze page for stopping decision
            analysis = self.incremental_system.analyze_page_for_incremental_decision(
                property_texts,
                self.session_stats['session_id'],
                page_number,
                self.session_stats['last_scrape_date']
            )
            
            return {
                'should_stop': analysis['should_stop'],
                'reason': analysis['stop_reason'],
                'confidence': analysis['confidence'],
                'old_percentage': analysis['date_analysis']['old_percentage']
            }
            
        except Exception as e:
            self.logger.error(f"Error in incremental decision: {str(e)}")
            return {'should_stop': False, 'reason': f'Decision error: {str(e)}'}
    
    def finalize_scraping_session(self):
        """Finalize the scraping session"""
        
        self.session_stats['end_time'] = datetime.now()
        
        if self.incremental_enabled and self.session_stats.get('session_id'):
            # Finalize incremental session
            self.incremental_system.finalize_incremental_session(
                self.session_stats['session_id'],
                {
                    'pages_scraped': self.session_stats['pages_scraped'],
                    'properties_found': self.session_stats['properties_found'],
                    'properties_saved': self.session_stats['properties_saved']
                }
            )
        
        # Calculate duration
        if self.session_stats['start_time'] and self.session_stats['end_time']:
            duration = self.session_stats['end_time'] - self.session_stats['start_time']
            self.session_stats['duration_seconds'] = duration.total_seconds()
            self.session_stats['duration_formatted'] = f"{duration.total_seconds()//60:.0f}m {duration.total_seconds()%60:.0f}s"
        
        print(f"\n📊 SCRAPING SESSION COMPLETE")
        print("="*50)
        print(f"✅ Mode: {self.session_stats['mode']}")
        print(f"✅ Pages scraped: {self.session_stats['pages_scraped']}")
        print(f"✅ Properties found: {self.session_stats['properties_found']}")
        print(f"✅ Properties saved: {self.session_stats['properties_saved']}")
        print(f"✅ Duration: {self.session_stats.get('duration_formatted', 'N/A')}")
        
        if self.session_stats.get('incremental_stopped'):
            print(f"🛑 Stopped by incremental logic: {self.session_stats['stop_reason']}")
    
    def save_to_csv(self, filename: str = None) -> tuple:
        """Save scraped properties to CSV

        Returns:
            tuple: (DataFrame, filename) or (None, None) if failed
        """

        if not self.properties:
            print("⚠️ No properties to save")
            return None, None

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mode = self.session_stats.get('mode', 'unknown')
            filename = f"magicbricks_{mode}_scrape_{timestamp}.csv"

        try:
            df = pd.DataFrame(self.properties)
            df.to_csv(filename, index=False)

            print(f"💾 Saved {len(self.properties)} properties to {filename}")
            return df, filename

        except Exception as e:
            self.logger.error(f"Error saving to CSV: {str(e)}")
            return None, None
    
    def close(self):
        """Close the WebDriver"""
        
        if self.driver:
            self.driver.quit()
            self.logger.info("WebDriver closed")


def main():
    """Main function for testing integrated scraper"""
    
    try:
        # Initialize integrated scraper
        scraper = IntegratedMagicBricksScraper(headless=True, incremental_enabled=True)
        
        # Test incremental scraping
        print("🧪 Testing integrated scraper with incremental mode...")
        
        result = scraper.scrape_properties_with_incremental(
            city='gurgaon',
            mode=ScrapingMode.INCREMENTAL,
            max_pages=5  # Limit for testing
        )
        
        if result['success']:
            print(f"\n✅ Scraping successful!")
            print(f"📊 Properties scraped: {result['properties_scraped']}")
            print(f"📄 Pages scraped: {result['pages_scraped']}")
            print(f"📁 Output file: {result.get('output_file', 'N/A')}")

            if result.get('output_file'):
                print(f"💾 Data saved successfully to {result['output_file']}")
        else:
            print(f"❌ Scraping failed: {result['error']}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    
    finally:
        if 'scraper' in locals():
            scraper.close()


if __name__ == "__main__":
    main()
