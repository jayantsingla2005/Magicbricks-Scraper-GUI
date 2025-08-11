#!/usr/bin/env python3
"""
Production URL Discovery & Queue Management System
Implements robust URL discovery from listing pages with intelligent queue management and deduplication.
"""

import time
import json
import hashlib
import threading
import random
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from queue import Queue, Empty, PriorityQueue
from urllib.parse import urljoin, urlparse
import re
import sqlite3

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
    from ..utils.logger import ScraperLogger
    from ..database.database_manager import DatabaseManager
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from core.modern_scraper import ModernMagicBricksScraper
    from utils.logger import ScraperLogger
    from database.database_manager import DatabaseManager


class URLPriorityQueue:
    """
    Priority queue for URL processing with intelligent prioritization
    """
    
    def __init__(self, max_size: int = 50000):
        """Initialize priority queue"""
        self.queue = PriorityQueue(maxsize=max_size)
        self.url_set = set()  # For fast duplicate checking
        self.lock = threading.Lock()
        
        # Priority levels
        self.PRIORITY_HIGH = 1      # New properties, premium listings
        self.PRIORITY_NORMAL = 2    # Standard properties
        self.PRIORITY_LOW = 3       # Older properties, already processed
        
        # Statistics
        self.stats = {
            'urls_added': 0,
            'urls_processed': 0,
            'duplicates_filtered': 0,
            'priority_high': 0,
            'priority_normal': 0,
            'priority_low': 0
        }
    
    def add_url(self, url: str, metadata: Dict[str, Any], priority: Optional[int] = None) -> bool:
        """Add URL to priority queue with intelligent prioritization"""
        with self.lock:
            # Check for duplicates
            url_hash = hashlib.md5(url.encode()).hexdigest()
            if url_hash in self.url_set:
                self.stats['duplicates_filtered'] += 1
                return False
            
            # Determine priority if not specified
            if priority is None:
                priority = self._calculate_priority(url, metadata)
            
            try:
                # Add to queue with priority and timestamp
                queue_item = (priority, time.time(), url, metadata)
                self.queue.put(queue_item, block=False)
                
                # Track in set for duplicate checking
                self.url_set.add(url_hash)
                
                # Update statistics
                self.stats['urls_added'] += 1
                if priority == self.PRIORITY_HIGH:
                    self.stats['priority_high'] += 1
                elif priority == self.PRIORITY_NORMAL:
                    self.stats['priority_normal'] += 1
                else:
                    self.stats['priority_low'] += 1
                
                return True
                
            except:
                return False  # Queue full
    
    def get_next_url(self, timeout: float = 1.0) -> Optional[Tuple[str, Dict[str, Any], int]]:
        """Get next URL from priority queue"""
        try:
            priority, timestamp, url, metadata = self.queue.get(timeout=timeout)
            
            with self.lock:
                self.stats['urls_processed'] += 1
            
            return url, metadata, priority
            
        except Empty:
            return None
    
    def _calculate_priority(self, url: str, metadata: Dict[str, Any]) -> int:
        """Calculate URL priority based on metadata and URL characteristics"""
        
        # High priority indicators
        high_priority_keywords = ['new', 'launch', 'premium', 'luxury', 'exclusive']
        normal_priority_keywords = ['sale', 'apartment', 'house', 'flat']
        
        # Check metadata for priority indicators
        title = metadata.get('listing_title', '').lower()
        price = metadata.get('listing_price', '')
        
        # High priority conditions
        if any(keyword in title for keyword in high_priority_keywords):
            return self.PRIORITY_HIGH
        
        # Check for high-value properties (>2 Cr)
        if 'Cr' in price:
            try:
                price_value = float(re.search(r'(\d+(?:\.\d+)?)', price).group(1))
                if price_value >= 2.0:
                    return self.PRIORITY_HIGH
            except:
                pass
        
        # Normal priority for standard properties
        if any(keyword in title for keyword in normal_priority_keywords):
            return self.PRIORITY_NORMAL
        
        # Default to normal priority
        return self.PRIORITY_NORMAL
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        with self.lock:
            return {
                'queue_size': self.queue.qsize(),
                'total_urls_tracked': len(self.url_set),
                **self.stats
            }
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return self.queue.empty()


class URLDiscoveryManager:
    """
    Production URL Discovery Manager
    Discovers property URLs from listing pages with intelligent crawling and queue management
    """
    
    def __init__(self, config_path: str = "config/scraper_config.json", 
                 db_path: str = "data/url_discovery.db"):
        """Initialize URL discovery manager"""
        
        # Load configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Initialize components
        self.logger = ScraperLogger(self.config)
        self.url_queue = URLPriorityQueue()
        self.db_manager = DatabaseManager(db_path)
        
        # Discovery settings
        self.discovery_config = self.config.get('phase2', {}).get('url_discovery', {})
        self.max_pages = self.discovery_config.get('max_listing_pages', 100)
        self.urls_per_page_target = self.discovery_config.get('urls_per_page_target', 30)
        
        # URL patterns for property pages
        self.property_url_patterns = [
            r'/propertydetail/',
            r'/property-detail/',
            r'pdpid=',
            r'/property/',
            r'/listing/'
        ]
        
        # Exclude patterns
        self.exclude_patterns = [
            r'/builder/',
            r'/project/',
            r'/locality/',
            r'/advertisement',
            r'/banner',
            r'/search'
        ]
        
        # Discovery statistics
        self.discovery_stats = {
            'pages_crawled': 0,
            'urls_discovered': 0,
            'valid_urls': 0,
            'invalid_urls': 0,
            'discovery_rate': 0.0,
            'start_time': None,
            'end_time': None
        }
        
        # Initialize URL tracking database
        self._initialize_url_database()
    
    def _initialize_url_database(self):
        """Initialize database for URL tracking"""
        cursor = self.db_manager.connection.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discovered_urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                url_hash TEXT UNIQUE NOT NULL,
                source_page TEXT,
                discovery_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                priority INTEGER,
                metadata TEXT,
                processing_status TEXT DEFAULT 'pending',
                processed_time TIMESTAMP,
                error_count INTEGER DEFAULT 0,
                last_error TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discovery_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                pages_crawled INTEGER DEFAULT 0,
                urls_discovered INTEGER DEFAULT 0,
                config TEXT,
                status TEXT DEFAULT 'running'
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_url_hash ON discovered_urls(url_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_processing_status ON discovered_urls(processing_status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_discovery_time ON discovered_urls(discovery_time)")
        
        self.db_manager.connection.commit()
        self.logger.logger.info("✅ URL discovery database initialized")
    
    def discover_urls_from_listings(self, start_page: int = 1, max_pages: Optional[int] = None,
                                  session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Discover property URLs from listing pages
        
        Args:
            start_page: Starting page number
            max_pages: Maximum pages to crawl
            session_id: Optional session ID for tracking
        """
        
        if max_pages is None:
            max_pages = self.max_pages
        
        if session_id is None:
            session_id = f"discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.discovery_stats['start_time'] = datetime.now()
        
        # Create discovery session
        self._create_discovery_session(session_id, start_page, max_pages)
        
        self.logger.logger.info(f"🔍 Starting URL discovery from page {start_page} to {max_pages}")
        self.logger.logger.info(f"📋 Session ID: {session_id}")
        
        # Initialize browser
        driver = self._setup_discovery_browser()
        
        try:
            base_url = self.config['website']['base_url']
            
            for page_num in range(start_page, start_page + max_pages):
                try:
                    # Construct page URL
                    if page_num == 1:
                        page_url = base_url
                    else:
                        page_url = f"{base_url}?page={page_num}"
                    
                    self.logger.logger.info(f"🔍 Discovering URLs from page {page_num}")
                    
                    # Discover URLs from this page
                    page_urls = self._discover_urls_from_page(driver, page_url, page_num)
                    
                    # Add URLs to queue and database
                    valid_urls = 0
                    for url, metadata in page_urls:
                        if self._add_discovered_url(url, metadata, page_url, session_id):
                            valid_urls += 1
                    
                    # Update statistics
                    self.discovery_stats['pages_crawled'] += 1
                    self.discovery_stats['urls_discovered'] += len(page_urls)
                    self.discovery_stats['valid_urls'] += valid_urls
                    self.discovery_stats['invalid_urls'] += len(page_urls) - valid_urls
                    
                    self.logger.logger.info(f"✅ Page {page_num}: Found {len(page_urls)} URLs, {valid_urls} valid")
                    
                    # Delay between pages
                    delay = random.uniform(
                        self.discovery_config.get('discovery_delay_min', 3),
                        self.discovery_config.get('discovery_delay_max', 6)
                    )
                    time.sleep(delay)
                    
                except Exception as e:
                    self.logger.log_error("URL_DISCOVERY", f"Failed to discover URLs from page {page_num}: {str(e)}")
                    continue
        
        finally:
            driver.quit()
            self.discovery_stats['end_time'] = datetime.now()
            
            # Update session
            self._update_discovery_session(session_id)
        
        # Calculate final statistics
        total_time = (self.discovery_stats['end_time'] - self.discovery_stats['start_time']).total_seconds()
        self.discovery_stats['discovery_rate'] = self.discovery_stats['urls_discovered'] / total_time if total_time > 0 else 0
        
        self.logger.logger.info(f"🎯 URL Discovery Complete")
        self.logger.logger.info(f"📊 Total URLs discovered: {self.discovery_stats['urls_discovered']}")
        self.logger.logger.info(f"✅ Valid URLs: {self.discovery_stats['valid_urls']}")
        self.logger.logger.info(f"⏱️  Discovery rate: {self.discovery_stats['discovery_rate']:.1f} URLs/second")
        
        return {
            'success': True,
            'session_id': session_id,
            'statistics': self.discovery_stats,
            'queue_stats': self.url_queue.get_stats()
        }
    
    def _setup_discovery_browser(self) -> webdriver.Chrome:
        """Setup optimized browser for URL discovery"""
        # Use the same browser setup as the main scraper but optimized for discovery
        scraper = ModernMagicBricksScraper()
        return scraper._setup_browser()
    
    def _discover_urls_from_page(self, driver: webdriver.Chrome, page_url: str, 
                                page_num: int) -> List[Tuple[str, Dict[str, Any]]]:
        """Discover property URLs from a single listing page"""
        
        discovered_urls = []
        
        try:
            # Navigate to page
            driver.get(page_url)
            
            # Wait for page load
            time.sleep(random.uniform(2, 4))
            
            # Get page source
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find all links
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href')
                if not href:
                    continue
                
                # Convert to absolute URL
                absolute_url = urljoin(page_url, href)
                
                # Check if it's a property URL
                if self._is_property_url(absolute_url):
                    # Extract metadata from the link context
                    metadata = self._extract_url_metadata(link, page_num)
                    discovered_urls.append((absolute_url, metadata))
        
        except Exception as e:
            self.logger.log_error("PAGE_URL_DISCOVERY", f"Failed to discover URLs from {page_url}: {str(e)}")
        
        return discovered_urls
    
    def _is_property_url(self, url: str) -> bool:
        """Check if URL is a valid property page URL"""
        
        # Check for property URL patterns
        has_property_pattern = any(pattern in url for pattern in self.property_url_patterns)
        
        # Check for exclude patterns
        has_exclude_pattern = any(pattern in url for pattern in self.exclude_patterns)
        
        return has_property_pattern and not has_exclude_pattern
    
    def _extract_url_metadata(self, link_element, page_num: int) -> Dict[str, Any]:
        """Extract metadata from link element context"""
        
        metadata = {
            'discovery_page': page_num,
            'discovery_time': datetime.now().isoformat()
        }
        
        try:
            # Try to find property card context
            property_card = link_element.find_parent(['div', 'article'], class_=re.compile(r'card|property|listing'))
            
            if property_card:
                # Extract title
                title_elem = property_card.find(['h1', 'h2', 'h3'], class_=re.compile(r'title|name'))
                if title_elem:
                    metadata['listing_title'] = title_elem.get_text(strip=True)
                
                # Extract price
                price_elem = property_card.find(['div', 'span'], class_=re.compile(r'price|cost|amount'))
                if price_elem:
                    metadata['listing_price'] = price_elem.get_text(strip=True)
                
                # Extract location
                location_elem = property_card.find(['div', 'span'], class_=re.compile(r'location|locality|address'))
                if location_elem:
                    metadata['listing_location'] = location_elem.get_text(strip=True)
        
        except Exception as e:
            metadata['extraction_error'] = str(e)
        
        return metadata
    
    def _add_discovered_url(self, url: str, metadata: Dict[str, Any], 
                           source_page: str, session_id: str) -> bool:
        """Add discovered URL to queue and database"""
        
        try:
            # Calculate URL hash for deduplication
            url_hash = hashlib.md5(url.encode()).hexdigest()
            
            # Check if URL already exists in database
            cursor = self.db_manager.connection.cursor()
            cursor.execute("SELECT id FROM discovered_urls WHERE url_hash = ?", (url_hash,))
            
            if cursor.fetchone():
                return False  # URL already exists
            
            # Determine priority
            priority = self.url_queue._calculate_priority(url, metadata)
            
            # Add to database
            cursor.execute("""
                INSERT INTO discovered_urls 
                (url, url_hash, source_page, priority, metadata, processing_status)
                VALUES (?, ?, ?, ?, ?, 'pending')
            """, (url, url_hash, source_page, priority, json.dumps(metadata)))
            
            self.db_manager.connection.commit()
            
            # Add to priority queue
            return self.url_queue.add_url(url, metadata, priority)
            
        except Exception as e:
            self.logger.log_error("URL_STORAGE", f"Failed to store URL {url}: {str(e)}")
            return False
    
    def _create_discovery_session(self, session_id: str, start_page: int, max_pages: int):
        """Create discovery session in database"""
        
        cursor = self.db_manager.connection.cursor()
        
        session_config = {
            'start_page': start_page,
            'max_pages': max_pages,
            'discovery_config': self.discovery_config
        }
        
        cursor.execute("""
            INSERT INTO discovery_sessions (session_id, start_time, config)
            VALUES (?, ?, ?)
        """, (session_id, datetime.now(), json.dumps(session_config)))
        
        self.db_manager.connection.commit()
    
    def _update_discovery_session(self, session_id: str):
        """Update discovery session with final statistics"""
        
        cursor = self.db_manager.connection.cursor()
        
        cursor.execute("""
            UPDATE discovery_sessions 
            SET end_time = ?, pages_crawled = ?, urls_discovered = ?, status = 'completed'
            WHERE session_id = ?
        """, (
            datetime.now(),
            self.discovery_stats['pages_crawled'],
            self.discovery_stats['urls_discovered'],
            session_id
        ))
        
        self.db_manager.connection.commit()
    
    def get_pending_urls(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get pending URLs from database"""
        
        cursor = self.db_manager.connection.cursor()
        
        query = """
            SELECT url, metadata, priority, discovery_time 
            FROM discovered_urls 
            WHERE processing_status = 'pending'
            ORDER BY priority ASC, discovery_time ASC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        return [
            {
                'url': row[0],
                'metadata': json.loads(row[1]) if row[1] else {},
                'priority': row[2],
                'discovery_time': row[3]
            }
            for row in rows
        ]
    
    def mark_url_processed(self, url: str, success: bool = True, error: Optional[str] = None):
        """Mark URL as processed in database"""
        
        cursor = self.db_manager.connection.cursor()
        
        if success:
            cursor.execute("""
                UPDATE discovered_urls 
                SET processing_status = 'completed', processed_time = ?
                WHERE url = ?
            """, (datetime.now(), url))
        else:
            cursor.execute("""
                UPDATE discovered_urls 
                SET processing_status = 'failed', error_count = error_count + 1, 
                    last_error = ?, processed_time = ?
                WHERE url = ?
            """, (error, datetime.now(), url))
        
        self.db_manager.connection.commit()
    
    def get_discovery_statistics(self) -> Dict[str, Any]:
        """Get comprehensive discovery statistics"""

        cursor = self.db_manager.connection.cursor()

        # Get URL counts by status
        cursor.execute("""
            SELECT processing_status, COUNT(*)
            FROM discovered_urls
            GROUP BY processing_status
        """)
        status_counts = dict(cursor.fetchall())

        # Get recent discovery activity
        cursor.execute("""
            SELECT COUNT(*)
            FROM discovered_urls
            WHERE discovery_time > datetime('now', '-24 hours')
        """)
        recent_discoveries = cursor.fetchone()[0]

        return {
            'queue_stats': self.url_queue.get_stats(),
            'database_stats': status_counts,
            'recent_discoveries_24h': recent_discoveries,
            'discovery_session_stats': self.discovery_stats
        }

    def close(self):
        """Close database connections and cleanup resources"""
        if hasattr(self, 'db_manager') and self.db_manager:
            self.db_manager.close()


# Export for easy import
__all__ = ['URLDiscoveryManager', 'URLPriorityQueue']
