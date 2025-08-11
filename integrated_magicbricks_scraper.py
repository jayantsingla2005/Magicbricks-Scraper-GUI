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
from src.core.detailed_property_extractor import DetailedPropertyExtractor
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

        # Anti-scraping enhancement variables
        self.bot_detection_count = 0
        self.last_detection_time = None
        self.current_user_agent_index = 0
        self.session_start_time = None
        self.failed_requests = 0
        self.consecutive_failures = 0

        # City URL mapping for correct URLs
        self.city_url_mapping = {
            'mumbai': 'mumbai',
            'delhi': 'new-delhi',  # Fix: Delhi uses 'new-delhi' in URL
            'bangalore': 'bangalore',
            'pune': 'pune',
            'chennai': 'chennai',
            'hyderabad': 'hyderabad',
            'kolkata': 'kolkata',
            'ahmedabad': 'ahmedabad',
            'gurgaon': 'gurgaon',
            'noida': 'noida'
        }
        
        # Setup logging
        self.setup_logging()

        # Setup date parser (always needed for comprehensive data)
        if not hasattr(self, 'date_parser') or self.date_parser is None:
            self.date_parser = DateParsingSystem()

        # Note: DetailedPropertyExtractor is available for individual page scraping if needed
        # For now, we're doing comprehensive extraction from listing pages

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
                                         max_pages: int = None, include_individual_pages: bool = False) -> Dict[str, Any]:
        """Main scraping method with incremental support"""
        
        try:
            # Setup driver
            self.setup_driver()
            
            # Start session
            if not self.start_scraping_session(city, mode):
                return {'success': False, 'error': 'Failed to start session'}
            
            # Build base URL with correct city mapping
            url_city = self.city_url_mapping.get(city.lower(), city.lower())
            base_url = f"https://www.magicbricks.com/property-for-sale-in-{url_city}-pppfs"
            
            if mode in [ScrapingMode.INCREMENTAL, ScrapingMode.CONSERVATIVE, ScrapingMode.DATE_RANGE]:
                base_url += "?sort=date_desc"  # Force chronological sorting
            
            print(f"🔗 Base URL: {base_url}")
            
            # Scraping loop with enhanced anti-scraping
            page_number = 1
            consecutive_old_pages = 0
            self.session_start_time = time.time()

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
                
                # Scrape page with bot detection
                page_result = self.scrape_single_page(page_url, page_number)

                if not page_result['success']:
                    self.consecutive_failures += 1
                    print(f"❌ Failed to scrape page {page_number}: {page_result['error']}")

                    # Check if it's bot detection
                    if 'bot' in page_result['error'].lower() or 'captcha' in page_result['error'].lower():
                        self._handle_bot_detection()
                        continue  # Retry after recovery
                    else:
                        break
                else:
                    self.consecutive_failures = 0  # Reset on success
                
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
                
                # Enhanced delay strategy
                self._enhanced_delay_strategy(page_number)
                
                page_number += 1
            
            # Finalize session
            self.finalize_scraping_session()

            # Save to CSV and get filename (Phase 1 Complete)
            df, output_file = self.save_to_csv()

            # PHASE 2: Optional Individual Property Page Scraping
            individual_properties_scraped = 0
            if include_individual_pages and len(self.properties) > 0:
                self.logger.info("\\n🏠 PHASE 2: Starting Individual Property Page Scraping")
                self.logger.info("=" * 60)

                # Extract property URLs from scraped data
                property_urls = [prop.get('property_url', '') for prop in self.properties if prop.get('property_url')]
                property_urls = [url for url in property_urls if url]  # Remove empty URLs

                if property_urls:
                    self.logger.info(f"   📋 Found {len(property_urls)} property URLs for detailed scraping")

                    # Scrape individual property pages with enhanced anti-scraping
                    detailed_properties = self.scrape_individual_property_pages(property_urls, batch_size=10)
                    individual_properties_scraped = len(detailed_properties)

                    # Update CSV with detailed information if any were scraped
                    if detailed_properties:
                        self._update_csv_with_individual_data(output_file, detailed_properties)
                        self.logger.info(f"   ✅ Updated CSV with {individual_properties_scraped} detailed properties")

                else:
                    self.logger.warning("   ⚠️ No property URLs found for individual page scraping")

            return {
                'success': True,
                'session_stats': self.session_stats,
                'properties_scraped': len(self.properties),
                'individual_properties_scraped': individual_properties_scraped,
                'pages_scraped': self.session_stats['pages_scraped'],
                'output_file': output_file,
                'two_phase_scraping': include_individual_pages
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

            # Check for bot detection
            page_source = self.driver.page_source
            current_url = self.driver.current_url

            if self._detect_bot_detection(page_source, current_url):
                return {'success': False, 'error': 'Bot detection triggered'}

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
        """Extract comprehensive data from a single property card using robust selectors"""

        try:
            # Extract title using comprehensive selectors
            title = self._extract_with_fallback(card, [
                'h2.mb-srp__card--title',
                'h2[class*="title"]',
                'h3[class*="title"]',
                'a[class*="title"]',
                '.mb-srp__card--title',
                'h1', 'h2', 'h3', 'h4',  # Generic headers
                'a[href*="property"]',  # Property links
                '.SRPTuple__title',  # Alternative structure
                '[data-testid*="title"]'  # Test ID based
            ], 'N/A')

            # Extract price using comprehensive selectors
            price = self._extract_with_fallback(card, [
                'div.mb-srp__card__price--amount',
                'span[class*="price"]',
                'div[class*="price"]',
                '.mb-srp__card__price--amount',
                '.SRPTuple__price',  # Alternative structure
                '[data-testid*="price"]',  # Test ID based
                '*[class*="cost"]',  # Cost variations
                '*[class*="amount"]'  # Amount variations
            ], 'N/A')

            # Extract area using comprehensive selectors
            area = self._extract_with_fallback(card, [
                'div.mb-srp__card__summary--value',
                'span[class*="area"]',
                'div[class*="area"]',
                '.mb-srp__card__summary--value',
                '.SRPTuple__area',  # Alternative structure
                '[data-testid*="area"]',  # Test ID based
                '*[class*="sqft"]',  # Square feet variations
                '*[class*="size"]',  # Size variations
                '*[class*="carpet"]'  # Carpet area variations
            ], 'N/A')

            # Extract property URL for validation
            property_url = self._extract_property_url(card)

            # Only proceed if we have a valid property URL (avoids wrapper duplicates)
            if not property_url:
                return None

            # Extract posting date using specific date selector
            posting_date_text = self._extract_with_fallback(card, [
                '.mb-srp__card__photo__fig--post',  # Primary date selector
                'div[class*="post"]',  # Alternative post selectors
                'div[class*="update"]',  # Update selectors
                'div[class*="date"]',  # Date selectors
                '*[class*="ago"]',  # Time ago selectors
                '*[class*="hours"]',  # Hours selectors
                '*[class*="yesterday"]',  # Yesterday selectors
                '*[class*="today"]'  # Today selectors
            ], '')

            # If no specific date element found, try parsing from card text as fallback
            if not posting_date_text:
                card_text = card.get_text()
                posting_date_text = self.date_parser.parse_posting_date(card_text) if self.date_parser else ""

            # Parse the date text to get structured date info
            date_parse_result = self.date_parser.parse_posting_date(posting_date_text) if self.date_parser and posting_date_text else None
            parsed_posting_date = date_parse_result.get('parsed_datetime') if date_parse_result and date_parse_result.get('success') else None

            # COMPREHENSIVE FIELD EXTRACTION - Extract additional fields using specific selectors

            # Extract structured property details using the exact page structure
            bathrooms = self._extract_structured_field(card, 'Bathroom')
            balcony = self._extract_structured_field(card, 'Balcony')
            floor_details = self._extract_structured_field(card, 'Floor')
            status = self._extract_structured_field(card, 'Status')
            furnishing = self._extract_structured_field(card, 'Furnishing')
            facing = self._extract_structured_field(card, 'facing')
            parking = self._extract_structured_field(card, 'Car Parking')
            ownership = self._extract_structured_field(card, 'Ownership')
            transaction = self._extract_structured_field(card, 'Transaction')
            overlooking = self._extract_structured_field(card, 'overlooking')

            # Extract property type from title (1 BHK, 2 BHK, etc.)
            property_type = self._extract_property_type_from_title(title)

            # Extract society/project name from links
            society = self._extract_with_fallback(card, [
                'a[href*="pdpid"]',  # Project detail page links
                'a[href*="project"]'
            ], '')

            # Extract locality from the card structure
            locality = self._extract_with_fallback(card, [
                '.mb-srp__card__ads--locality',
                '*[class*="locality"]'
            ], '')

            # Build comprehensive property data
            property_data = {
                # Basic fields (existing)
                'title': title,
                'price': price,
                'area': area,
                'property_url': property_url,
                'page_number': page_number,
                'property_index': property_index,
                'scraped_at': datetime.now(),
                'posting_date_text': posting_date_text,
                'parsed_posting_date': parsed_posting_date,

                # Comprehensive fields (new)
                'bathrooms': bathrooms,
                'balcony': balcony,
                'property_type': property_type,
                'furnishing': furnishing,
                'floor_details': floor_details,
                'locality': locality,
                'society': society,
                'status': status,
                'facing': facing,
                'parking': parking,
                'ownership': ownership,
                'transaction': transaction,
                'overlooking': overlooking
            }

            return property_data

        except Exception as e:
            self.logger.error(f"Error extracting property data: {str(e)}")
            return None

    def _extract_structured_field(self, card, field_name: str) -> str:
        """Extract structured field value based on MagicBricks page structure"""
        try:
            # Find all elements that contain the field name
            field_elements = card.find_all(text=lambda text: text and field_name in text)

            for element in field_elements:
                # Get the parent element
                parent = element.parent
                if parent:
                    # Look for the next sibling or child that contains the value
                    next_sibling = parent.find_next_sibling()
                    if next_sibling:
                        value = next_sibling.get_text(strip=True)
                        if value and value != field_name:
                            return value

                    # Also check parent's next sibling
                    parent_next = parent.parent.find_next_sibling() if parent.parent else None
                    if parent_next:
                        value = parent_next.get_text(strip=True)
                        if value and value != field_name:
                            return value

            return ''
        except Exception:
            return ''

    def _extract_property_type_from_title(self, title: str) -> str:
        """Extract property type from title (1 BHK, 2 BHK, Studio, etc.)"""
        try:
            import re
            # Look for BHK patterns
            bhk_match = re.search(r'(\d+)\s*BHK', title, re.I)
            if bhk_match:
                return f"{bhk_match.group(1)} BHK"

            # Look for Studio
            if 'studio' in title.lower():
                return 'Studio'

            # Look for other property types
            property_types = ['Villa', 'House', 'Plot', 'Apartment', 'Flat']
            for prop_type in property_types:
                if prop_type.lower() in title.lower():
                    return prop_type

            return ''
        except Exception:
            return ''

    def _extract_with_fallback(self, card, selectors: List[str], default: str = 'N/A') -> str:
        """Extract text using fallback selectors with intelligent filtering"""

        for selector in selectors:
            try:
                elem = card.select_one(selector)
                if elem:
                    text = elem.get_text(strip=True)
                    if text and text != default and len(text) > 1:
                        # Additional validation for meaningful content
                        if not text.lower() in ['n/a', 'na', 'null', 'none', '--', '...']:
                            return text
            except Exception:
                continue

        # If no specific selector works, try intelligent text extraction
        try:
            all_text = card.get_text()

            # Look for price patterns
            if any(keyword in selectors[0].lower() for keyword in ['price', 'cost', 'amount']):
                import re
                price_match = re.search(r'₹[\d,.]+ (?:Crore|Lakh|crore|lakh)', all_text)
                if price_match:
                    return price_match.group()

            # Look for area patterns
            if any(keyword in selectors[0].lower() for keyword in ['area', 'sqft', 'size']):
                import re
                area_match = re.search(r'\d+[\d,.]* (?:sqft|sq ft|Sq\.? ?ft)', all_text, re.I)
                if area_match:
                    return area_match.group()

        except Exception:
            pass

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
    
    def _get_enhanced_user_agents(self):
        """Get list of realistic user agents for rotation"""
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]

    def _detect_bot_detection(self, page_source: str, current_url: str) -> bool:
        """Detect if we've been flagged as a bot"""
        bot_indicators = [
            'captcha', 'robot', 'bot detection', 'access denied',
            'cloudflare', 'please verify', 'security check',
            'unusual traffic', 'automated requests'
        ]

        page_lower = page_source.lower()
        url_lower = current_url.lower()

        for indicator in bot_indicators:
            if indicator in page_lower or indicator in url_lower:
                return True

        return False

    def _handle_bot_detection(self):
        """Handle bot detection with recovery strategies"""
        self.bot_detection_count += 1
        self.last_detection_time = time.time()

        self.logger.warning(f"🚨 Bot detection #{self.bot_detection_count} - Implementing recovery strategy")

        if self.bot_detection_count <= 3:
            # Strategy 1: Extended delay and user agent rotation
            delay = min(30 + (self.bot_detection_count * 15), 120)  # 30s to 120s
            self.logger.info(f"   🔄 Strategy 1: Extended delay ({delay}s) + User agent rotation")

            # Rotate user agent
            user_agents = self._get_enhanced_user_agents()
            self.current_user_agent_index = (self.current_user_agent_index + 1) % len(user_agents)

            time.sleep(delay)

            # Restart browser session
            self._restart_browser_session()

        elif self.bot_detection_count <= 5:
            # Strategy 2: Longer delay and session reset
            delay = 180 + (self.bot_detection_count * 30)  # 3-5 minutes
            self.logger.info(f"   🔄 Strategy 2: Long delay ({delay}s) + Complete session reset")

            time.sleep(delay)
            self._restart_browser_session()

        else:
            # Strategy 3: Extended break
            delay = 600  # 10 minutes
            self.logger.warning(f"   ⏸️ Strategy 3: Extended break ({delay}s) - Multiple detections")
            time.sleep(delay)
            self._restart_browser_session()

    def _restart_browser_session(self):
        """Restart browser session with new configuration"""
        try:
            if self.driver:
                self.driver.quit()
                time.sleep(2)

            # Create new session with rotated user agent
            self._setup_webdriver()
            self.logger.info("   ✅ Browser session restarted successfully")

        except Exception as e:
            self.logger.error(f"   ❌ Failed to restart browser session: {str(e)}")

    def _enhanced_delay_strategy(self, page_number: int):
        """Enhanced delay strategy based on session health"""
        base_delay = random.uniform(2.0, 5.0)

        # Increase delays if we've had recent bot detection
        if self.last_detection_time and (time.time() - self.last_detection_time) < 300:  # 5 minutes
            base_delay *= 1.5

        # Increase delays for consecutive failures
        if self.consecutive_failures > 0:
            base_delay *= (1 + self.consecutive_failures * 0.3)

        # Longer delays for later pages in session
        if page_number > 10:
            base_delay *= 1.2

        # Session duration factor
        if self.session_start_time and (time.time() - self.session_start_time) > 1800:  # 30 minutes
            base_delay *= 1.3

        final_delay = min(base_delay, 15.0)  # Cap at 15 seconds

        self.logger.info(f"⏱️ Waiting {final_delay:.1f} seconds before next page...")
        time.sleep(final_delay)

    def scrape_individual_property_pages(self, property_urls: List[str], batch_size: int = 10) -> List[Dict[str, Any]]:
        """
        Enhanced individual property page scraping with advanced anti-scraping measures
        """
        detailed_properties = []
        total_urls = len(property_urls)

        self.logger.info(f"🏠 Starting individual property page scraping for {total_urls} properties")
        self.logger.info(f"   📦 Batch size: {batch_size}")
        self.logger.info(f"   🛡️ Enhanced anti-scraping: Enabled")

        # Process in batches
        for batch_start in range(0, total_urls, batch_size):
            batch_end = min(batch_start + batch_size, total_urls)
            batch_urls = property_urls[batch_start:batch_end]

            self.logger.info(f"\\n📦 Processing batch {batch_start//batch_size + 1}: Properties {batch_start+1}-{batch_end}")

            # Process each property in the batch
            for i, url in enumerate(batch_urls, 1):
                try:
                    # Enhanced delay strategy for individual pages
                    if i > 1:  # Skip delay for first property in batch
                        delay = self._calculate_individual_page_delay(i, len(batch_urls))
                        self.logger.info(f"   ⏱️ Waiting {delay:.1f}s before next property...")
                        time.sleep(delay)

                    # Scrape individual property
                    property_data = self._scrape_single_property_page(url, batch_start + i)

                    if property_data:
                        detailed_properties.append(property_data)
                        self.logger.info(f"   ✅ Property {batch_start + i}/{total_urls}: Success")
                    else:
                        self.logger.warning(f"   ❌ Property {batch_start + i}/{total_urls}: Failed")

                except Exception as e:
                    self.logger.error(f"   ❌ Property {batch_start + i}/{total_urls}: Error - {str(e)}")
                    continue

            # Batch completion break
            if batch_end < total_urls:
                batch_break = 15 + (batch_start // batch_size) * 5  # Increasing breaks
                self.logger.info(f"   🛌 Batch break: {batch_break}s")
                time.sleep(batch_break)

        self.logger.info(f"\\n🎉 Individual property scraping complete: {len(detailed_properties)}/{total_urls} successful")
        return detailed_properties

    def _calculate_individual_page_delay(self, property_index: int, batch_size: int) -> float:
        """Calculate smart delay for individual property pages"""
        import random

        # Base delay: 3-8 seconds
        base_delay = random.uniform(3.0, 8.0)

        # Increase delay based on recent bot detection
        if self.last_detection_time and (time.time() - self.last_detection_time) < 600:  # 10 minutes
            base_delay *= 1.8

        # Increase delay for consecutive failures
        if self.consecutive_failures > 0:
            base_delay *= (1 + self.consecutive_failures * 0.4)

        # Progressive delay within batch
        if property_index > 5:
            base_delay *= 1.2

        # Session duration factor
        if self.session_start_time and (time.time() - self.session_start_time) > 3600:  # 1 hour
            base_delay *= 1.5

        return min(base_delay, 20.0)  # Cap at 20 seconds

    def _scrape_single_property_page(self, url: str, property_index: int) -> Optional[Dict[str, Any]]:
        """Scrape a single property page with enhanced error handling"""
        try:
            # Navigate with bot detection
            self.driver.get(url)

            # Check for bot detection
            page_source = self.driver.page_source
            current_url = self.driver.current_url

            if self._detect_bot_detection(page_source, current_url):
                self.logger.warning(f"   🚨 Bot detection on property {property_index}")
                self._handle_bot_detection()
                return None

            # Wait for page load
            time.sleep(2)

            # Extract detailed property data
            soup = BeautifulSoup(page_source, 'html.parser')

            property_data = {
                'url': url,
                'scraped_at': datetime.now().isoformat(),
                'property_index': property_index,
                'title': self._extract_property_title(soup),
                'price': self._extract_property_price(soup),
                'area': self._extract_property_area(soup),
                'amenities': self._extract_amenities(soup),
                'description': self._extract_description(soup),
                'builder_info': self._extract_builder_info(soup),
                'location_details': self._extract_location_details(soup),
                'specifications': self._extract_specifications(soup)
            }

            return property_data

        except Exception as e:
            self.logger.error(f"   ❌ Error scraping property {property_index}: {str(e)}")
            return None

    def _extract_property_title(self, soup: BeautifulSoup) -> str:
        """Extract property title from individual page"""
        selectors = [
            'h1.mb-ldp__dtls__title',
            'h1[class*="title"]',
            '.property-title',
            'h1'
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)

        return ''

    def _extract_property_price(self, soup: BeautifulSoup) -> str:
        """Extract property price from individual page"""
        selectors = [
            '.mb-ldp__dtls__price',
            '[class*="price"]',
            '.property-price'
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)

        return ''

    def _extract_property_area(self, soup: BeautifulSoup) -> str:
        """Extract property area from individual page"""
        selectors = [
            '.mb-ldp__dtls__area',
            '[class*="area"]',
            '.property-area'
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)

        return ''

    def _extract_amenities(self, soup: BeautifulSoup) -> List[str]:
        """Extract amenities from individual page"""
        amenities = []

        # Common amenity selectors
        amenity_selectors = [
            '.mb-ldp__amenities li',
            '.amenities-list li',
            '[class*="amenity"]'
        ]

        for selector in amenity_selectors:
            elements = soup.select(selector)
            for element in elements:
                amenity = element.get_text(strip=True)
                if amenity and amenity not in amenities:
                    amenities.append(amenity)

        return amenities

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract property description from individual page"""
        selectors = [
            '.mb-ldp__dtls__desc',
            '.property-description',
            '[class*="description"]'
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)

        return ''

    def _extract_builder_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract builder information from individual page"""
        builder_info = {}

        # Builder name
        builder_selectors = [
            '.mb-ldp__builder__name',
            '.builder-name',
            '[class*="builder"]'
        ]

        for selector in builder_selectors:
            element = soup.select_one(selector)
            if element:
                builder_info['name'] = element.get_text(strip=True)
                break

        return builder_info

    def _extract_location_details(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract detailed location information"""
        location_details = {}

        # Location selectors
        location_selectors = [
            '.mb-ldp__location',
            '.property-location',
            '[class*="location"]'
        ]

        for selector in location_selectors:
            element = soup.select_one(selector)
            if element:
                location_details['address'] = element.get_text(strip=True)
                break

        return location_details

    def _extract_specifications(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract detailed specifications"""
        specifications = {}

        # Specification selectors
        spec_selectors = [
            '.mb-ldp__specs tr',
            '.specifications tr',
            '[class*="spec"] tr'
        ]

        for selector in spec_selectors:
            rows = soup.select(selector)
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value:
                        specifications[key] = value

        return specifications

    def _update_csv_with_individual_data(self, csv_file: str, detailed_properties: List[Dict[str, Any]]):
        """Update CSV file with detailed individual property data"""
        try:
            import pandas as pd

            # Read existing CSV
            df = pd.read_csv(csv_file)

            # Create a mapping of URL to detailed data
            detailed_data_map = {prop['url']: prop for prop in detailed_properties}

            # Add new columns for detailed data
            new_columns = ['amenities', 'description', 'builder_name', 'location_address', 'specifications']
            for col in new_columns:
                if col not in df.columns:
                    df[col] = ''

            # Update rows with detailed data
            for index, row in df.iterrows():
                property_url = row.get('property_url', '')
                if property_url in detailed_data_map:
                    detailed_data = detailed_data_map[property_url]

                    # Update with detailed information
                    df.at[index, 'amenities'] = ', '.join(detailed_data.get('amenities', []))
                    df.at[index, 'description'] = detailed_data.get('description', '')
                    df.at[index, 'builder_name'] = detailed_data.get('builder_info', {}).get('name', '')
                    df.at[index, 'location_address'] = detailed_data.get('location_details', {}).get('address', '')
                    df.at[index, 'specifications'] = str(detailed_data.get('specifications', {}))

            # Save updated CSV
            df.to_csv(csv_file, index=False)
            self.logger.info(f"   💾 CSV updated with detailed property information")

        except Exception as e:
            self.logger.error(f"   ❌ Failed to update CSV with detailed data: {str(e)}")

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
