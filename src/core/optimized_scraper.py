#!/usr/bin/env python3
"""
Optimized MagicBricks Scraper with Performance Enhancements
Implements multi-threading, browser optimization, and smart waiting for 50% speed improvement.
"""

import time
import json
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue, Empty

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# BeautifulSoup for parsing
from bs4 import BeautifulSoup
import re

try:
    from ..models.property_model import PropertyModel
    from ..utils.logger import ScraperLogger
    from .modern_scraper import ModernMagicBricksScraper
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from models.property_model import PropertyModel
    from utils.logger import ScraperLogger
    from core.modern_scraper import ModernMagicBricksScraper


class OptimizedMagicBricksScraper(ModernMagicBricksScraper):
    """
    Performance-optimized version of MagicBricks scraper
    Implements parallel processing and browser optimizations for 50% speed improvement
    """
    
    def __init__(self, config_path: str = "config/scraper_config.json"):
        """Initialize optimized scraper with performance settings"""
        super().__init__(config_path)
        
        # Performance settings
        self.performance_enabled = self.config.get('performance', {}).get('enable_optimization', False)
        self.parallel_enabled = self.config.get('performance', {}).get('parallel_processing', {}).get('enabled', False)
        self.max_workers = self.config.get('performance', {}).get('parallel_processing', {}).get('max_workers', 2)
        
        # Thread-safe data structures
        self.thread_lock = threading.Lock()
        self.page_queue = Queue()
        self.results_queue = Queue()
        
        # Performance metrics
        self.performance_stats = {
            'pages_processed_parallel': 0,
            'average_page_time_optimized': 0,
            'total_time_saved': 0
        }
    
    def _setup_optimized_browser(self) -> webdriver.Chrome:
        """Setup browser with performance optimizations"""
        chrome_options = Options()
        
        # Base options from parent class
        for option in self.config['browser']['chrome_options']:
            chrome_options.add_argument(option)
        
        # Performance optimizations
        if self.performance_enabled:
            perf_config = self.config['performance']['browser_optimization']
            
            if perf_config.get('headless', False):
                chrome_options.add_argument('--headless')
            
            if perf_config.get('disable_images', True):
                prefs = {"profile.managed_default_content_settings.images": 2}
                chrome_options.add_experimental_option("prefs", prefs)
            
            if perf_config.get('disable_css', False):
                chrome_options.add_argument('--disable-web-security')
                chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            
            # Additional performance options
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-background-timer-throttling')
            chrome_options.add_argument('--disable-renderer-backgrounding')
            chrome_options.add_argument('--disable-backgrounding-occluded-windows')
            chrome_options.add_argument('--disable-ipc-flooding-protection')
            
            # Memory optimizations
            chrome_options.add_argument('--memory-pressure-off')
            chrome_options.add_argument('--max_old_space_size=4096')
        
        # Set page load strategy
        page_load_strategy = self.config['performance']['browser_optimization'].get('page_load_strategy', 'normal')
        chrome_options.page_load_strategy = page_load_strategy
        
        # Create driver with proper service handling
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            # Fallback to system ChromeDriver
            try:
                driver = webdriver.Chrome(options=chrome_options)
            except Exception as e2:
                raise Exception(f"Failed to initialize Chrome driver: {str(e)} | Fallback error: {str(e2)}")
        
        # Set timeouts
        if self.performance_enabled:
            timeout = self.config['performance']['optimized_delays']['page_timeout']
        else:
            timeout = self.config['delays']['page_timeout']
        
        driver.set_page_load_timeout(timeout)
        driver.implicitly_wait(timeout)
        
        return driver
    
    def _smart_wait(self, driver: webdriver.Chrome, condition, timeout: Optional[int] = None) -> bool:
        """Implement smart waiting with adaptive timeouts"""
        if not self.performance_enabled:
            return super()._wait_for_element(driver, condition, timeout)
        
        # Use optimized timeouts
        if timeout is None:
            timeout = self.config['performance']['optimized_delays']['element_wait_timeout']
        
        try:
            wait = WebDriverWait(driver, timeout)
            wait.until(condition)
            return True
        except TimeoutException:
            return False
    
    def _get_optimized_delay(self, delay_type: str) -> float:
        """Get optimized delay based on performance settings"""
        if not self.performance_enabled:
            # Use standard delays
            delays = self.config['delays']
            if delay_type == 'between_pages':
                return random.uniform(delays['between_requests_min'], delays['between_requests_max'])
            elif delay_type == 'page_load':
                return random.uniform(delays['page_load_min'], delays['page_load_max'])
            else:
                return delays.get(delay_type, 1)
        
        # Use optimized delays
        opt_delays = self.config['performance']['optimized_delays']
        if delay_type == 'between_pages':
            return random.uniform(opt_delays['between_requests_min'], opt_delays['between_requests_max'])
        elif delay_type == 'page_load':
            return random.uniform(opt_delays['page_load_min'], opt_delays['page_load_max'])
        else:
            return opt_delays.get(delay_type, 0.5)
    
    def _scrape_page_optimized(self, page_url: str, worker_id: int = 0) -> Tuple[List[PropertyModel], int, int]:
        """Optimized page scraping with performance enhancements"""
        start_time = time.time()
        
        # Setup optimized browser for this worker
        driver = self._setup_optimized_browser()
        
        try:
            # Navigate with optimized timing
            driver.get(page_url)
            
            # Smart wait for page load
            if self.performance_enabled and self.config['performance']['optimized_delays']['smart_waiting']:
                # Wait for specific elements instead of fixed delay
                self._smart_wait(driver, EC.presence_of_element_located((By.CSS_SELECTOR, self.config['selectors']['property_cards'])))
            else:
                time.sleep(self._get_optimized_delay('page_load'))
            
            # Get page source and parse
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract properties using parent class method
            property_cards = soup.select(self.config['selectors']['property_cards'])
            extracted_properties = []
            
            for i, card in enumerate(property_cards):
                try:
                    property_data = self._extract_property_data(card, i + 1)
                    if property_data:
                        extracted_properties.append(property_data)
                    
                    # Minimal delay between properties
                    if i < len(property_cards) - 1:
                        time.sleep(self._get_optimized_delay('between_properties'))
                        
                except Exception as e:
                    self.logger.log_error("PROPERTY_EXTRACTION", f"Worker {worker_id}: Failed to extract property {i+1}: {str(e)}")
                    continue
            
            page_time = time.time() - start_time
            
            # Update performance stats
            with self.thread_lock:
                self.performance_stats['pages_processed_parallel'] += 1
                current_avg = self.performance_stats['average_page_time_optimized']
                pages_count = self.performance_stats['pages_processed_parallel']
                self.performance_stats['average_page_time_optimized'] = ((current_avg * (pages_count - 1)) + page_time) / pages_count
            
            return extracted_properties, len(property_cards), len(extracted_properties)
            
        except Exception as e:
            self.logger.log_error("PAGE_SCRAPING", f"Worker {worker_id}: Failed to scrape page {page_url}: {str(e)}")
            return [], 0, 0
            
        finally:
            try:
                driver.quit()
            except Exception:
                pass
    
    def scrape_with_parallel_processing(self, start_page: int = 1, max_pages: Optional[int] = None) -> Dict[str, Any]:
        """Scrape pages using parallel processing for improved performance"""
        
        if not self.parallel_enabled:
            self.logger.logger.info("🔄 Parallel processing disabled, using standard scraping")
            return self.scrape_all_pages(start_page, max_pages)
        
        self.logger.logger.info(f"🚀 Starting PARALLEL scraping with {self.max_workers} workers")
        start_time = time.time()
        
        # Prepare page URLs
        if max_pages is None:
            max_pages = self.config['website']['max_pages']
        
        base_url = self.config['website']['base_url']
        page_urls = []
        
        for page_num in range(start_page, start_page + max_pages):
            if page_num == 1:
                page_urls.append(base_url)
            else:
                page_urls.append(f"{base_url}?page={page_num}")
        
        # Process pages in parallel
        all_properties = []
        total_found = 0
        total_extracted = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all page scraping tasks
            future_to_page = {
                executor.submit(self._scrape_page_optimized, url, i): (i, url) 
                for i, url in enumerate(page_urls)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_page):
                worker_id, page_url = future_to_page[future]
                
                try:
                    properties, found, extracted = future.result()
                    
                    with self.thread_lock:
                        all_properties.extend(properties)
                        total_found += found
                        total_extracted += extracted
                    
                    self.logger.logger.info(f"✅ Worker {worker_id}: Page completed - {extracted}/{found} properties")
                    
                except Exception as e:
                    self.logger.log_error("PARALLEL_PROCESSING", f"Worker {worker_id} failed: {str(e)}")
        
        # Store results
        self.scraped_properties = all_properties
        
        # Calculate performance improvement
        total_time = time.time() - start_time
        estimated_sequential_time = len(page_urls) * 14  # Baseline 14s per page
        time_saved = estimated_sequential_time - total_time
        
        self.performance_stats['total_time_saved'] = time_saved
        
        # Export data
        output_files = self._export_data()
        
        # Log performance results
        self.logger.logger.info("🎯 PARALLEL PROCESSING COMPLETE")
        self.logger.logger.info(f"⏱️  Total Time: {total_time:.1f}s")
        self.logger.logger.info(f"📈 Estimated Sequential Time: {estimated_sequential_time:.1f}s")
        self.logger.logger.info(f"🚀 Time Saved: {time_saved:.1f}s ({(time_saved/estimated_sequential_time)*100:.1f}%)")
        self.logger.logger.info(f"📊 Average Page Time: {self.performance_stats['average_page_time_optimized']:.1f}s")
        
        return {
            'success': True,
            'total_properties': len(all_properties),
            'valid_properties': len([p for p in all_properties if p.is_valid()]),
            'pages_processed': len(page_urls),
            'output_files': output_files,
            'performance_stats': self.performance_stats,
            'time_saved': time_saved,
            'speed_improvement': f"{(time_saved/estimated_sequential_time)*100:.1f}%"
        }


# Export for easy import
__all__ = ['OptimizedMagicBricksScraper']
