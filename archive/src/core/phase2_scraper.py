#!/usr/bin/env python3
"""
Phase II Scraper - Detailed Property Page Scraping
Implements URL queue management and parallel processing for detailed property data extraction.
"""

import time
import json
import uuid
import random
import threading
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from pathlib import Path
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
import re

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# BeautifulSoup for parsing
from bs4 import BeautifulSoup

try:
    from .modern_scraper import ModernMagicBricksScraper
    from ..models.property_model import PropertyModel
    from ..utils.logger import ScraperLogger
    from ..database.database_manager import DatabaseManager
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from core.modern_scraper import ModernMagicBricksScraper
    from models.property_model import PropertyModel
    from utils.logger import ScraperLogger
    from database.database_manager import DatabaseManager


class URLQueueManager:
    """
    Manages URL queue for detailed property page scraping
    Handles URL discovery, deduplication, and processing status
    """
    
    def __init__(self, max_queue_size: int = 10000):
        """Initialize URL queue manager"""
        self.pending_urls = Queue(maxsize=max_queue_size)
        self.processing_urls = set()
        self.completed_urls = set()
        self.failed_urls = set()
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'urls_discovered': 0,
            'urls_processed': 0,
            'urls_failed': 0,
            'duplicate_urls_filtered': 0
        }
    
    def add_url(self, url: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add URL to processing queue"""
        with self.lock:
            # Check for duplicates
            if url in self.completed_urls or url in self.processing_urls or url in self.failed_urls:
                self.stats['duplicate_urls_filtered'] += 1
                return False
            
            try:
                self.pending_urls.put((url, metadata or {}), block=False)
                self.stats['urls_discovered'] += 1
                return True
            except:
                return False  # Queue full
    
    def get_next_url(self, timeout: float = 1.0) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Get next URL for processing"""
        try:
            url, metadata = self.pending_urls.get(timeout=timeout)
            with self.lock:
                self.processing_urls.add(url)
            return url, metadata
        except Empty:
            return None
    
    def mark_completed(self, url: str):
        """Mark URL as completed"""
        with self.lock:
            self.processing_urls.discard(url)
            self.completed_urls.add(url)
            self.stats['urls_processed'] += 1
    
    def mark_failed(self, url: str):
        """Mark URL as failed"""
        with self.lock:
            self.processing_urls.discard(url)
            self.failed_urls.add(url)
            self.stats['urls_failed'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        with self.lock:
            return {
                'pending': self.pending_urls.qsize(),
                'processing': len(self.processing_urls),
                'completed': len(self.completed_urls),
                'failed': len(self.failed_urls),
                **self.stats
            }
    
    def is_empty(self) -> bool:
        """Check if queue is empty and no URLs are processing"""
        with self.lock:
            return self.pending_urls.empty() and len(self.processing_urls) == 0


class DetailedPropertyExtractor:
    """
    Extracts detailed information from individual property pages
    Handles complex property details not available on listing pages
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize detailed property extractor"""
        self.config = config
        self.detailed_selectors = self._load_detailed_selectors()
    
    def _load_detailed_selectors(self) -> Dict[str, Any]:
        """Load selectors for detailed property pages"""
        return {
            'property_details': {
                'overview': '.mb-ldp__dtls__body',
                'price_details': '.mb-ldp__price__dtls',
                'amenities': '.mb-ldp__amenities',
                'location': '.mb-ldp__location',
                'floor_plan': '.mb-ldp__floorplan',
                'gallery': '.mb-ldp__gallery'
            },
            'detailed_fields': {
                'property_id': '[data-testid="property-id"]',
                'rera_id': '[data-testid="rera-id"]',
                'builder_name': '.mb-ldp__builder__name',
                'project_details': '.mb-ldp__project__dtls',
                'possession_date': '.mb-ldp__possession',
                'price_breakdown': '.mb-ldp__price__breakdown',
                'maintenance_charges': '.mb-ldp__maintenance',
                'booking_amount': '.mb-ldp__booking',
                'loan_details': '.mb-ldp__loan',
                'nearby_places': '.mb-ldp__nearby',
                'connectivity': '.mb-ldp__connectivity',
                'schools': '.mb-ldp__schools',
                'hospitals': '.mb-ldp__hospitals',
                'shopping': '.mb-ldp__shopping'
            }
        }
    
    def extract_detailed_data(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract detailed data from property page"""
        detailed_data = {
            'source_url': url,
            'extracted_at': datetime.now().isoformat(),
            'extraction_success': False
        }
        
        try:
            # Extract basic property details
            detailed_data.update(self._extract_property_overview(soup))
            
            # Extract price details
            detailed_data.update(self._extract_price_details(soup))
            
            # Extract amenities
            detailed_data.update(self._extract_amenities(soup))
            
            # Extract location details
            detailed_data.update(self._extract_location_details(soup))
            
            # Extract nearby places
            detailed_data.update(self._extract_nearby_places(soup))
            
            # Extract additional details
            detailed_data.update(self._extract_additional_details(soup))
            
            detailed_data['extraction_success'] = True
            
        except Exception as e:
            detailed_data['extraction_error'] = str(e)
        
        return detailed_data
    
    def _extract_property_overview(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract property overview details"""
        overview = {}
        
        try:
            # Property ID
            prop_id_elem = soup.select_one(self.detailed_selectors['detailed_fields']['property_id'])
            if prop_id_elem:
                overview['property_id'] = prop_id_elem.get_text(strip=True)
            
            # RERA ID
            rera_elem = soup.select_one(self.detailed_selectors['detailed_fields']['rera_id'])
            if rera_elem:
                overview['rera_id'] = rera_elem.get_text(strip=True)
            
            # Builder name
            builder_elem = soup.select_one(self.detailed_selectors['detailed_fields']['builder_name'])
            if builder_elem:
                overview['builder_name'] = builder_elem.get_text(strip=True)
            
            # Possession date
            possession_elem = soup.select_one(self.detailed_selectors['detailed_fields']['possession_date'])
            if possession_elem:
                overview['possession_date'] = possession_elem.get_text(strip=True)
        
        except Exception as e:
            overview['overview_extraction_error'] = str(e)
        
        return overview
    
    def _extract_price_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract detailed price information"""
        price_details = {}
        
        try:
            # Price breakdown
            breakdown_elem = soup.select_one(self.detailed_selectors['detailed_fields']['price_breakdown'])
            if breakdown_elem:
                price_details['price_breakdown'] = breakdown_elem.get_text(strip=True)
            
            # Maintenance charges
            maintenance_elem = soup.select_one(self.detailed_selectors['detailed_fields']['maintenance_charges'])
            if maintenance_elem:
                price_details['maintenance_charges'] = maintenance_elem.get_text(strip=True)
            
            # Booking amount
            booking_elem = soup.select_one(self.detailed_selectors['detailed_fields']['booking_amount'])
            if booking_elem:
                price_details['booking_amount'] = booking_elem.get_text(strip=True)
        
        except Exception as e:
            price_details['price_extraction_error'] = str(e)
        
        return price_details
    
    def _extract_amenities(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract detailed amenities list"""
        amenities_data = {}
        
        try:
            amenities_section = soup.select_one(self.detailed_selectors['property_details']['amenities'])
            if amenities_section:
                # Extract all amenity items
                amenity_items = amenities_section.find_all(['li', 'span', 'div'], class_=re.compile(r'amenity|feature'))
                amenities_list = [item.get_text(strip=True) for item in amenity_items if item.get_text(strip=True)]
                
                amenities_data['detailed_amenities'] = amenities_list
                amenities_data['amenities_count'] = len(amenities_list)
        
        except Exception as e:
            amenities_data['amenities_extraction_error'] = str(e)
        
        return amenities_data
    
    def _extract_location_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract detailed location information"""
        location_data = {}
        
        try:
            location_section = soup.select_one(self.detailed_selectors['property_details']['location'])
            if location_section:
                # Extract coordinates if available
                coords_pattern = r'lat[:\s]*([0-9.-]+).*lng[:\s]*([0-9.-]+)'
                coords_match = re.search(coords_pattern, location_section.get_text())
                if coords_match:
                    location_data['latitude'] = coords_match.group(1)
                    location_data['longitude'] = coords_match.group(2)
                
                # Extract address details
                address_elem = location_section.find(text=re.compile(r'address|location', re.I))
                if address_elem:
                    location_data['detailed_address'] = address_elem.strip()
        
        except Exception as e:
            location_data['location_extraction_error'] = str(e)
        
        return location_data
    
    def _extract_nearby_places(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract nearby places and connectivity"""
        nearby_data = {}
        
        try:
            # Schools
            schools_elem = soup.select_one(self.detailed_selectors['detailed_fields']['schools'])
            if schools_elem:
                schools = [item.get_text(strip=True) for item in schools_elem.find_all(['li', 'div'])]
                nearby_data['nearby_schools'] = schools
            
            # Hospitals
            hospitals_elem = soup.select_one(self.detailed_selectors['detailed_fields']['hospitals'])
            if hospitals_elem:
                hospitals = [item.get_text(strip=True) for item in hospitals_elem.find_all(['li', 'div'])]
                nearby_data['nearby_hospitals'] = hospitals
            
            # Shopping
            shopping_elem = soup.select_one(self.detailed_selectors['detailed_fields']['shopping'])
            if shopping_elem:
                shopping = [item.get_text(strip=True) for item in shopping_elem.find_all(['li', 'div'])]
                nearby_data['nearby_shopping'] = shopping
            
            # Connectivity
            connectivity_elem = soup.select_one(self.detailed_selectors['detailed_fields']['connectivity'])
            if connectivity_elem:
                nearby_data['connectivity_details'] = connectivity_elem.get_text(strip=True)
        
        except Exception as e:
            nearby_data['nearby_extraction_error'] = str(e)
        
        return nearby_data
    
    def _extract_additional_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract additional property details"""
        additional_data = {}
        
        try:
            # Loan details
            loan_elem = soup.select_one(self.detailed_selectors['detailed_fields']['loan_details'])
            if loan_elem:
                additional_data['loan_details'] = loan_elem.get_text(strip=True)
            
            # Project details
            project_elem = soup.select_one(self.detailed_selectors['detailed_fields']['project_details'])
            if project_elem:
                additional_data['project_details'] = project_elem.get_text(strip=True)
            
            # Extract any additional structured data
            script_tags = soup.find_all('script', type='application/ld+json')
            for script in script_tags:
                try:
                    structured_data = json.loads(script.string)
                    if '@type' in structured_data and 'RealEstate' in str(structured_data.get('@type', '')):
                        additional_data['structured_data'] = structured_data
                        break
                except:
                    continue
        
        except Exception as e:
            additional_data['additional_extraction_error'] = str(e)
        
        return additional_data


class Phase2Scraper(ModernMagicBricksScraper):
    """
    Phase II Scraper for detailed property page extraction
    Combines listing page URL discovery with detailed property page scraping
    """

    def __init__(self, config_path: str = "config/scraper_config.json",
                 db_path: str = "data/magicbricks_phase2.db", max_workers: int = 3):
        """Initialize Phase II scraper"""
        super().__init__(config_path)

        # Phase II components
        self.url_queue = URLQueueManager()
        self.detail_extractor = DetailedPropertyExtractor(self.config)
        self.max_workers = max_workers

        # Database for detailed data
        self.db_manager = DatabaseManager(db_path)

        # Phase II statistics
        self.phase2_stats = {
            'urls_discovered': 0,
            'detailed_pages_scraped': 0,
            'detailed_extraction_errors': 0,
            'total_detailed_data_points': 0
        }

    def discover_property_urls(self, start_page: int = 1, max_pages: int = 10) -> int:
        """
        Phase 1: Discover property URLs from listing pages
        Returns number of URLs discovered
        """
        self.logger.logger.info(f"🔍 Phase 1: Discovering property URLs from {max_pages} listing pages")

        # Initialize browser for URL discovery
        self.driver = self._setup_browser()
        self.wait = WebDriverWait(self.driver, self.config['delays']['element_wait_timeout'])

        urls_discovered = 0

        try:
            for page_num in range(start_page, start_page + max_pages):
                try:
                    # Navigate to listing page
                    if page_num == 1:
                        page_url = self.config['website']['base_url']
                    else:
                        page_url = f"{self.config['website']['base_url']}?page={page_num}"

                    self.logger.logger.info(f"🔍 Discovering URLs from page {page_num}")
                    self.driver.get(page_url)

                    # Wait for page load
                    time.sleep(random.uniform(2, 4))

                    # Extract property URLs
                    page_urls = self._extract_property_urls_from_page()

                    # Add URLs to queue
                    for url, metadata in page_urls:
                        if self.url_queue.add_url(url, metadata):
                            urls_discovered += 1

                    self.logger.logger.info(f"✅ Page {page_num}: Found {len(page_urls)} property URLs")

                    # Delay between pages
                    time.sleep(random.uniform(3, 6))

                except Exception as e:
                    self.logger.log_error("URL_DISCOVERY", f"Failed to discover URLs from page {page_num}: {str(e)}")
                    continue

        finally:
            if self.driver:
                self.driver.quit()

        self.phase2_stats['urls_discovered'] = urls_discovered
        self.logger.logger.info(f"🎯 Phase 1 Complete: Discovered {urls_discovered} property URLs")

        return urls_discovered

    def _extract_property_urls_from_page(self) -> List[Tuple[str, Dict[str, Any]]]:
        """Extract property URLs and metadata from current listing page"""
        property_urls = []

        try:
            # Get page source
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Find property cards
            property_cards = soup.select(self.config['selectors']['property_cards'])

            for i, card in enumerate(property_cards):
                try:
                    # Extract property URL
                    url_elem = card.select_one('a[href*="/propertydetail/"]')
                    if not url_elem:
                        url_elem = card.select_one('a[href*="/property-detail/"]')
                    if not url_elem:
                        url_elem = card.select_one('a[href*="pdpid"]')

                    if url_elem:
                        relative_url = url_elem.get('href')
                        if relative_url:
                            # Convert to absolute URL
                            full_url = urljoin(self.config['website']['base_url'], relative_url)

                            # Extract basic metadata from listing card
                            metadata = self._extract_listing_metadata(card, i + 1)

                            property_urls.append((full_url, metadata))

                except Exception as e:
                    self.logger.log_error("URL_EXTRACTION", f"Failed to extract URL from card {i+1}: {str(e)}")
                    continue

        except Exception as e:
            self.logger.log_error("PAGE_URL_EXTRACTION", f"Failed to extract URLs from page: {str(e)}")

        return property_urls

    def _extract_listing_metadata(self, card_soup: BeautifulSoup, position: int) -> Dict[str, Any]:
        """Extract basic metadata from listing card"""
        metadata = {
            'position_on_page': position,
            'discovered_at': datetime.now().isoformat()
        }

        try:
            # Extract basic info that might be useful for prioritization
            title_elem = card_soup.select_one('h2, .mb-srp__card__title')
            if title_elem:
                metadata['listing_title'] = title_elem.get_text(strip=True)

            price_elem = card_soup.select_one('[class*="price"]')
            if price_elem:
                metadata['listing_price'] = price_elem.get_text(strip=True)

            locality_elem = card_soup.select_one('[class*="locality"], [class*="location"]')
            if locality_elem:
                metadata['listing_locality'] = locality_elem.get_text(strip=True)

        except Exception as e:
            metadata['metadata_extraction_error'] = str(e)

        return metadata

    def scrape_detailed_properties(self, max_workers: Optional[int] = None) -> Dict[str, Any]:
        """
        Phase 2: Scrape detailed property pages using parallel processing
        """
        if max_workers is None:
            max_workers = self.max_workers

        self.logger.logger.info(f"🚀 Phase 2: Starting detailed property scraping with {max_workers} workers")

        detailed_properties = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit initial batch of workers
            futures = []

            for worker_id in range(max_workers):
                future = executor.submit(self._detailed_scraping_worker, worker_id)
                futures.append(future)

            # Collect results
            for future in as_completed(futures):
                try:
                    worker_results = future.result()
                    detailed_properties.extend(worker_results)
                except Exception as e:
                    self.logger.log_error("WORKER_ERROR", f"Worker failed: {str(e)}")

        # Store results in database
        if detailed_properties:
            self._store_detailed_properties(detailed_properties)

        # Generate summary
        summary = {
            'success': True,
            'urls_discovered': self.phase2_stats['urls_discovered'],
            'detailed_pages_scraped': self.phase2_stats['detailed_pages_scraped'],
            'extraction_errors': self.phase2_stats['detailed_extraction_errors'],
            'total_detailed_properties': len(detailed_properties),
            'queue_stats': self.url_queue.get_stats()
        }

        self.logger.logger.info(f"🎯 Phase 2 Complete: Scraped {len(detailed_properties)} detailed properties")

        return summary

    def _detailed_scraping_worker(self, worker_id: int) -> List[Dict[str, Any]]:
        """Worker function for detailed property scraping"""
        worker_results = []

        # Setup browser for this worker
        driver = self._setup_browser()

        try:
            self.logger.logger.info(f"👷 Worker {worker_id}: Starting detailed scraping")

            while True:
                # Get next URL from queue
                url_data = self.url_queue.get_next_url(timeout=5.0)
                if url_data is None:
                    # No more URLs or timeout
                    if self.url_queue.is_empty():
                        break
                    continue

                url, metadata = url_data

                try:
                    # Scrape detailed property page
                    detailed_data = self._scrape_single_detailed_property(driver, url, metadata)

                    if detailed_data:
                        worker_results.append(detailed_data)
                        self.phase2_stats['detailed_pages_scraped'] += 1
                        self.url_queue.mark_completed(url)

                        self.logger.logger.info(f"👷 Worker {worker_id}: Scraped {url}")
                    else:
                        self.phase2_stats['detailed_extraction_errors'] += 1
                        self.url_queue.mark_failed(url)

                except Exception as e:
                    self.phase2_stats['detailed_extraction_errors'] += 1
                    self.url_queue.mark_failed(url)
                    self.logger.log_error("DETAILED_SCRAPING", f"Worker {worker_id} failed to scrape {url}: {str(e)}")

                # Delay between requests
                time.sleep(random.uniform(2, 5))

        finally:
            driver.quit()
            self.logger.logger.info(f"👷 Worker {worker_id}: Completed with {len(worker_results)} properties")

        return worker_results

    def _scrape_single_detailed_property(self, driver: webdriver.Chrome, url: str,
                                       metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Scrape a single detailed property page"""
        try:
            # Navigate to property page
            driver.get(url)

            # Wait for page load
            time.sleep(random.uniform(3, 6))

            # Get page source and parse
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Extract detailed data
            detailed_data = self.detail_extractor.extract_detailed_data(soup, url)

            # Merge with listing metadata
            detailed_data.update(metadata)

            return detailed_data

        except Exception as e:
            self.logger.log_error("SINGLE_PROPERTY_SCRAPING", f"Failed to scrape {url}: {str(e)}")
            return None

    def _store_detailed_properties(self, detailed_properties: List[Dict[str, Any]]):
        """Store detailed properties in database"""
        try:
            # Create detailed properties table if needed
            self._create_detailed_properties_table()

            # Store properties
            for prop_data in detailed_properties:
                self._store_single_detailed_property(prop_data)

            self.logger.logger.info(f"✅ Stored {len(detailed_properties)} detailed properties in database")

        except Exception as e:
            self.logger.log_error("DATABASE_STORAGE", f"Failed to store detailed properties: {str(e)}")

    def _create_detailed_properties_table(self):
        """Create table for detailed property data"""
        cursor = self.db_manager.connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detailed_properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_url TEXT UNIQUE NOT NULL,
                property_id TEXT,
                rera_id TEXT,
                builder_name TEXT,
                possession_date TEXT,
                price_breakdown TEXT,
                maintenance_charges TEXT,
                booking_amount TEXT,
                detailed_amenities TEXT,
                amenities_count INTEGER,
                latitude TEXT,
                longitude TEXT,
                detailed_address TEXT,
                nearby_schools TEXT,
                nearby_hospitals TEXT,
                nearby_shopping TEXT,
                connectivity_details TEXT,
                loan_details TEXT,
                project_details TEXT,
                structured_data TEXT,
                listing_metadata TEXT,
                extracted_at TIMESTAMP,
                extraction_success BOOLEAN,
                extraction_error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.db_manager.connection.commit()

    def _store_single_detailed_property(self, prop_data: Dict[str, Any]):
        """Store single detailed property in database"""
        cursor = self.db_manager.connection.cursor()

        # Prepare data for insertion
        insert_data = {
            'source_url': prop_data.get('source_url'),
            'property_id': prop_data.get('property_id'),
            'rera_id': prop_data.get('rera_id'),
            'builder_name': prop_data.get('builder_name'),
            'possession_date': prop_data.get('possession_date'),
            'price_breakdown': prop_data.get('price_breakdown'),
            'maintenance_charges': prop_data.get('maintenance_charges'),
            'booking_amount': prop_data.get('booking_amount'),
            'detailed_amenities': json.dumps(prop_data.get('detailed_amenities', [])),
            'amenities_count': prop_data.get('amenities_count', 0),
            'latitude': prop_data.get('latitude'),
            'longitude': prop_data.get('longitude'),
            'detailed_address': prop_data.get('detailed_address'),
            'nearby_schools': json.dumps(prop_data.get('nearby_schools', [])),
            'nearby_hospitals': json.dumps(prop_data.get('nearby_hospitals', [])),
            'nearby_shopping': json.dumps(prop_data.get('nearby_shopping', [])),
            'connectivity_details': prop_data.get('connectivity_details'),
            'loan_details': prop_data.get('loan_details'),
            'project_details': prop_data.get('project_details'),
            'structured_data': json.dumps(prop_data.get('structured_data', {})),
            'listing_metadata': json.dumps({k: v for k, v in prop_data.items() if k.startswith('listing_')}),
            'extracted_at': prop_data.get('extracted_at'),
            'extraction_success': prop_data.get('extraction_success', False),
            'extraction_error': prop_data.get('extraction_error')
        }

        # Insert into database
        placeholders = ', '.join(['?' for _ in insert_data.keys()])
        columns = ', '.join(insert_data.keys())

        cursor.execute(f"""
            INSERT OR REPLACE INTO detailed_properties ({columns})
            VALUES ({placeholders})
        """, list(insert_data.values()))

        self.db_manager.connection.commit()


# Export for easy import
__all__ = ['URLQueueManager', 'DetailedPropertyExtractor', 'Phase2Scraper']
