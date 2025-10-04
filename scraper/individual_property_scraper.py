#!/usr/bin/env python3
"""
Individual Property Scraper Module
Handles scraping of individual property pages with concurrent/sequential processing.
Extracted from integrated_magicbricks_scraper.py for better maintainability.
"""

import time
import random
import logging
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup


class IndividualPropertyScraper:
    """
    Handles individual property page scraping with concurrent and sequential modes
    """
    
    def __init__(self, driver, property_extractor, bot_handler, individual_tracker=None, logger=None, restart_callback=None):
        """
        Initialize individual property scraper

        Args:
            driver: Selenium WebDriver instance
            property_extractor: PropertyExtractor instance
            bot_handler: BotDetectionHandler instance
            individual_tracker: IndividualPropertyTracker instance (optional)
            logger: Logger instance
            restart_callback: Callable to restart the browser session (provided by parent)
        """
        self.driver = driver
        self.property_extractor = property_extractor
        self.bot_handler = bot_handler
        self.individual_tracker = individual_tracker
        self.logger = logger or logging.getLogger(__name__)
        self.restart_callback = restart_callback

    def scrape_individual_property_pages(self, property_urls: List[str], batch_size: int = 10,
                                        progress_callback: Optional[Callable] = None, 
                                        progress_data: Optional[Dict] = None,
                                        force_rescrape: bool = False,
                                        use_concurrent: bool = True,
                                        session_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Enhanced individual property page scraping with duplicate detection and concurrent processing
        
        Args:
            property_urls: List of property URLs to scrape
            batch_size: Number of properties to process in each batch
            progress_callback: Callback function for progress updates
            progress_data: Data to pass to progress callback
            force_rescrape: Force re-scraping of already scraped properties
            use_concurrent: Use concurrent processing (True) or sequential (False)
            session_id: Session ID for tracking
            
        Returns:
            List of detailed property dictionaries
        """
        
        if not property_urls:
            self.logger.warning("No property URLs provided for individual scraping")
            return []
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"INDIVIDUAL PROPERTY PAGE SCRAPING")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Total URLs: {len(property_urls)}")
        self.logger.info(f"Batch Size: {batch_size}")
        self.logger.info(f"Mode: {'Concurrent' if use_concurrent else 'Sequential'}")
        
        # Filter out already scraped URLs if tracker is available and not forcing rescrape
        urls_to_scrape = property_urls
        if self.individual_tracker and not force_rescrape:
            urls_to_scrape = []
            for url in property_urls:
                if not self.individual_tracker.is_property_scraped(url, session_id):
                    urls_to_scrape.append(url)
                else:
                    self.logger.debug(f"Skipping already scraped URL: {url}")
            
            self.logger.info(f"After duplicate filtering: {len(urls_to_scrape)} URLs to scrape")
        
        if not urls_to_scrape:
            self.logger.info("All properties already scraped. Use force_rescrape=True to re-scrape.")
            return []
        
        # Choose scraping method
        if use_concurrent:
            detailed_properties = self._scrape_individual_pages_concurrent_enhanced(
                urls_to_scrape, batch_size, progress_callback, progress_data, session_id
            )
        else:
            detailed_properties = self._scrape_individual_pages_sequential_enhanced(
                urls_to_scrape, batch_size, progress_callback, progress_data, session_id
            )
        
        return detailed_properties
    
    def _scrape_individual_pages_concurrent_enhanced(self, property_urls: List[str], batch_size: int,
                                                   progress_callback: Optional[Callable] = None, 
                                                   progress_data: Optional[Dict] = None,
                                                   session_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Enhanced concurrent scraping with tracking integration"""
        
        detailed_properties = []
        total_urls = len(property_urls)
        
        # Process in batches
        for batch_start in range(0, total_urls, batch_size):
            batch_end = min(batch_start + batch_size, total_urls)
            batch_urls = property_urls[batch_start:batch_end]
            
            self.logger.info(f"\n📦 Processing batch {batch_start//batch_size + 1}: URLs {batch_start+1}-{batch_end}")
            
            # Use ThreadPoolExecutor for concurrent scraping
            with ThreadPoolExecutor(max_workers=min(4, len(batch_urls))) as executor:
                future_to_url = {
                    executor.submit(self._scrape_single_property_enhanced, url, session_id): url 
                    for url in batch_urls
                }
                
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        property_details = future.result()
                        if property_details:
                            detailed_properties.append(property_details)
                            
                            # Mark as scraped in tracker
                            if self.individual_tracker:
                                self.individual_tracker.mark_property_scraped(url, session_id)
                            
                            # Progress callback
                            if progress_callback and progress_data:
                                progress_callback(progress_data)
                                
                    except Exception as e:
                        self.logger.error(f"Error scraping {url}: {str(e)}")
            
            # Inter-batch delay
            if batch_end < total_urls:
                delay = random.uniform(3.0, 6.0)
                self.logger.info(f"⏱️ Inter-batch delay: {delay:.1f} seconds")
                time.sleep(delay)
        
        return detailed_properties
    
    def _scrape_individual_pages_sequential_enhanced(self, property_urls: List[str], batch_size: int,
                                                   progress_callback: Optional[Callable] = None,
                                                   progress_data: Optional[Dict] = None,
                                                   session_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Enhanced sequential scraping with tracking integration"""
        
        detailed_properties = []
        total_urls = len(property_urls)
        
        for idx, url in enumerate(property_urls, 1):
            self.logger.info(f"\n🔍 Scraping individual property {idx}/{total_urls}: {url}")
            
            try:
                property_details = self._scrape_single_property_enhanced(url, session_id)
                
                if property_details:
                    detailed_properties.append(property_details)
                    
                    # Mark as scraped in tracker
                    if self.individual_tracker:
                        self.individual_tracker.mark_property_scraped(url, session_id)
                    
                    # Progress callback
                    if progress_callback and progress_data:
                        progress_callback(progress_data)
                
                # Delay between requests
                delay = self.bot_handler.calculate_enhanced_delay(idx, 4.0, 8.0)
                self.logger.info(f"⏱️ Waiting {delay:.1f} seconds before next property...")
                time.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"❌ Error scraping {url}: {str(e)}")
                continue
        
        return detailed_properties
    
    def _scrape_single_property_enhanced(self, property_url: str, session_id: Optional[int] = None,
                                        max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        Scrape a single property page with retry logic
        
        Args:
            property_url: Property URL to scrape
            session_id: Session ID for tracking
            max_retries: Maximum number of retry attempts
            
        Returns:
            Property details dictionary or None if failed
        """
        
        for attempt in range(max_retries):
            try:
                # Navigate to property page
                self.driver.get(property_url)
                time.sleep(random.uniform(2.0, 4.0))
                
                # Get page source
                page_source = self.driver.page_source
                current_url = self.driver.current_url
                
                # Check for bot detection
                if self.bot_handler.detect_bot_detection(page_source, current_url):
                    self.logger.warning(f"Bot detection on individual page: {property_url}")
                    self.bot_handler.handle_bot_detection(lambda: self._restart_driver())
                    continue
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Extract property details using property_extractor
                property_details = {
                    'property_url': property_url,
                    'title': self.property_extractor._safe_extract_property_title(soup),
                    'price': self.property_extractor._safe_extract_property_price(soup),
                    'area': self.property_extractor._safe_extract_property_area(soup),
                    'description': self.property_extractor._safe_extract_description(soup),
                    'amenities': ', '.join(self.property_extractor._safe_extract_amenities(soup)),
                    'builder_info': self.property_extractor._safe_extract_builder_info(soup),
                    'location_details': self.property_extractor._safe_extract_location_details(soup),
                    'specifications': self.property_extractor._safe_extract_specifications(soup)
                }
                
                # Validate extracted data
                if property_details.get('title') or property_details.get('price'):
                    self.logger.info(f"   ✅ Successfully scraped: {property_details.get('title', 'N/A')[:50]}")
                    return property_details
                else:
                    self.logger.warning(f"   ⚠️ No meaningful data extracted from {property_url}")
                    if attempt < max_retries - 1:
                        time.sleep(random.uniform(3.0, 5.0))
                        continue
                    
            except Exception as e:
                self.logger.error(f"   ❌ Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(3.0, 5.0))
                else:
                    self.logger.error(f"   ❌ Failed to scrape property after {max_retries} attempts")
                    return None
        
        return None
    
    def _restart_driver(self):
        """Restart driver using callback provided by parent class"""
        try:
            if callable(getattr(self, 'restart_callback', None)):
                self.logger.info("[RESTART] Restarting driver via parent callback...")
                self.restart_callback()
            else:
                self.logger.warning("Driver restart requested but no restart_callback provided")
        except Exception as e:
            self.logger.error(f"Driver restart failed: {e}")

    def calculate_individual_page_delay(self, property_index: int) -> float:
        """
        Calculate delay for individual property page scraping
        
        Args:
            property_index: Current property index
            
        Returns:
            Delay in seconds
        """
        return self.bot_handler.calculate_enhanced_delay(property_index, 4.0, 8.0)

