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
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
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
# from src.core.detailed_property_extractor import DetailedPropertyExtractor  # Available for future individual page scraping
from smart_stopping_logic import SmartStoppingLogic
from url_tracking_system import URLTrackingSystem


class IntegratedMagicBricksScraper:
    """
    Production MagicBricks scraper with integrated incremental scraping system
    """
    
    def __init__(self, headless: bool = True, incremental_enabled: bool = True, custom_config: Dict[str, Any] = None):
        """Initialize integrated scraper with custom configuration"""

        # Core scraper setup
        self.headless = headless
        self.driver = None
        self.properties = []

        # Setup custom configuration
        self.config = self._setup_default_config()
        if custom_config:
            self.config.update(custom_config)

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
        print(f"   ⚙️ Custom configuration: {'Enabled' if custom_config else 'Default'}")

    def _setup_default_config(self) -> Dict[str, Any]:
        """Setup default configuration for the scraper"""
        return {
            # Delay configurations - REDUCED for better performance
            'page_delay_min': 0.5,
            'page_delay_max': 2.0,
            'individual_delay_min': 0.1,
            'individual_delay_max': 3.0,
            'batch_break_delay': 5,
            'bot_recovery_delay': 15,
            
            # Concurrent scraping configurations
            'concurrent_pages': 4,  # Default concurrent pages for individual scraping
            'max_concurrent_pages': 8,  # Maximum allowed concurrent pages
            'concurrent_enabled': True,  # Enable concurrent scraping by default

            # City-specific delays (REDUCED for better performance)
            'city_delays': {
                'mumbai': {'page': (0.5, 2.0), 'individual': (0.1, 3.0)},
                'delhi': {'page': (0.5, 2.0), 'individual': (0.1, 3.0)},
                'bangalore': {'page': (0.5, 2.0), 'individual': (0.1, 3.0)},
                'pune': {'page': (0.5, 2.0), 'individual': (0.1, 3.0)},
                'hyderabad': {'page': (0.5, 2.0), 'individual': (0.1, 3.0)},
                'chennai': {'page': (0.5, 2.0), 'individual': (0.1, 3.0)},
                'kolkata': {'page': (0.5, 2.0), 'individual': (0.1, 3.0)},
                'ahmedabad': {'page': (0.5, 2.0), 'individual': (0.1, 3.0)},
                'gurgaon': {'page': (0.5, 2.0), 'individual': (0.1, 3.0)},
                'noida': {'page': (0.5, 2.0), 'individual': (0.1, 3.0)}
            },

            # Anti-scraping configurations
            'max_retries': 3,
            'timeout_seconds': 30,
            'user_agent_rotation': True,
            'proxy_rotation': False,
            'captcha_handling': True,

            # Performance configurations
            'batch_size': 10,
            'max_workers': 3,
            'memory_optimization': True,
            'cache_enabled': False,

            # Export configurations
            'default_export_formats': ['csv'],
            'auto_backup': False,
            'compression_enabled': False,

            # Filtering configurations
            'enable_filtering': False,
            'price_filter': {'min': None, 'max': None},
            'area_filter': {'min': None, 'max': None},
            'property_type_filter': [],  # ['apartment', 'house', 'plot', etc.]
            'bhk_filter': [],  # ['1', '2', '3', '4+']
            'location_filter': [],  # Specific localities
            'amenities_filter': [],  # Required amenities
            'exclude_keywords': []  # Keywords to exclude from title/description
        }

    def setup_logging(self):
        """Setup logging for the scraper with Unicode support"""

        # Create custom formatter that handles Unicode safely
        class SafeFormatter(logging.Formatter):
            def format(self, record):
                # Replace Unicode characters that might cause issues
                if hasattr(record, 'msg'):
                    if isinstance(record.msg, str):
                        # Replace problematic Unicode characters with safe alternatives
                        record.msg = (record.msg
                                    .replace('🏠', '[HOUSE]')
                                    .replace('📦', '[BATCH]')
                                    .replace('🛡️', '[SHIELD]')
                                    .replace('⏱️', '[TIMER]')
                                    .replace('✅', '[SUCCESS]')
                                    .replace('❌', '[ERROR]')
                                    .replace('🛌', '[BREAK]')
                                    .replace('📋', '[LIST]')
                                    .replace('💾', '[SAVE]')
                                    .replace('🎉', '[COMPLETE]')
                                    .replace('🚨', '[ALERT]')
                                    .replace('🔄', '[RETRY]')
                                    .replace('⏸️', '[PAUSE]'))
                return super().format(record)

        # Setup logging with safe formatter
        formatter = SafeFormatter('%(asctime)s - %(levelname)s - %(message)s')

        # File handler with UTF-8 encoding
        file_handler = logging.FileHandler('integrated_scraper.log', encoding='utf-8')
        file_handler.setFormatter(formatter)

        # Console handler with safe encoding
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Add new handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Prevent duplicate logs
        self.logger.propagate = False
    
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
        """Setup Chrome WebDriver with enhanced error handling and session management"""
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                chrome_options = Options()
                
                if self.headless:
                    chrome_options.add_argument("--headless")
                
                # Enhanced stability options
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--disable-web-security")
                chrome_options.add_argument("--disable-features=VizDisplayCompositor")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-plugins")
                chrome_options.add_argument("--disable-images")  # Faster loading
                chrome_options.add_argument("--disable-javascript")  # Reduce complexity
                
                # Enhanced anti-detection measures
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                # Performance optimizations
                chrome_options.add_argument("--memory-pressure-off")
                chrome_options.add_argument("--max_old_space_size=4096")
                
                # Create WebDriver with timeout
                self.driver = webdriver.Chrome(options=chrome_options)
                
                # Set timeouts
                self.driver.implicitly_wait(10)
                self.driver.set_page_load_timeout(30)
                self.driver.set_script_timeout(30)
                
                # Anti-detection script
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                # Test connection
                self.driver.get("https://www.google.com")
                
                self.logger.info(f"Chrome WebDriver initialized successfully (attempt {attempt + 1})")
                return
                
            except Exception as e:
                self.logger.error(f"Failed to initialize WebDriver (attempt {attempt + 1}): {str(e)}")
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))  # Progressive delay
                else:
                    raise Exception(f"Failed to initialize WebDriver after {max_retries} attempts: {str(e)}")
    
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
                                         max_pages: int = None, include_individual_pages: bool = False,
                                         export_formats: List[str] = ['csv'], progress_callback=None) -> Dict[str, Any]:
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
            
            # Initialize progress tracking
            estimated_total_pages = max_pages if max_pages else 50  # Default estimate
            progress_data = {
                'phase': 'listing_extraction',
                'current_page': 0,
                'total_pages': estimated_total_pages,
                'properties_found': 0,
                'progress_percentage': 0,
                'estimated_time_remaining': 0,
                'start_time': time.time(),
                'city': city,
                'mode': mode.value if hasattr(mode, 'value') else str(mode)
            }

            # Send initial progress update
            if progress_callback:
                progress_callback(progress_data)

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

                # Update progress before scraping page
                progress_data.update({
                    'current_page': page_number,
                    'progress_percentage': min((page_number / estimated_total_pages) * 100, 100),
                    'properties_found': len(self.properties)
                })

                # Calculate estimated time remaining
                elapsed_time = time.time() - progress_data['start_time']
                if page_number > 1:
                    avg_time_per_page = elapsed_time / (page_number - 1)
                    remaining_pages = max(0, estimated_total_pages - page_number + 1)
                    progress_data['estimated_time_remaining'] = avg_time_per_page * remaining_pages

                # Send progress update
                if progress_callback:
                    progress_callback(progress_data)

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

            # Validate data quality
            validation_report = self._validate_data_completeness(self.properties)
            self.session_stats['validation_report'] = validation_report

            # Log data quality summary
            self.logger.info(f"\\n[COMPLETE] DATA QUALITY REPORT")
            self.logger.info(f"   [LIST] Total properties: {validation_report.get('total_properties', 0)}")
            self.logger.info(f"   [SUCCESS] Valid properties: {validation_report.get('valid_properties', 0)}")
            self.logger.info(f"   [SHIELD] Validation success rate: {validation_report.get('validation_success_rate', 0):.1f}%")
            self.logger.info(f"   [COMPLETE] Average data quality: {validation_report.get('data_quality_average', 0):.1f}%")

            # Export data in requested formats (Phase 1 Complete)
            exported_files = self.export_data(formats=export_formats)

            # Get primary output file (CSV is always included)
            output_file = exported_files.get('csv', 'No CSV file generated')

            # PHASE 2: Optional Individual Property Page Scraping
            individual_properties_scraped = 0
            if include_individual_pages and len(self.properties) > 0:
                self.logger.info("\\n[HOUSE] PHASE 2: Starting Individual Property Page Scraping")
                self.logger.info("=" * 60)

                # Extract property URLs from scraped data
                property_urls = [prop.get('property_url', '') for prop in self.properties if prop.get('property_url')]
                property_urls = [url for url in property_urls if url]  # Remove empty URLs

                if property_urls:
                    self.logger.info(f"   [LIST] Found {len(property_urls)} property URLs for detailed scraping")

                    # Update progress for Phase 2
                    progress_data.update({
                        'phase': 'individual_property_extraction',
                        'current_page': 0,
                        'total_pages': len(property_urls),
                        'progress_percentage': 0,
                        'estimated_time_remaining': 0,
                        'start_time': time.time()
                    })

                    # Send progress update for Phase 2 start
                    if progress_callback:
                        progress_callback(progress_data)

                    # Scrape individual property pages with enhanced anti-scraping and progress tracking
                    detailed_properties = self.scrape_individual_property_pages(
                        property_urls,
                        batch_size=10,
                        progress_callback=progress_callback,
                        progress_data=progress_data
                    )
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
                'exported_files': exported_files,
                'export_formats': export_formats,
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
                        # Validate and clean property data
                        cleaned_property_data = self._validate_and_clean_property_data(property_data)

                        # Apply filtering if enabled
                        if self._apply_property_filters(cleaned_property_data):
                            page_properties.append(cleaned_property_data)
                            property_texts.append(card.get_text())

                            # Track filtering stats
                            if not hasattr(self, '_filter_stats'):
                                self._filter_stats = {'total': 0, 'filtered': 0, 'excluded': 0}
                            self._filter_stats['total'] += 1
                            self._filter_stats['filtered'] += 1
                        else:
                            # Property was excluded by filters
                            if not hasattr(self, '_filter_stats'):
                                self._filter_stats = {'total': 0, 'filtered': 0, 'excluded': 0}
                            self._filter_stats['total'] += 1
                            self._filter_stats['excluded'] += 1
                            self.logger.debug(f"Property {i+1} on page {page_number} excluded by filters")
                        
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

        # Updated selectors based on current MagicBricks structure
        selectors = [
            '.mb-srp__card',  # Updated: removed div prefix for broader matching
            '.mb-srp__list',  # Updated: actual class name found in HTML
            'li.mb-srp__list__item',  # Keep as fallback
            'div.mb-srp__card',  # Keep as fallback
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
        property_cards = soup.select('.mb-srp__card, .mb-srp__list, div.SRPTuple__card, li.mb-srp__list__item')

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

    def save_to_json(self, filename: str = None) -> tuple:
        """Save scraped properties to JSON

        Returns:
            tuple: (data, filename) or (None, None) if failed
        """

        if not self.properties:
            print("⚠️ No properties to save")
            return None, None

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mode = self.session_stats.get('mode', 'unknown')
            filename = f"magicbricks_{mode}_scrape_{timestamp}.json"

        try:
            # Create comprehensive JSON structure
            json_data = {
                'metadata': {
                    'scrape_timestamp': datetime.now().isoformat(),
                    'total_properties': len(self.properties),
                    'session_stats': self.session_stats,
                    'scraper_version': '2.0',
                    'export_format': 'json'
                },
                'properties': self.properties
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)

            print(f"💾 Saved {len(self.properties)} properties to {filename}")
            return json_data, filename

        except Exception as e:
            self.logger.error(f"Error saving to JSON: {str(e)}")
            return None, None

    def save_to_excel(self, filename: str = None) -> tuple:
        """Save scraped properties to Excel with multiple sheets

        Returns:
            tuple: (DataFrame, filename) or (None, None) if failed
        """

        if not self.properties:
            print("⚠️ No properties to save")
            return None, None

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mode = self.session_stats.get('mode', 'unknown')
            filename = f"magicbricks_{mode}_scrape_{timestamp}.xlsx"

        try:
            df = pd.DataFrame(self.properties)

            # Create Excel writer with multiple sheets
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Main properties sheet
                df.to_excel(writer, sheet_name='Properties', index=False)

                # Summary sheet
                summary_data = {
                    'Metric': [
                        'Total Properties',
                        'Scrape Date',
                        'Mode',
                        'Pages Scraped',
                        'Duration',
                        'Success Rate'
                    ],
                    'Value': [
                        len(self.properties),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        self.session_stats.get('mode', 'unknown'),
                        self.session_stats.get('pages_scraped', 0),
                        self.session_stats.get('duration_formatted', 'N/A'),
                        f"{self.session_stats.get('success_rate', 0):.1f}%"
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)

                # City breakdown if available
                if 'city_stats' in self.session_stats:
                    city_df = pd.DataFrame(self.session_stats['city_stats'])
                    city_df.to_excel(writer, sheet_name='City_Stats', index=False)

            print(f"💾 Saved {len(self.properties)} properties to {filename}")
            return df, filename

        except Exception as e:
            self.logger.error(f"Error saving to Excel: {str(e)}")
            return None, None

    def export_data(self, formats: List[str] = ['csv'], base_filename: str = None) -> Dict[str, str]:
        """Export data in multiple formats

        Args:
            formats: List of formats to export ('csv', 'json', 'excel')
            base_filename: Base filename without extension

        Returns:
            Dict mapping format to filename
        """

        if not self.properties:
            print("⚠️ No properties to export")
            return {}

        if base_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mode = self.session_stats.get('mode', 'unknown')
            base_filename = f"magicbricks_{mode}_scrape_{timestamp}"

        exported_files = {}

        for format_type in formats:
            try:
                if format_type.lower() == 'csv':
                    filename = f"{base_filename}.csv"
                    _, saved_filename = self.save_to_csv(filename)
                    if saved_filename:
                        exported_files['csv'] = saved_filename

                elif format_type.lower() == 'json':
                    filename = f"{base_filename}.json"
                    _, saved_filename = self.save_to_json(filename)
                    if saved_filename:
                        exported_files['json'] = saved_filename

                elif format_type.lower() == 'excel':
                    filename = f"{base_filename}.xlsx"
                    _, saved_filename = self.save_to_excel(filename)
                    if saved_filename:
                        exported_files['excel'] = saved_filename

                else:
                    print(f"⚠️ Unsupported format: {format_type}")

            except Exception as e:
                self.logger.error(f"Error exporting {format_type}: {str(e)}")

        return exported_files

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

    def scrape_individual_property_pages(self, property_urls: List[str], batch_size: int = 10,
                                        progress_callback=None, progress_data=None) -> List[Dict[str, Any]]:
        """
        Enhanced individual property page scraping with concurrent processing and advanced anti-scraping measures
        """
        detailed_properties = []
        total_urls = len(property_urls)
        
        # Check if concurrent scraping is enabled
        concurrent_enabled = self.config.get('concurrent_enabled', True)
        concurrent_pages = min(self.config.get('concurrent_pages', 4), self.config.get('max_concurrent_pages', 8))
        
        self.logger.info(f"🏠 Starting individual property page scraping for {total_urls} properties")
        self.logger.info(f"   📦 Batch size: {batch_size}")
        self.logger.info(f"   🛡️ Enhanced anti-scraping: Enabled")
        self.logger.info(f"   🔄 Concurrent processing: {'Enabled' if concurrent_enabled else 'Disabled'}")
        if concurrent_enabled:
            self.logger.info(f"   ⚡ Concurrent workers: {concurrent_pages}")

        if concurrent_enabled and total_urls > 1:
            return self._scrape_individual_pages_concurrent(property_urls, batch_size, progress_callback, progress_data)
        else:
            return self._scrape_individual_pages_sequential(property_urls, batch_size, progress_callback, progress_data)

    def _scrape_individual_pages_concurrent(self, property_urls: List[str], batch_size: int = 10,
                                          progress_callback=None, progress_data=None) -> List[Dict[str, Any]]:
        """
        Concurrent individual property page scraping using ThreadPoolExecutor
        """
        detailed_properties = []
        total_urls = len(property_urls)
        concurrent_pages = min(self.config.get('concurrent_pages', 4), self.config.get('max_concurrent_pages', 8))
        
        # Thread-safe results collection
        results_lock = threading.Lock()
        processed_count = 0
        
        def process_property_batch(batch_urls_with_indices):
            """Process a batch of properties concurrently"""
            nonlocal processed_count
            batch_results = []
            
            # Create a separate WebDriver for this thread
            thread_driver = None
            try:
                # Setup thread-specific WebDriver
                chrome_options = Options()
                if self.headless:
                    chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--disable-images")
                chrome_options.add_argument("--disable-javascript")
                chrome_options.add_argument("--disable-web-security")
                chrome_options.add_argument("--memory-pressure-off")
                
                thread_driver = webdriver.Chrome(options=chrome_options)
                thread_driver.implicitly_wait(10)
                thread_driver.set_page_load_timeout(30)
                
                for url, original_index in batch_urls_with_indices:
                    try:
                        # Apply reduced delay for concurrent processing
                        delay = random.uniform(
                            self.config.get('individual_delay_min', 0.1),
                            self.config.get('individual_delay_max', 3.0)
                        )
                        time.sleep(delay)
                        
                        # Scrape property using thread-specific driver
                        property_data = self._scrape_single_property_page_with_driver(thread_driver, url, original_index)
                        
                        if property_data:
                            batch_results.append(property_data)
                            
                        with results_lock:
                            processed_count += 1
                            self.logger.info(f"   ✅ Property {processed_count}/{total_urls}: {'Success' if property_data else 'Failed'}")
                            
                            # Update progress
                            if progress_callback and progress_data:
                                progress_data.update({
                                    'current_page': processed_count,
                                    'progress_percentage': (processed_count / total_urls) * 100,
                                    'properties_found': len(detailed_properties) + len(batch_results)
                                })
                                progress_callback(progress_data)
                                
                    except Exception as e:
                        with results_lock:
                            processed_count += 1
                            self.logger.error(f"   ❌ Property {processed_count}/{total_urls}: Error - {str(e)}")
                        
            except Exception as e:
                self.logger.error(f"Thread setup error: {str(e)}")
            finally:
                if thread_driver:
                    try:
                        thread_driver.quit()
                    except:
                        pass
                        
            return batch_results
        
        # Process in batches with concurrent workers
        for batch_start in range(0, total_urls, batch_size):
            batch_end = min(batch_start + batch_size, total_urls)
            batch_urls = property_urls[batch_start:batch_end]
            
            self.logger.info(f"\n📦 Processing batch {batch_start//batch_size + 1}: Properties {batch_start+1}-{batch_end}")
            
            # Prepare URLs with their original indices
            batch_urls_with_indices = [(url, batch_start + i) for i, url in enumerate(batch_urls)]
            
            # Split batch into chunks for concurrent processing
            chunk_size = max(1, len(batch_urls_with_indices) // concurrent_pages)
            chunks = [batch_urls_with_indices[i:i + chunk_size] for i in range(0, len(batch_urls_with_indices), chunk_size)]
            
            # Process chunks concurrently
            with ThreadPoolExecutor(max_workers=concurrent_pages) as executor:
                future_to_chunk = {executor.submit(process_property_batch, chunk): chunk for chunk in chunks}
                
                for future in as_completed(future_to_chunk):
                    try:
                        chunk_results = future.result()
                        detailed_properties.extend(chunk_results)
                    except Exception as e:
                        self.logger.error(f"Chunk processing error: {str(e)}")
            
            # Batch completion break
            if batch_end < total_urls:
                batch_break = self.config.get('batch_break_delay', 5)
                self.logger.info(f"   🛌 Batch break: {batch_break}s")
                time.sleep(batch_break)
        
        self.logger.info(f"\n🎉 Concurrent individual property scraping complete: {len(detailed_properties)}/{total_urls} successful")
        return detailed_properties
    
    def _scrape_individual_pages_sequential(self, property_urls: List[str], batch_size: int = 10,
                                          progress_callback=None, progress_data=None) -> List[Dict[str, Any]]:
        """
        Sequential individual property page scraping (original method)
        """
        detailed_properties = []
        total_urls = len(property_urls)

        # Process in batches
        for batch_start in range(0, total_urls, batch_size):
            batch_end = min(batch_start + batch_size, total_urls)
            batch_urls = property_urls[batch_start:batch_end]

            self.logger.info(f"\n📦 Processing batch {batch_start//batch_size + 1}: Properties {batch_start+1}-{batch_end}")

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

                    # Update progress for individual property scraping
                    if progress_callback and progress_data:
                        current_property = batch_start + i
                        progress_data.update({
                            'current_page': current_property,
                            'progress_percentage': (current_property / total_urls) * 100,
                            'properties_found': len(detailed_properties)
                        })

                        # Calculate estimated time remaining
                        elapsed_time = time.time() - progress_data['start_time']
                        if current_property > 0:
                            avg_time_per_property = elapsed_time / current_property
                            remaining_properties = total_urls - current_property
                            progress_data['estimated_time_remaining'] = avg_time_per_property * remaining_properties

                        progress_callback(progress_data)

                except Exception as e:
                    self.logger.error(f"   ❌ Property {batch_start + i}/{total_urls}: Error - {str(e)}")
                    continue

            # Batch completion break
            if batch_end < total_urls:
                batch_break = self.config.get('batch_break_delay', 5)
                self.logger.info(f"   🛌 Batch break: {batch_break}s")
                time.sleep(batch_break)

        self.logger.info(f"\n🎉 Sequential individual property scraping complete: {len(detailed_properties)}/{total_urls} successful")
        return detailed_properties

    def _scrape_single_property_page_with_driver(self, driver, url: str, property_index: int) -> Dict[str, Any]:
        """
        Scrape a single property page using a specific WebDriver instance (for concurrent processing)
        """
        try:
            self.logger.debug(f"Navigating to property {property_index}: {url}")
            
            # Navigate to the property page
            driver.get(url)
            time.sleep(random.uniform(1, 3))  # Brief wait for page load
            
            # Check for bot detection
            if self._detect_bot_detection(driver.page_source, driver.current_url):
                self.logger.warning(f"Bot detection on property {property_index}, applying recovery")
                time.sleep(random.uniform(5, 10))
                return None
            
            # Validate that we're on a property page
            if not self._validate_property_page(driver.page_source):
                self.logger.warning(f"Invalid property page for {url}")
                return None
            
            # Extract property data using BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extract all property details
            property_data = {
                'url': url,
                'title': self._safe_extract_property_title(soup),
                'price': self._safe_extract_property_price(soup),
                'area': self._safe_extract_property_area(soup),
                'locality': self._safe_extract_locality(soup),
                'society': self._safe_extract_society(soup),
                'property_type': self._safe_extract_property_type(soup),
                'bhk': self._safe_extract_bhk(soup),
                'bathrooms': self._safe_extract_bathrooms(soup),
                'furnishing': self._safe_extract_furnishing(soup),
                'floor': self._safe_extract_floor(soup),
                'age': self._safe_extract_age(soup),
                'facing': self._safe_extract_facing(soup),
                'parking': self._safe_extract_parking(soup),
                'amenities': self._safe_extract_amenities(soup),
                'description': self._safe_extract_description(soup),
                'builder_info': self._safe_extract_builder_info(soup),
                'location_details': self._safe_extract_location_details(soup),
                'specifications': self._safe_extract_specifications(soup),
                'contact_info': self._safe_extract_contact_info(soup),
                'images': self._safe_extract_images(soup),
                'scraped_at': datetime.now().isoformat(),
                'property_id': self._extract_property_id(url)
            }
            
            # Validate extracted data
            if self._validate_extracted_data(property_data):
                self.consecutive_failures = 0  # Reset failure count on success
                return property_data
            else:
                self.logger.warning(f"Invalid data extracted for property {property_index}")
                return None
                
        except TimeoutException:
            self.logger.error(f"Timeout loading property {property_index}: {url}")
            self.consecutive_failures += 1
            return None
        except Exception as e:
            self.logger.error(f"Error scraping property {property_index}: {str(e)}")
            self.consecutive_failures += 1
            return None

    def _calculate_individual_page_delay(self, property_index: int, batch_size: int, city: str = None) -> float:
        """Calculate smart delay for individual property pages using custom configuration"""
        import random

        # Get city-specific delays if available
        if city and city.lower() in self.config.get('city_delays', {}):
            city_config = self.config['city_delays'][city.lower()]
            min_delay, max_delay = city_config.get('individual', (3, 8))
        else:
            # Use global configuration
            min_delay = self.config.get('individual_delay_min', 3)
            max_delay = self.config.get('individual_delay_max', 8)

        # Base delay using configured range
        base_delay = random.uniform(float(min_delay), float(max_delay))

        # Increase delay based on recent bot detection
        if hasattr(self, 'last_detection_time') and self.last_detection_time and (time.time() - self.last_detection_time) < 600:  # 10 minutes
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

    def _calculate_page_delay(self, page_number: int, city: str = None) -> float:
        """Calculate smart delay for page navigation using custom configuration"""
        import random

        # Get city-specific delays if available
        if city and city.lower() in self.config.get('city_delays', {}):
            city_config = self.config['city_delays'][city.lower()]
            min_delay, max_delay = city_config.get('page', (3, 8))
        else:
            # Use global configuration
            min_delay = self.config.get('page_delay_min', 3)
            max_delay = self.config.get('page_delay_max', 8)

        # Base delay using configured range
        base_delay = random.uniform(float(min_delay), float(max_delay))

        # Add progressive delay for later pages
        if page_number > 5:
            base_delay += random.uniform(0.5, 2.0)

        # Increase delay based on recent bot detection
        if hasattr(self, 'last_detection_time') and self.last_detection_time and (time.time() - self.last_detection_time) < 600:
            base_delay *= 1.5

        return base_delay

    def get_config_value(self, key: str, default=None):
        """Get a configuration value with fallback to default"""
        return self.config.get(key, default)

    def update_config(self, updates: Dict[str, Any]):
        """Update configuration values"""
        self.config.update(updates)
        self.logger.info(f"Configuration updated: {list(updates.keys())}")

    def _apply_property_filters(self, property_data: Dict[str, Any]) -> bool:
        """Apply filtering criteria to determine if property should be included"""

        if not self.config.get('enable_filtering', False):
            return True  # No filtering enabled, include all properties

        try:
            # Price filtering
            price_filter = self.config.get('price_filter', {})
            if price_filter.get('min') or price_filter.get('max'):
                price_text = property_data.get('price', '').lower()
                price_value = self._extract_numeric_price(price_text)

                if price_value:
                    if price_filter.get('min') and price_value < price_filter['min']:
                        return False
                    if price_filter.get('max') and price_value > price_filter['max']:
                        return False

            # Area filtering
            area_filter = self.config.get('area_filter', {})
            if area_filter.get('min') or area_filter.get('max'):
                area_text = property_data.get('area', '').lower()
                area_value = self._extract_numeric_area(area_text)

                if area_value:
                    if area_filter.get('min') and area_value < area_filter['min']:
                        return False
                    if area_filter.get('max') and area_value > area_filter['max']:
                        return False

            # Property type filtering
            property_type_filter = self.config.get('property_type_filter', [])
            if property_type_filter:
                property_type = property_data.get('property_type', '').lower()
                if not any(ptype.lower() in property_type for ptype in property_type_filter):
                    return False

            # BHK filtering
            bhk_filter = self.config.get('bhk_filter', [])
            if bhk_filter:
                title = property_data.get('title', '').lower()
                area = property_data.get('area', '').lower()
                combined_text = f"{title} {area}"

                bhk_found = False
                for bhk in bhk_filter:
                    if bhk.lower() in combined_text or f"{bhk} bhk" in combined_text:
                        bhk_found = True
                        break

                if not bhk_found:
                    return False

            # Location filtering
            location_filter = self.config.get('location_filter', [])
            if location_filter:
                locality = property_data.get('locality', '').lower()
                society = property_data.get('society', '').lower()
                combined_location = f"{locality} {society}"

                location_found = False
                for location in location_filter:
                    if location.lower() in combined_location:
                        location_found = True
                        break

                if not location_found:
                    return False

            # Exclude keywords filtering
            exclude_keywords = self.config.get('exclude_keywords', [])
            if exclude_keywords:
                title = property_data.get('title', '').lower()
                description = property_data.get('description', '').lower()
                combined_text = f"{title} {description}"

                for keyword in exclude_keywords:
                    if keyword.lower() in combined_text:
                        return False

            return True  # Passed all filters

        except Exception as e:
            self.logger.warning(f"Error applying filters: {str(e)}")
            return True  # Include property if filtering fails

    def _extract_numeric_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price value from price text"""
        import re

        # Remove common currency symbols and text
        price_text = re.sub(r'[₹,\s]', '', price_text)

        # Extract numbers and handle units (lakh, crore)
        if 'crore' in price_text.lower():
            numbers = re.findall(r'(\d+\.?\d*)', price_text)
            if numbers:
                return float(numbers[0]) * 10000000  # Convert crores to actual value
        elif 'lakh' in price_text.lower():
            numbers = re.findall(r'(\d+\.?\d*)', price_text)
            if numbers:
                return float(numbers[0]) * 100000  # Convert lakhs to actual value
        else:
            numbers = re.findall(r'(\d+\.?\d*)', price_text)
            if numbers:
                return float(numbers[0])

        return None

    def _extract_numeric_area(self, area_text: str) -> Optional[float]:
        """Extract numeric area value from area text"""
        import re

        # Extract numbers from area text
        numbers = re.findall(r'(\d+\.?\d*)', area_text)
        if numbers:
            return float(numbers[0])

        return None

    def get_filtered_properties_count(self) -> Dict[str, int]:
        """Get count of properties before and after filtering"""
        if not hasattr(self, '_filter_stats'):
            return {'total': 0, 'filtered': 0, 'excluded': 0}

        return self._filter_stats

    def _validate_and_clean_property_data(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean property data for quality assurance"""

        cleaned_data = property_data.copy()
        validation_issues = []

        try:
            # Clean and validate title
            title = cleaned_data.get('title', '').strip()
            if title:
                # Remove excessive whitespace and normalize
                title = ' '.join(title.split())
                # Remove common unwanted characters
                title = title.replace('\n', ' ').replace('\t', ' ')
                cleaned_data['title'] = title
            else:
                validation_issues.append('Missing title')

            # Clean and validate price
            price = cleaned_data.get('price', '').strip()
            if price:
                # Normalize price format
                price = price.replace('₹', '').replace(',', '').strip()
                # Validate price contains numbers
                if not any(char.isdigit() for char in price):
                    validation_issues.append('Invalid price format')
                cleaned_data['price'] = price
            else:
                validation_issues.append('Missing price')

            # Clean and validate area
            area = cleaned_data.get('area', '').strip()
            if area:
                # Normalize area format
                area = area.replace(',', '').strip()
                cleaned_data['area'] = area
            else:
                validation_issues.append('Missing area')

            # Validate and clean property URL
            url = cleaned_data.get('property_url', '').strip()
            if url:
                if not url.startswith('http'):
                    if url.startswith('/'):
                        cleaned_data['property_url'] = f"https://www.magicbricks.com{url}"
                    else:
                        validation_issues.append('Invalid URL format')
            else:
                validation_issues.append('Missing property URL')

            # Clean locality and society
            for field in ['locality', 'society']:
                value = cleaned_data.get(field, '').strip()
                if value:
                    # Remove excessive whitespace and normalize
                    value = ' '.join(value.split())
                    cleaned_data[field] = value

            # Validate numeric fields
            for field in ['bathrooms', 'balcony']:
                value = cleaned_data.get(field, '')
                if value and isinstance(value, str):
                    # Extract numeric value
                    import re
                    numbers = re.findall(r'\d+', value)
                    if numbers:
                        cleaned_data[field] = numbers[0]

            # Clean and validate posting date
            posting_date = cleaned_data.get('posting_date_text', '').strip()
            if posting_date:
                # Normalize date format
                posting_date = ' '.join(posting_date.split())
                cleaned_data['posting_date_text'] = posting_date

            # Add data quality score
            total_fields = len([k for k in cleaned_data.keys() if k not in ['scraped_at', 'session_id', 'page_number', 'property_index']])
            filled_fields = len([v for v in cleaned_data.values() if v and str(v).strip()])
            quality_score = (filled_fields / total_fields) * 100 if total_fields > 0 else 0

            cleaned_data['data_quality_score'] = round(quality_score, 1)
            cleaned_data['validation_issues'] = validation_issues
            cleaned_data['is_valid'] = len(validation_issues) == 0

            return cleaned_data

        except Exception as e:
            self.logger.warning(f"Error validating property data: {str(e)}")
            cleaned_data['validation_issues'] = validation_issues + [f"Validation error: {str(e)}"]
            cleaned_data['is_valid'] = False
            return cleaned_data

    def _validate_data_completeness(self, properties: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate overall data completeness and quality"""

        if not properties:
            return {
                'total_properties': 0,
                'valid_properties': 0,
                'data_quality_average': 0,
                'completeness_report': {}
            }

        total_properties = len(properties)
        valid_properties = len([p for p in properties if p.get('is_valid', False)])

        # Calculate field completeness
        field_completeness = {}
        essential_fields = ['title', 'price', 'area', 'property_url']

        for field in essential_fields:
            filled_count = len([p for p in properties if p.get(field) and str(p[field]).strip()])
            field_completeness[field] = (filled_count / total_properties) * 100 if total_properties > 0 else 0

        # Calculate average data quality score
        quality_scores = [p.get('data_quality_score', 0) for p in properties]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

        return {
            'total_properties': total_properties,
            'valid_properties': valid_properties,
            'validation_success_rate': (valid_properties / total_properties) * 100 if total_properties > 0 else 0,
            'data_quality_average': round(avg_quality, 1),
            'field_completeness': field_completeness,
            'completeness_report': {
                'excellent': len([p for p in properties if p.get('data_quality_score', 0) >= 90]),
                'good': len([p for p in properties if 70 <= p.get('data_quality_score', 0) < 90]),
                'fair': len([p for p in properties if 50 <= p.get('data_quality_score', 0) < 70]),
                'poor': len([p for p in properties if p.get('data_quality_score', 0) < 50])
            }
        }

    def _scrape_single_property_page(self, url: str, property_index: int, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Scrape a single property page with enhanced error handling and retry logic"""

        for attempt in range(max_retries):
            try:
                self.logger.info(f"   🔍 Scraping property {property_index} (attempt {attempt + 1}/{max_retries})")

                # Navigate with timeout and error handling
                try:
                    self.driver.set_page_load_timeout(30)  # 30 second timeout
                    self.driver.get(url)
                except Exception as nav_error:
                    self.logger.warning(f"   ⚠️ Navigation error on attempt {attempt + 1}: {str(nav_error)}")
                    if attempt < max_retries - 1:
                        time.sleep(5 * (attempt + 1))  # Progressive delay
                        continue
                    else:
                        raise nav_error

                # Check for bot detection
                page_source = self.driver.page_source
                current_url = self.driver.current_url

                if self._detect_bot_detection(page_source, current_url):
                    self.logger.warning(f"   🚨 Bot detection on property {property_index} (attempt {attempt + 1})")
                    if attempt < max_retries - 1:
                        self._handle_bot_detection()
                        continue
                    else:
                        return None

                # Validate page loaded correctly
                if not self._validate_property_page(driver.page_source):
                    self.logger.warning(f"   ⚠️ Invalid property page on attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        time.sleep(3 * (attempt + 1))
                        continue
                    else:
                        return None

                # Wait for page load with progressive timeout
                time.sleep(2 + attempt)

                # Extract detailed property data with error handling
                soup = BeautifulSoup(page_source, 'html.parser')

                property_data = {
                    'url': url,
                    'scraped_at': datetime.now().isoformat(),
                    'property_index': property_index,
                    'scrape_attempt': attempt + 1,
                    'title': self._safe_extract_property_title(soup),
                    'price': self._safe_extract_property_price(soup),
                    'area': self._safe_extract_property_area(soup),
                    'amenities': self._safe_extract_amenities(soup),
                    'description': self._safe_extract_description(soup),
                    'builder_info': self._safe_extract_builder_info(soup),
                    'location_details': self._safe_extract_location_details(soup),
                    'specifications': self._safe_extract_specifications(soup)
                }

                # Validate extracted data quality
                if self._validate_extracted_data(property_data):
                    self.logger.info(f"   ✅ Property {property_index} scraped successfully")
                    return property_data
                else:
                    self.logger.warning(f"   ⚠️ Poor data quality on attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        # Return partial data if it's the last attempt
                        self.logger.info(f"   📝 Returning partial data for property {property_index}")
                        return property_data

            except Exception as e:
                self.logger.error(f"   ❌ Error scraping property {property_index} (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    # Progressive delay with jitter
                    delay = (5 * (attempt + 1)) + random.uniform(1, 3)
                    self.logger.info(f"   ⏱️ Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)

                    # Try to recover browser state
                    try:
                        self.driver.refresh()
                        time.sleep(2)
                    except:
                        pass
                else:
                    self.logger.error(f"   ❌ Failed to scrape property {property_index} after {max_retries} attempts")
                    return None

        return None

    def _validate_property_page(self, page_source: str) -> bool:
        """Validate that the property page loaded correctly"""
        # Check for common property page indicators
        indicators = [
            'property', 'price', 'sqft', 'bedroom', 'bathroom',
            'magicbricks', 'contact', 'details'
        ]

        page_lower = page_source.lower()
        found_indicators = sum(1 for indicator in indicators if indicator in page_lower)

        # Require at least 3 indicators to consider page valid
        return found_indicators >= 3

    def _validate_extracted_data(self, property_data: Dict[str, Any]) -> bool:
        """Validate the quality of extracted property data"""
        # Check for essential fields
        essential_fields = ['title', 'price', 'area']
        filled_essential = sum(1 for field in essential_fields if property_data.get(field))

        # Check for additional fields
        additional_fields = ['amenities', 'description', 'builder_info', 'location_details']
        filled_additional = sum(1 for field in additional_fields if property_data.get(field))

        # Require at least 2 essential fields and 1 additional field
        return filled_essential >= 2 and filled_additional >= 1

    def _safe_extract_property_title(self, soup: BeautifulSoup) -> str:
        """Safely extract property title from individual page with fallbacks"""
        selectors = [
            'h1.mb-ldp__dtls__title',
            'h1[class*="title"]',
            '.property-title',
            'h1',
            '[class*="heading"]',
            '[class*="name"]'
        ]

        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text(strip=True)
                    if title and len(title) > 5:  # Ensure meaningful title
                        return title
            except Exception as e:
                self.logger.debug(f"Error extracting title with selector {selector}: {str(e)}")
                continue

        return ''

    def _extract_property_title(self, soup: BeautifulSoup) -> str:
        """Extract property title from individual page (legacy method)"""
        return self._safe_extract_property_title(soup)

    def _safe_extract_property_price(self, soup: BeautifulSoup) -> str:
        """Safely extract property price from individual page with fallbacks"""
        selectors = [
            '.mb-ldp__dtls__price',
            '[class*="price"]',
            '.property-price',
            '[class*="cost"]',
            '[class*="amount"]'
        ]

        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    price = element.get_text(strip=True)
                    # Validate price format (should contain numbers and currency indicators)
                    if price and any(char.isdigit() for char in price):
                        return price
            except Exception as e:
                self.logger.debug(f"Error extracting price with selector {selector}: {str(e)}")
                continue

        return ''

    def _extract_property_price(self, soup: BeautifulSoup) -> str:
        """Extract property price from individual page (legacy method)"""
        return self._safe_extract_property_price(soup)

    def _safe_extract_property_area(self, soup: BeautifulSoup) -> str:
        """Safely extract property area from individual page with fallbacks"""
        selectors = [
            '.mb-ldp__dtls__area',
            '[class*="area"]',
            '.property-area',
            '[class*="sqft"]',
            '[class*="size"]'
        ]

        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    area = element.get_text(strip=True)
                    # Validate area format (should contain numbers and area units)
                    if area and any(char.isdigit() for char in area):
                        return area
            except Exception as e:
                self.logger.debug(f"Error extracting area with selector {selector}: {str(e)}")
                continue

        return ''

    def _extract_property_area(self, soup: BeautifulSoup) -> str:
        """Extract property area from individual page (legacy method)"""
        return self._safe_extract_property_area(soup)

    def _safe_extract_amenities(self, soup: BeautifulSoup) -> List[str]:
        """Safely extract amenities from individual page with fallbacks"""
        amenities = []

        amenity_selectors = [
            '.mb-ldp__amenities li',
            '.amenities-list li',
            '[class*="amenity"]',
            '[class*="facility"] li',
            '[class*="feature"] li'
        ]

        for selector in amenity_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    amenity = element.get_text(strip=True)
                    if amenity and len(amenity) > 2 and amenity not in amenities:
                        amenities.append(amenity)
            except Exception as e:
                self.logger.debug(f"Error extracting amenities with selector {selector}: {str(e)}")
                continue

        return amenities

    def _safe_extract_description(self, soup: BeautifulSoup) -> str:
        """Safely extract property description from individual page with fallbacks"""
        selectors = [
            '.mb-ldp__dtls__desc',
            '.property-description',
            '[class*="description"]',
            '[class*="about"]',
            '[class*="detail"] p'
        ]

        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    description = element.get_text(strip=True)
                    if description and len(description) > 20:  # Ensure meaningful description
                        return description
            except Exception as e:
                self.logger.debug(f"Error extracting description with selector {selector}: {str(e)}")
                continue

        return ''

    def _safe_extract_builder_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Safely extract builder information from individual page with fallbacks"""
        builder_info = {}

        builder_selectors = [
            '.mb-ldp__builder__name',
            '.builder-name',
            '[class*="builder"]',
            '[class*="developer"]'
        ]

        for selector in builder_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    name = element.get_text(strip=True)
                    if name and len(name) > 2:
                        builder_info['name'] = name
                        break
            except Exception as e:
                self.logger.debug(f"Error extracting builder info with selector {selector}: {str(e)}")
                continue

        return builder_info

    def _safe_extract_location_details(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Safely extract detailed location information with fallbacks"""
        location_details = {}

        location_selectors = [
            '.mb-ldp__location',
            '.property-location',
            '[class*="location"]',
            '[class*="address"]'
        ]

        for selector in location_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    address = element.get_text(strip=True)
                    if address and len(address) > 5:
                        location_details['address'] = address
                        break
            except Exception as e:
                self.logger.debug(f"Error extracting location with selector {selector}: {str(e)}")
                continue

        return location_details

    def _safe_extract_specifications(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Safely extract detailed specifications with fallbacks"""
        specifications = {}

        spec_selectors = [
            '.mb-ldp__specs tr',
            '.specifications tr',
            '[class*="spec"] tr',
            '[class*="detail"] tr'
        ]

        for selector in spec_selectors:
            try:
                rows = soup.select(selector)
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        if key and value and len(key) > 1 and len(value) > 1:
                            specifications[key] = value
            except Exception as e:
                self.logger.debug(f"Error extracting specifications with selector {selector}: {str(e)}")
                continue

        return specifications

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

    def scrape_multiple_cities_parallel(self, cities: List[str], mode: ScrapingMode = ScrapingMode.INCREMENTAL,
                                      max_pages_per_city: int = None, include_individual_pages: bool = False,
                                      export_formats: List[str] = ['csv'], max_workers: int = 3) -> Dict[str, Any]:
        """
        Scrape multiple cities in parallel with proper resource management

        Args:
            cities: List of city names to scrape
            mode: Scraping mode for all cities
            max_pages_per_city: Maximum pages per city
            include_individual_pages: Whether to include individual property scraping
            export_formats: Export formats for each city
            max_workers: Maximum number of parallel workers (recommended: 2-4)

        Returns:
            Dict containing results for all cities
        """

        self.logger.info(f"[HOUSE] Starting parallel city scraping for {len(cities)} cities")
        self.logger.info(f"   [LIST] Cities: {', '.join(cities)}")
        self.logger.info(f"   [WORKERS] Workers: {max_workers}")
        self.logger.info(f"   [PAGES] Max pages per city: {max_pages_per_city}")
        self.logger.info(f"   [HOUSE] Individual pages: {include_individual_pages}")

        start_time = time.time()
        results = {}
        failed_cities = []

        # Thread-safe progress tracking
        progress_lock = threading.Lock()
        completed_cities = 0

        def scrape_single_city(city: str) -> Tuple[str, Dict[str, Any]]:
            """Scrape a single city in a separate thread"""
            nonlocal completed_cities

            try:
                # Create a separate scraper instance for this thread
                city_scraper = IntegratedMagicBricksScraper()

                self.logger.info(f"   [LIST] Starting {city} scraping...")

                result = city_scraper.scrape_properties_with_incremental(
                    city=city,
                    mode=mode,
                    max_pages=max_pages_per_city,
                    include_individual_pages=include_individual_pages,
                    export_formats=export_formats
                )

                # Update progress safely
                with progress_lock:
                    completed_cities += 1
                    self.logger.info(f"   [SUCCESS] {city} completed ({completed_cities}/{len(cities)})")

                return city, result

            except Exception as e:
                with progress_lock:
                    completed_cities += 1
                    self.logger.error(f"   [ERROR] {city} failed ({completed_cities}/{len(cities)}): {str(e)}")

                return city, {'success': False, 'error': str(e)}

        # Execute parallel scraping with controlled concurrency
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all city scraping tasks
            future_to_city = {executor.submit(scrape_single_city, city): city for city in cities}

            # Collect results as they complete
            for future in as_completed(future_to_city):
                city = future_to_city[future]
                try:
                    city_name, result = future.result()
                    results[city_name] = result

                    if not result.get('success', False):
                        failed_cities.append(city_name)

                except Exception as e:
                    self.logger.error(f"   [ERROR] Unexpected error for {city}: {str(e)}")
                    results[city] = {'success': False, 'error': str(e)}
                    failed_cities.append(city)

        # Calculate overall statistics
        total_duration = time.time() - start_time
        successful_cities = len(cities) - len(failed_cities)
        total_properties = sum(result.get('properties_scraped', 0) for result in results.values() if result.get('success'))
        total_pages = sum(result.get('pages_scraped', 0) for result in results.values() if result.get('success'))

        # Compile summary
        summary = {
            'success': len(failed_cities) == 0,
            'total_cities': len(cities),
            'successful_cities': successful_cities,
            'failed_cities': failed_cities,
            'total_properties_scraped': total_properties,
            'total_pages_scraped': total_pages,
            'total_duration': total_duration,
            'duration_formatted': f"{int(total_duration // 60)}m {int(total_duration % 60)}s",
            'average_properties_per_city': total_properties / successful_cities if successful_cities > 0 else 0,
            'properties_per_minute': (total_properties * 60) / total_duration if total_duration > 0 else 0,
            'parallel_efficiency': f"{(total_properties / total_duration) / max_workers:.1f} props/min/worker" if total_duration > 0 else "N/A",
            'city_results': results,
            'export_formats': export_formats,
            'parallel_workers': max_workers
        }

        # Log summary
        self.logger.info(f"\\n[HOUSE] PARALLEL CITY SCRAPING COMPLETE")
        self.logger.info(f"   [SUCCESS] Successful cities: {successful_cities}/{len(cities)}")
        self.logger.info(f"   [LIST] Total properties: {total_properties}")
        self.logger.info(f"   [TIMER] Total duration: {summary['duration_formatted']}")
        self.logger.info(f"   [ROCKET] Efficiency: {summary['parallel_efficiency']}")

        if failed_cities:
            self.logger.warning(f"   [ERROR] Failed cities: {', '.join(failed_cities)}")

        return summary

    def close(self):
        """Close the WebDriver"""

        if self.driver:
            self.driver.quit()
            self.logger.info("WebDriver closed")

    # Missing _safe_extract methods - simple fallback implementations
    def _safe_extract_locality(self, soup: BeautifulSoup) -> str:
        """Safely extract locality with fallbacks"""
        selectors = ['.mb-ldp__location', '[class*="locality"]', '[class*="location"]']
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)
            except:
                continue
        return 'N/A'

    def _safe_extract_society(self, soup: BeautifulSoup) -> str:
        """Safely extract society with fallbacks"""
        selectors = ['.mb-ldp__society', '[class*="society"]', '[class*="project"]']
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)
            except:
                continue
        return 'N/A'

    def _safe_extract_property_type(self, soup: BeautifulSoup) -> str:
        """Safely extract property type with fallbacks"""
        selectors = ['.mb-ldp__type', '[class*="type"]', '[class*="category"]']
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)
            except:
                continue
        return 'N/A'

    def _safe_extract_bhk(self, soup: BeautifulSoup) -> str:
        """Safely extract BHK with fallbacks"""
        selectors = ['.mb-ldp__bhk', '[class*="bhk"]', '[class*="bedroom"]']
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)
            except:
                continue
        return 'N/A'

    def _safe_extract_bathrooms(self, soup: BeautifulSoup) -> str:
        """Safely extract bathrooms with fallbacks"""
        selectors = ['.mb-ldp__bathroom', '[class*="bathroom"]', '[class*="bath"]']
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)
            except:
                continue
        return 'N/A'

    def _safe_extract_furnishing(self, soup: BeautifulSoup) -> str:
        """Safely extract furnishing with fallbacks"""
        selectors = ['.mb-ldp__furnishing', '[class*="furnish"]', '[class*="furniture"]']
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)
            except:
                continue
        return 'N/A'

    def _safe_extract_floor(self, soup: BeautifulSoup) -> str:
        """Safely extract floor with fallbacks"""
        selectors = ['.mb-ldp__floor', '[class*="floor"]']
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)
            except:
                continue
        return 'N/A'

    def _safe_extract_age(self, soup: BeautifulSoup) -> str:
        """Safely extract age with fallbacks"""
        selectors = ['.mb-ldp__age', '[class*="age"]', '[class*="year"]']
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)
            except:
                continue
        return 'N/A'

    def _safe_extract_facing(self, soup: BeautifulSoup) -> str:
        """Safely extract facing with fallbacks"""
        selectors = ['.mb-ldp__facing', '[class*="facing"]', '[class*="direction"]']
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)
            except:
                continue
        return 'N/A'

    def _safe_extract_parking(self, soup: BeautifulSoup) -> str:
        """Safely extract parking with fallbacks"""
        selectors = ['.mb-ldp__parking', '[class*="parking"]', '[class*="garage"]']
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)
            except:
                continue
        return 'N/A'

    def _safe_extract_contact_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Safely extract contact info with fallbacks"""
        contact_info = {}
        try:
            phone_selectors = ['.mb-ldp__contact', '[class*="phone"]', '[class*="contact"]']
            for selector in phone_selectors:
                element = soup.select_one(selector)
                if element:
                    contact_info['phone'] = element.get_text(strip=True)
                    break
        except:
            pass
        return contact_info

    def _safe_extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Safely extract images with fallbacks"""
        images = []
        try:
            img_selectors = ['.mb-ldp__gallery img', '[class*="gallery"] img', '[class*="image"] img']
            for selector in img_selectors:
                elements = soup.select(selector)
                for img in elements:
                    src = img.get('src') or img.get('data-src')
                    if src:
                        images.append(src)
                if images:
                    break
        except:
            pass
        return images[:10]  # Limit to 10 images
    
    def _extract_property_id(self, url: str) -> str:
        """Extract property ID from URL"""
        try:
            # Extract property ID from URL parts
            url_parts = url.split('/')
            for part in url_parts:
                if part.startswith('property'):
                    return part
            # If no property part found, try to extract from URL pattern
            import re
            match = re.search(r'property[^/]*-([^/]+)', url)
            if match:
                return match.group(1)
            # Fallback: use last part of URL
            return url_parts[-1] if url_parts else 'unknown'
        except Exception as e:
            self.logger.warning(f"Error extracting property ID from URL {url}: {str(e)}")
            return 'unknown'


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
