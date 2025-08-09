"""
Modern MagicBricks Scraper with React Support and Advanced Anti-Detection
Production-ready scraper with comprehensive error handling and detailed logging
"""

import json
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException,
    StaleElementReferenceException, ElementNotInteractableException
)
from bs4 import BeautifulSoup

from ..models.property_model import PropertyModel
from ..utils.logger import ScraperLogger


class ModernMagicBricksScraper:
    """
    Production-ready MagicBricks scraper with modern React support
    """
    
    def __init__(self, config_path: str = "config/scraper_config.json"):
        """Initialize scraper with configuration"""
        self.config = self._load_config(config_path)
        self.logger = ScraperLogger(self.config)
        self.driver = None
        self.wait = None
        
        # Session tracking
        self.current_page = 1
        self.total_properties_scraped = 0
        self.consecutive_failures = 0
        self.circuit_breaker_active = False
        
        # Data storage
        self.scraped_properties: List[PropertyModel] = []
        self.failed_extractions: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.page_load_times: List[float] = []
        self.extraction_times: List[float] = []
        
        self.logger.logger.info("🔧 Modern MagicBricks Scraper initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def _setup_browser(self) -> webdriver.Chrome:
        """Setup Chrome browser with advanced anti-detection"""
        chrome_options = Options()
        
        # Basic stealth options
        for option in self.config['browser']['chrome_options']:
            chrome_options.add_argument(option)
        
        # Headless mode
        if self.config['browser']['headless']:
            chrome_options.add_argument('--headless')
        
        # Random viewport size
        viewport = random.choice(self.config['browser']['viewport_sizes'])
        chrome_options.add_argument(f'--window-size={viewport["width"]},{viewport["height"]}')
        
        # Random user agent
        user_agent = random.choice(self.config['browser']['user_agents'])
        chrome_options.add_argument(f'--user-agent={user_agent}')
        
        # Advanced anti-detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Create driver
        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            # Execute stealth scripts
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": user_agent,
                "acceptLanguage": "en-US,en;q=0.9",
                "platform": "Win32"
            })
            
            # Set timeouts
            driver.set_page_load_timeout(self.config['delays']['page_timeout'])
            driver.implicitly_wait(self.config['delays']['element_wait_timeout'])
            
            self.logger.logger.info(f"🌐 Browser initialized with User-Agent: {user_agent[:50]}...")
            return driver
            
        except Exception as e:
            self.logger.log_error("BROWSER_SETUP", f"Failed to initialize browser: {str(e)}")
            raise
    
    def _wait_for_react_render(self):
        """Wait for React components to fully render"""
        try:
            # Wait for React to be available
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return typeof React !== 'undefined' || document.readyState === 'complete'")
            )
            
            # Additional wait for dynamic content
            time.sleep(self.config['delays']['react_render_wait'])
            
            # Wait for property cards to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.config['selectors']['property_cards']))
            )
            
        except TimeoutException:
            self.logger.log_error("REACT_RENDER", "Timeout waiting for React components to render")
            raise
    
    def _random_delay(self, min_delay: Optional[float] = None, max_delay: Optional[float] = None):
        """Add random delay to mimic human behavior"""
        if min_delay is None:
            min_delay = self.config['delays']['between_requests_min']
        if max_delay is None:
            max_delay = self.config['delays']['between_requests_max']
        
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _extract_property_data(self, property_element, position: int) -> Optional[PropertyModel]:
        """Extract comprehensive property data from a property card element"""
        try:
            property_data = PropertyModel()
            property_data.position_on_page = position
            property_data.page_number = self.current_page
            
            # Get HTML content for BeautifulSoup parsing
            html_content = property_element.get_attribute('outerHTML')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title (required field)
            title_element = soup.select_one(self.config['selectors']['title'])
            if title_element:
                property_data.title = title_element.get_text(strip=True)
            
            # Extract price (required field)
            price_selectors = self.config['selectors']['price']
            price_element = (soup.select_one(price_selectors['primary']) or 
                           soup.select_one(price_selectors['fallback']))
            
            if price_element:
                property_data.price = price_element.get_text(strip=True)
            else:
                # Try regex extraction from entire card
                price_match = re.search(price_selectors['regex'], html_content)
                if price_match:
                    property_data.price = price_match.group(0)
            
            # Extract price per sqft
            price_sqft_selectors = self.config['selectors']['price_per_sqft']
            price_sqft_element = (soup.select_one(price_sqft_selectors['primary']) or 
                                soup.select_one(price_sqft_selectors['fallback']))
            
            if price_sqft_element:
                property_data.price_per_sqft = price_sqft_element.get_text(strip=True)
            else:
                price_sqft_match = re.search(price_sqft_selectors['regex'], html_content)
                if price_sqft_match:
                    property_data.price_per_sqft = price_sqft_match.group(0)
            
            # Extract society/project name with enhanced fallbacks
            society_selectors = self.config['selectors']['society']
            if isinstance(society_selectors, dict):
                # Try primary selector first
                society_element = soup.select_one(society_selectors['primary'])
                if society_element:
                    property_data.society = society_element.get_text(strip=True)
                else:
                    # Try fallback selectors
                    for fallback_selector in society_selectors['fallback']:
                        society_element = soup.select_one(fallback_selector)
                        if society_element:
                            property_data.society = society_element.get_text(strip=True)
                            break
            else:
                # Legacy single selector
                society_element = soup.select_one(society_selectors)
                if society_element:
                    property_data.society = society_element.get_text(strip=True)
            
            # Enhanced area extraction based on research findings
            area_selectors = self.config['selectors']['area']
            all_text = soup.get_text()

            # Use regex patterns to find area data in the text
            for pattern in area_selectors['regex_patterns']:
                if 'Super Area' in pattern:
                    super_match = re.search(pattern, all_text, re.IGNORECASE)
                    if super_match:
                        property_data.super_area = super_match.group(1) if super_match.groups() else super_match.group(0)
                        break
                elif 'Carpet Area' in pattern:
                    carpet_match = re.search(pattern, all_text, re.IGNORECASE)
                    if carpet_match:
                        property_data.carpet_area = carpet_match.group(1) if carpet_match.groups() else carpet_match.group(0)
                        break
                else:
                    # General sqft pattern
                    area_match = re.search(pattern, all_text, re.IGNORECASE)
                    if area_match:
                        # Determine if it's super area or carpet area based on context
                        context_before = all_text[max(0, area_match.start()-50):area_match.start()]
                        if 'super' in context_before.lower():
                            property_data.super_area = area_match.group(0)
                        elif 'carpet' in context_before.lower():
                            property_data.carpet_area = area_match.group(0)
                        else:
                            # Default to super area if no context
                            if not property_data.super_area:
                                property_data.super_area = area_match.group(0)
                        break

            # If still no area found, try fallback selectors
            if not property_data.super_area and not property_data.carpet_area:
                for fallback_selector in area_selectors['fallback']:
                    try:
                        # Note: BeautifulSoup doesn't support :contains() so we'll search text
                        if ':contains(' in fallback_selector:
                            continue  # Skip CSS :contains() selectors
                        area_element = soup.select_one(fallback_selector)
                        if area_element:
                            area_text = area_element.get_text(strip=True)
                            if 'sqft' in area_text.lower():
                                property_data.super_area = area_text
                                break
                    except Exception:
                        continue
            
            # Extract bedrooms
            bedroom_selectors = self.config['selectors']['bedrooms']
            bedroom_element = soup.select_one(bedroom_selectors['primary'])
            if bedroom_element:
                bedroom_text = bedroom_element.get_text(strip=True)
                bedroom_match = re.search(r'(\d+)', bedroom_text)
                if bedroom_match:
                    property_data.bedrooms = int(bedroom_match.group(1))
            else:
                # Fallback: extract from title
                if property_data.title:
                    bedroom_match = re.search(bedroom_selectors['regex'], property_data.title)
                    if bedroom_match:
                        property_data.bedrooms = int(bedroom_match.group(1))
            
            # Extract other property details with enhanced handling
            detail_fields = [
                'bathrooms', 'floor', 'furnishing', 'facing',
                'overlooking', 'ownership', 'parking', 'balcony', 'age',
                'transaction_type', 'possession_date'
            ]

            for field in detail_fields:
                if field in self.config['selectors']:
                    element = soup.select_one(self.config['selectors'][field])
                    if element:
                        value = element.get_text(strip=True)
                        setattr(property_data, field, value)

            # Enhanced status extraction
            status_config = self.config['selectors']['status']
            if isinstance(status_config, dict):
                # Try primary selector first
                status_element = soup.select_one(status_config['primary'])
                if status_element:
                    property_data.status = status_element.get_text(strip=True)
                else:
                    # Try fallback selectors
                    for fallback_selector in status_config['fallback']:
                        status_element = soup.select_one(fallback_selector)
                        if status_element:
                            property_data.status = status_element.get_text(strip=True)
                            break

                    # If still no status, try regex patterns on entire card
                    if not property_data.status:
                        for pattern in status_config['regex_patterns']:
                            status_match = re.search(pattern, html_content, re.IGNORECASE)
                            if status_match:
                                property_data.status = status_match.group(0)
                                break
            else:
                # Legacy single selector
                status_element = soup.select_one(status_config)
                if status_element:
                    property_data.status = status_element.get_text(strip=True)
            
            # Extract image information
            image_element = soup.select_one(self.config['selectors']['image'])
            if image_element:
                property_data.image_url = image_element.get('src')
                
                # Extract image count from photo count indicator
                photo_count_element = soup.select_one('.mb-srp__card__photo__fig--count')
                if photo_count_element:
                    count_text = photo_count_element.get_text(strip=True)
                    count_match = re.search(r'(\d+)', count_text)
                    if count_match:
                        property_data.image_count = int(count_match.group(1))
            
            # Extract property URL
            url_element = soup.select_one(self.config['selectors']['property_url'])
            if url_element:
                property_data.property_url = url_element.get('href')
                if property_data.property_url and not property_data.property_url.startswith('http'):
                    property_data.property_url = 'https://www.magicbricks.com' + property_data.property_url
            
            # Extract owner information
            owner_element = soup.select_one(self.config['selectors']['owner_info'])
            if owner_element:
                owner_text = owner_element.get_text(strip=True)
                if 'Owner:' in owner_text:
                    property_data.owner_name = owner_text.replace('Owner:', '').strip()
                    property_data.owner_type = 'Owner'
                elif 'Agent:' in owner_text:
                    property_data.owner_name = owner_text.replace('Agent:', '').strip()
                    property_data.owner_type = 'Agent'
                else:
                    property_data.owner_name = owner_text
            
            # Extract description
            desc_element = soup.select_one(self.config['selectors']['description'])
            if desc_element:
                property_data.description = desc_element.get_text(strip=True)
            
            # Extract locality from title or other sources
            if property_data.title:
                # Try to extract locality from title pattern
                locality_match = re.search(r'in\s+([^,]+(?:\s+\w+)*)\s+Gurgaon', property_data.title, re.IGNORECASE)
                if locality_match:
                    property_data.locality = locality_match.group(1).strip()
            
            # Determine property type from title
            if property_data.title:
                title_lower = property_data.title.lower()
                if 'apartment' in title_lower or 'flat' in title_lower:
                    property_data.property_type = 'Apartment'
                elif 'villa' in title_lower:
                    property_data.property_type = 'Villa'
                elif 'plot' in title_lower or 'land' in title_lower:
                    property_data.property_type = 'Plot'
                elif 'floor' in title_lower:
                    property_data.property_type = 'Independent Floor'
                elif 'house' in title_lower:
                    property_data.property_type = 'House'
            
            # Log successful extraction
            self.logger.log_property_extraction(property_data.to_dict(), position, True)
            
            return property_data
            
        except Exception as e:
            self.logger.log_error("PROPERTY_EXTRACTION", f"Failed to extract property data: {str(e)}",
                                self.current_page, position)
            self.logger.log_property_extraction({}, position, False)
            return None

    def _scrape_page(self, page_url: str) -> Tuple[List[PropertyModel], int, int]:
        """
        Scrape a single page and return extracted properties
        Returns: (properties, properties_found, properties_extracted)
        """
        start_time = time.time()

        try:
            # Navigate to page
            self.logger.logger.debug(f"🔗 Navigating to: {page_url}")
            self.driver.get(page_url)

            # Wait for React to render
            self._wait_for_react_render()

            # Random delay to mimic human behavior
            self._random_delay()

            # Find all property cards
            property_cards = self.driver.find_elements(By.CSS_SELECTOR, self.config['selectors']['property_cards'])
            properties_found = len(property_cards)

            if properties_found == 0:
                self.logger.log_error("PAGE_SCRAPING", "No property cards found on page", self.current_page)
                return [], 0, 0

            self.logger.logger.debug(f"🏠 Found {properties_found} property cards")

            # Extract data from each property card
            extracted_properties = []

            for i, card in enumerate(property_cards, 1):
                try:
                    # Small delay between extractions
                    if i > 1:
                        time.sleep(random.uniform(0.1, 0.3))

                    property_data = self._extract_property_data(card, i)

                    if property_data and property_data.is_valid():
                        extracted_properties.append(property_data)
                    elif property_data:
                        # Property extracted but invalid
                        self.failed_extractions.append({
                            'page': self.current_page,
                            'position': i,
                            'reason': 'Invalid data (missing title or price)',
                            'data': property_data.to_dict()
                        })

                except StaleElementReferenceException:
                    self.logger.log_error("STALE_ELEMENT", f"Stale element reference for property {i}",
                                        self.current_page, i)
                    continue
                except Exception as e:
                    self.logger.log_error("PROPERTY_PROCESSING", f"Error processing property {i}: {str(e)}",
                                        self.current_page, i)
                    continue

            # Track page load time
            page_time = time.time() - start_time
            self.page_load_times.append(page_time)

            return extracted_properties, properties_found, len(extracted_properties)

        except TimeoutException:
            self.logger.log_error("PAGE_TIMEOUT", f"Page load timeout: {page_url}", self.current_page)
            return [], 0, 0
        except WebDriverException as e:
            self.logger.log_error("WEBDRIVER_ERROR", f"WebDriver error: {str(e)}", self.current_page)
            return [], 0, 0
        except Exception as e:
            self.logger.log_error("PAGE_SCRAPING", f"Unexpected error: {str(e)}", self.current_page)
            return [], 0, 0

    def _retry_with_backoff(self, func, *args, **kwargs):
        """Execute function with exponential backoff retry"""
        max_retries = self.config['retry']['max_retries']
        backoff_factor = self.config['retry']['backoff_factor']

        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries:
                    raise e

                wait_time = backoff_factor ** attempt
                self.logger.log_error("RETRY_ATTEMPT", f"Attempt {attempt + 1} failed: {str(e)}",
                                    retry_count=attempt + 1)
                self.logger.logger.info(f"⏳ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

    def _save_checkpoint(self):
        """Save current progress to checkpoint file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_file = self.config['output']['checkpoint_filename'].format(timestamp=timestamp)
        checkpoint_path = Path(self.config['output']['export_directory']) / checkpoint_file

        checkpoint_data = {
            'timestamp': datetime.now().isoformat(),
            'current_page': self.current_page,
            'total_properties': len(self.scraped_properties),
            'total_valid_properties': len([p for p in self.scraped_properties if p.is_valid()]),
            'consecutive_failures': self.consecutive_failures,
            'session_stats': self.logger.get_session_stats(),
            'checkpoint_file': str(checkpoint_path)
        }

        try:
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)

            self.logger.log_checkpoint(checkpoint_data)
            return checkpoint_path

        except Exception as e:
            self.logger.log_error("CHECKPOINT_SAVE", f"Failed to save checkpoint: {str(e)}")
            return None

    def _check_circuit_breaker(self):
        """Check if circuit breaker should be activated"""
        threshold = self.config['retry']['circuit_breaker_threshold']

        if self.consecutive_failures >= threshold:
            if not self.circuit_breaker_active:
                self.circuit_breaker_active = True
                self.logger.logger.error(f"🚨 CIRCUIT BREAKER ACTIVATED - {self.consecutive_failures} consecutive failures")
                self.logger.logger.error("🛑 Stopping scraper to prevent further issues")
            return True

        return False

    def scrape_all_pages(self, start_page: int = 1, max_pages: Optional[int] = None) -> Dict[str, Any]:
        """
        Main method to scrape all pages
        """
        try:
            # Initialize browser
            self.driver = self._setup_browser()
            self.wait = WebDriverWait(self.driver, self.config['delays']['element_wait_timeout'])

            # Set limits
            if max_pages is None:
                max_pages = self.config['website']['max_pages']

            self.current_page = start_page

            self.logger.logger.info(f"🚀 Starting scraping from page {start_page} to {max_pages}")

            # Main scraping loop
            while self.current_page <= max_pages:
                # Check circuit breaker
                if self._check_circuit_breaker():
                    break

                # Construct page URL
                if self.current_page == 1:
                    page_url = self.config['website']['base_url']
                else:
                    page_url = f"{self.config['website']['base_url']}?page={self.current_page}"

                # Log page start
                self.logger.log_page_start(self.current_page, page_url)

                try:
                    # Scrape page with retry
                    properties, found, extracted = self._retry_with_backoff(
                        self._scrape_page, page_url
                    )

                    # Process results
                    valid_properties = [p for p in properties if p.is_valid()]

                    # Add to collection
                    self.scraped_properties.extend(valid_properties)
                    self.total_properties_scraped += len(valid_properties)

                    # Log page completion
                    errors = found - extracted if found > 0 else 0
                    self.logger.log_page_complete(
                        self.current_page, found, extracted, len(valid_properties), errors
                    )

                    # Reset consecutive failures on success
                    if extracted > 0:
                        self.consecutive_failures = 0
                    else:
                        self.consecutive_failures += 1

                    # Save checkpoint periodically
                    if self.current_page % self.config['output']['checkpoint_interval'] == 0:
                        self._save_checkpoint()

                    # Check if we've reached the end
                    if found == 0:
                        self.logger.logger.info("📄 No more properties found. Reached end of listings.")
                        break

                    # Move to next page
                    self.current_page += 1

                    # Random delay between pages
                    self._random_delay(
                        self.config['delays']['page_load_min'],
                        self.config['delays']['page_load_max']
                    )

                except Exception as e:
                    self.consecutive_failures += 1
                    self.logger.log_error("PAGE_PROCESSING", f"Failed to process page {self.current_page}: {str(e)}",
                                        self.current_page)

                    # Check if we should stop
                    if self.consecutive_failures >= self.config['retry']['max_consecutive_failures']:
                        self.logger.logger.error(f"🛑 Too many consecutive failures ({self.consecutive_failures}). Stopping.")
                        break

                    # Move to next page anyway
                    self.current_page += 1

            # Final checkpoint
            self._save_checkpoint()

            # Export data
            output_files = self._export_data()

            # Log session completion
            self.logger.log_session_complete(len(self.scraped_properties), output_files)

            return {
                'success': True,
                'total_properties': len(self.scraped_properties),
                'valid_properties': len([p for p in self.scraped_properties if p.is_valid()]),
                'pages_processed': self.current_page - start_page,
                'output_files': output_files,
                'session_stats': self.logger.get_session_stats()
            }

        except Exception as e:
            self.logger.log_error("SCRAPING_SESSION", f"Critical error in scraping session: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'total_properties': len(self.scraped_properties),
                'pages_processed': self.current_page - start_page if hasattr(self, 'current_page') else 0
            }

        finally:
            # Cleanup
            if self.driver:
                try:
                    self.driver.quit()
                    self.logger.logger.info("🔧 Browser closed successfully")
                except Exception as e:
                    self.logger.logger.error(f"❌ Error closing browser: {str(e)}")

    def _export_data(self) -> Dict[str, str]:
        """Export scraped data to CSV and JSON formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(self.config['output']['export_directory'])
        output_dir.mkdir(exist_ok=True)

        output_files = {}

        try:
            # Export to CSV
            csv_filename = self.config['output']['csv_filename'].format(timestamp=timestamp)
            csv_path = output_dir / csv_filename

            if self.scraped_properties:
                import pandas as pd

                # Convert to DataFrame
                data_rows = [prop.to_csv_row() for prop in self.scraped_properties]
                df = pd.DataFrame(data_rows)

                # Save CSV
                df.to_csv(csv_path, index=False, encoding='utf-8')
                output_files['CSV'] = str(csv_path)
                self.logger.logger.info(f"📊 CSV exported: {csv_path}")

            # Export to JSON
            json_filename = self.config['output']['json_filename'].format(timestamp=timestamp)
            json_path = output_dir / json_filename

            json_data = {
                'metadata': {
                    'export_timestamp': datetime.now().isoformat(),
                    'total_properties': len(self.scraped_properties),
                    'valid_properties': len([p for p in self.scraped_properties if p.is_valid()]),
                    'scraping_session': self.logger.get_session_stats()
                },
                'properties': [prop.to_dict() for prop in self.scraped_properties]
            }

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            output_files['JSON'] = str(json_path)
            self.logger.logger.info(f"📋 JSON exported: {json_path}")

        except Exception as e:
            self.logger.log_error("DATA_EXPORT", f"Failed to export data: {str(e)}")

        return output_files


# Export for easy import
__all__ = ['ModernMagicBricksScraper']
