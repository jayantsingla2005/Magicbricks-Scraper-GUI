#!/usr/bin/env python3
"""
Individual Property Tracking System
Handles duplicate detection and tracking for individual property page scraping
"""

import sqlite3
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import json


class IndividualPropertyTracker:
    """
    Comprehensive tracking system for individual property scraping
    Prevents duplicate scraping and manages property data persistence
    """
    
    def __init__(self, db_path: str = 'magicbricks_enhanced.db'):
        """Initialize individual property tracking system"""
        
        self.db_path = db_path
        self.connection = None
        
        # Tracking configuration
        self.config = {
            'enable_duplicate_detection': True,
            'force_rescrape_days': 30,  # Re-scrape after 30 days
            'max_retry_attempts': 3,
            'quality_threshold': 0.7,   # Minimum quality score
            'enable_change_detection': True
        }
        
        # Statistics tracking
        self.stats = {
            'total_urls_processed': 0,
            'new_properties_found': 0,
            'duplicates_skipped': 0,
            'failed_extractions': 0,
            'quality_rescraped': 0
        }
        
        # Initialize database schema
        self.setup_database_schema()
    
    def connect_db(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"[ERROR] Database connection failed: {str(e)}")
            return False
    
    def setup_database_schema(self):
        """Create necessary tables for individual property tracking"""
        
        if not self.connect_db():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # 1. Individual Properties Scraped Tracking Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS individual_properties_scraped (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    property_url TEXT UNIQUE NOT NULL,
                    property_id TEXT,
                    url_hash TEXT UNIQUE,
                    scraped_at DATETIME NOT NULL,
                    scraping_session_id INTEGER,
                    data_quality_score REAL DEFAULT 0.0,
                    extraction_success BOOLEAN DEFAULT 1,
                    retry_count INTEGER DEFAULT 0,
                    last_retry_at DATETIME,
                    force_rescrape_after DATETIME,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 2. Detailed Property Data Storage Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS property_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    property_url TEXT NOT NULL,
                    title TEXT,
                    price TEXT,
                    area TEXT,
                    locality TEXT,
                    society TEXT,
                    property_type TEXT,
                    bhk TEXT,
                    bathrooms TEXT,
                    furnishing TEXT,
                    floor TEXT,
                    age TEXT,
                    facing TEXT,
                    parking TEXT,
                    amenities TEXT,
                    description TEXT,
                    builder_info TEXT,
                    location_details TEXT,
                    specifications TEXT,
                    contact_info TEXT,
                    images TEXT,  -- JSON array
                    raw_html TEXT,
                    scraped_at DATETIME NOT NULL,
                    data_quality_score REAL DEFAULT 0.0,
                    extraction_metadata TEXT,  -- JSON
                    FOREIGN KEY (property_url) REFERENCES individual_properties_scraped(property_url)
                )
            ''')
            
            # 3. Individual Property Scraping Sessions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS individual_scraping_sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT NOT NULL,
                    start_timestamp DATETIME NOT NULL,
                    end_timestamp DATETIME,
                    total_urls_requested INTEGER DEFAULT 0,
                    new_properties_scraped INTEGER DEFAULT 0,
                    duplicates_skipped INTEGER DEFAULT 0,
                    failed_scraping INTEGER DEFAULT 0,
                    average_quality_score REAL DEFAULT 0.0,
                    session_config TEXT,  -- JSON
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 4. Property Change History (for tracking price/status changes)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS property_change_history (
                    change_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    property_url TEXT NOT NULL,
                    field_name TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    change_detected_at DATETIME NOT NULL,
                    scraping_session_id INTEGER,
                    FOREIGN KEY (property_url) REFERENCES individual_properties_scraped(property_url)
                )
            ''')
            
            # Create indexes for performance
            indexes = [
                ('idx_individual_scraped_url', 'individual_properties_scraped', 'property_url'),
                ('idx_individual_scraped_hash', 'individual_properties_scraped', 'url_hash'),
                ('idx_individual_scraped_date', 'individual_properties_scraped', 'scraped_at'),
                ('idx_individual_scraped_quality', 'individual_properties_scraped', 'data_quality_score'),
                ('idx_property_details_url', 'property_details', 'property_url'),
                ('idx_property_details_scraped', 'property_details', 'scraped_at'),
                ('idx_individual_sessions_start', 'individual_scraping_sessions', 'start_timestamp'),
                ('idx_change_history_url', 'property_change_history', 'property_url'),
                ('idx_change_history_date', 'property_change_history', 'change_detected_at')
            ]
            
            for index_name, table_name, column_name in indexes:
                try:
                    cursor.execute(f'CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})')
                except Exception as e:
                    print(f"[WARNING] Could not create index {index_name}: {str(e)}")
            
            self.connection.commit()
            print("[SUCCESS] Individual property tracking database schema created")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to create database schema: {str(e)}")
            return False
        
        finally:
            if self.connection:
                self.connection.close()
    
    def generate_url_hash(self, url: str) -> str:
        """Generate unique hash for URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL for consistent comparison"""
        # Remove common variations
        url = url.strip().lower()
        
        # Remove trailing slashes
        url = url.rstrip('/')
        
        # Remove common parameters that don't affect content
        import re
        url = re.sub(r'[?&](utm_|ref=|source=)[^&]*', '', url)
        
        return url
    
    def create_scraping_session(self, session_name: str, total_urls: int, config: Dict[str, Any] = None) -> int:
        """Create a new individual property scraping session"""
        
        if not self.connect_db():
            return -1
        
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                INSERT INTO individual_scraping_sessions 
                (session_name, start_timestamp, total_urls_requested, session_config)
                VALUES (?, ?, ?, ?)
            ''', (
                session_name,
                datetime.now(),
                total_urls,
                json.dumps(config or {})
            ))
            
            session_id = cursor.lastrowid
            self.connection.commit()
            
            print(f"[SUCCESS] Created individual scraping session {session_id} for {total_urls} URLs")
            return session_id
            
        except Exception as e:
            print(f"[ERROR] Failed to create scraping session: {str(e)}")
            return -1
        
        finally:
            if self.connection:
                self.connection.close()
    
    def filter_urls_for_scraping(self, property_urls: List[str], 
                                force_rescrape: bool = False,
                                quality_threshold: float = None) -> Dict[str, Any]:
        """
        Filter URLs to determine which need scraping
        
        Args:
            property_urls: List of property URLs to check
            force_rescrape: If True, include all URLs regardless of previous scraping
            quality_threshold: Minimum quality score to avoid re-scraping
        
        Returns:
            Dictionary with filtered URLs and statistics
        """
        
        if not self.connect_db():
            return {'success': False, 'error': 'Database connection failed'}
        
        try:
            cursor = self.connection.cursor()
            
            quality_threshold = quality_threshold or self.config['quality_threshold']
            current_time = datetime.now()
            
            result = {
                'success': True,
                'total_urls_requested': len(property_urls),
                'urls_to_scrape': [],
                'urls_to_skip': [],
                'new_urls': [],
                'duplicate_urls': [],
                'quality_rescrape_urls': [],
                'expired_urls': [],
                'statistics': {
                    'new_count': 0,
                    'duplicate_count': 0,
                    'quality_rescrape_count': 0,
                    'expired_count': 0,
                    'skip_count': 0
                }
            }
            
            for url in property_urls:
                normalized_url = self.normalize_url(url)
                url_hash = self.generate_url_hash(normalized_url)
                
                # Check if URL was previously scraped
                cursor.execute('''
                    SELECT property_url, scraped_at, data_quality_score, 
                           extraction_success, force_rescrape_after
                    FROM individual_properties_scraped 
                    WHERE url_hash = ? OR property_url = ?
                ''', (url_hash, normalized_url))
                
                existing_record = cursor.fetchone()
                
                if not existing_record:
                    # New URL - needs scraping
                    result['urls_to_scrape'].append(url)
                    result['new_urls'].append(url)
                    result['statistics']['new_count'] += 1
                    
                elif force_rescrape:
                    # Force re-scrape requested
                    result['urls_to_scrape'].append(url)
                    result['duplicate_urls'].append(url)
                    result['statistics']['duplicate_count'] += 1
                    
                else:
                    # Check various conditions for re-scraping
                    scraped_at = datetime.fromisoformat(existing_record['scraped_at'])
                    quality_score = existing_record['data_quality_score'] or 0.0
                    extraction_success = existing_record['extraction_success']
                    force_rescrape_after = existing_record['force_rescrape_after']
                    
                    should_rescrape = False
                    rescrape_reason = ""
                    
                    # Check if extraction failed previously
                    if not extraction_success:
                        should_rescrape = True
                        rescrape_reason = "previous_extraction_failed"
                    
                    # Check if quality is below threshold
                    elif quality_score < quality_threshold:
                        should_rescrape = True
                        rescrape_reason = "low_quality_score"
                        result['quality_rescrape_urls'].append(url)
                        result['statistics']['quality_rescrape_count'] += 1
                    
                    # Check if force rescrape date has passed
                    elif force_rescrape_after and current_time > datetime.fromisoformat(force_rescrape_after):
                        should_rescrape = True
                        rescrape_reason = "force_rescrape_date_passed"
                        result['expired_urls'].append(url)
                        result['statistics']['expired_count'] += 1
                    
                    if should_rescrape:
                        result['urls_to_scrape'].append(url)
                    else:
                        result['urls_to_skip'].append(url)
                        result['statistics']['skip_count'] += 1
            
            print(f"[FILTER] URL filtering complete:")
            print(f"   📊 Total requested: {result['statistics']['new_count'] + result['statistics']['duplicate_count'] + result['statistics']['skip_count']}")
            print(f"   🆕 New URLs: {result['statistics']['new_count']}")
            print(f"   🔄 Quality re-scrape: {result['statistics']['quality_rescrape_count']}")
            print(f"   ⏰ Expired URLs: {result['statistics']['expired_count']}")
            print(f"   ⏭️ Skipped (already good): {result['statistics']['skip_count']}")
            print(f"   🎯 Total to scrape: {len(result['urls_to_scrape'])}")
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
        finally:
            if self.connection:
                self.connection.close()

    def track_scraped_property(self, property_url: str, property_data: Dict[str, Any],
                              session_id: int, quality_score: float = None) -> bool:
        """Track a successfully scraped individual property"""

        if not self.connect_db():
            return False

        try:
            cursor = self.connection.cursor()

            normalized_url = self.normalize_url(property_url)
            url_hash = self.generate_url_hash(normalized_url)
            current_time = datetime.now()

            # Calculate quality score if not provided
            if quality_score is None:
                quality_score = self.calculate_data_quality_score(property_data)

            # Insert or update tracking record
            cursor.execute('''
                INSERT OR REPLACE INTO individual_properties_scraped
                (property_url, property_id, url_hash, scraped_at, scraping_session_id,
                 data_quality_score, extraction_success, retry_count, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
            ''', (
                normalized_url,
                property_data.get('property_id'),
                url_hash,
                current_time,
                session_id,
                quality_score,
                True,
                current_time
            ))

            # Store detailed property data
            cursor.execute('''
                INSERT OR REPLACE INTO property_details
                (property_url, title, price, area, locality, society, property_type,
                 bhk, bathrooms, furnishing, floor, age, facing, parking, amenities,
                 description, builder_info, location_details, specifications,
                 contact_info, images, raw_html, scraped_at, data_quality_score,
                 extraction_metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                normalized_url,
                property_data.get('title'),
                property_data.get('price'),
                property_data.get('area'),
                property_data.get('locality'),
                property_data.get('society'),
                property_data.get('property_type'),
                property_data.get('bhk'),
                property_data.get('bathrooms'),
                property_data.get('furnishing'),
                property_data.get('floor'),
                property_data.get('age'),
                property_data.get('facing'),
                property_data.get('parking'),
                json.dumps(property_data.get('amenities', [])),
                property_data.get('description'),
                json.dumps(property_data.get('builder_info', {})),
                json.dumps(property_data.get('location_details', {})),
                json.dumps(property_data.get('specifications', {})),
                json.dumps(property_data.get('contact_info', {})),
                json.dumps(property_data.get('images', [])),
                property_data.get('raw_html'),
                current_time,
                quality_score,
                json.dumps(property_data.get('extraction_metadata', {}))
            ))

            self.connection.commit()
            self.stats['total_urls_processed'] += 1

            return True

        except Exception as e:
            print(f"[ERROR] Failed to track scraped property {property_url}: {str(e)}")
            return False

        finally:
            if self.connection:
                self.connection.close()

    def calculate_data_quality_score(self, property_data: Dict[str, Any]) -> float:
        """Calculate data quality score based on completeness and validity"""

        # Define important fields and their weights
        field_weights = {
            'title': 0.15,
            'price': 0.20,
            'area': 0.15,
            'locality': 0.10,
            'property_type': 0.10,
            'bhk': 0.05,
            'amenities': 0.10,
            'description': 0.05,
            'images': 0.05,
            'contact_info': 0.05
        }

        total_score = 0.0

        for field, weight in field_weights.items():
            value = property_data.get(field)

            if value and value != 'N/A' and str(value).strip():
                # Field has value
                field_score = weight

                # Bonus for rich content
                if field == 'description' and len(str(value)) > 100:
                    field_score *= 1.2
                elif field == 'amenities' and isinstance(value, list) and len(value) > 3:
                    field_score *= 1.2
                elif field == 'images' and isinstance(value, list) and len(value) > 2:
                    field_score *= 1.2

                total_score += field_score

        # Normalize to 0-1 range
        return min(total_score, 1.0)

    def get_scraping_statistics(self, session_id: int = None) -> Dict[str, Any]:
        """Get comprehensive scraping statistics"""

        if not self.connect_db():
            return {'success': False, 'error': 'Database connection failed'}

        try:
            cursor = self.connection.cursor()

            stats = {'success': True}

            if session_id:
                # Get specific session stats
                cursor.execute('''
                    SELECT * FROM individual_scraping_sessions
                    WHERE session_id = ?
                ''', (session_id,))

                session_data = cursor.fetchone()
                if session_data:
                    stats['session'] = dict(session_data)

            # Get overall statistics
            cursor.execute('''
                SELECT
                    COUNT(*) as total_properties_scraped,
                    COUNT(CASE WHEN extraction_success = 1 THEN 1 END) as successful_extractions,
                    AVG(data_quality_score) as average_quality,
                    COUNT(CASE WHEN data_quality_score < 0.7 THEN 1 END) as low_quality_count,
                    MAX(scraped_at) as last_scrape_date
                FROM individual_properties_scraped
            ''')

            overall_stats = cursor.fetchone()
            if overall_stats:
                stats['overall'] = dict(overall_stats)

            return stats

        except Exception as e:
            return {'success': False, 'error': str(e)}

        finally:
            if self.connection:
                self.connection.close()


# Example usage and testing
if __name__ == "__main__":
    # Initialize tracker
    tracker = IndividualPropertyTracker()

    # Test URL filtering
    test_urls = [
        "https://www.magicbricks.com/property-detail-1",
        "https://www.magicbricks.com/property-detail-2",
        "https://www.magicbricks.com/property-detail-3"
    ]

    # Create test session
    session_id = tracker.create_scraping_session("Test Session", len(test_urls))

    # Filter URLs
    filter_result = tracker.filter_urls_for_scraping(test_urls)
    print(f"Filter result: {filter_result}")

    # Get statistics
    stats = tracker.get_scraping_statistics()
    print(f"Statistics: {stats}")
