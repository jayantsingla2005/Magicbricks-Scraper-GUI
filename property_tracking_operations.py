#!/usr/bin/env python3
"""
Property Tracking Operations
Core tracking logic for individual property scraping including URL filtering and property tracking.
"""

import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any
from property_database_manager import PropertyDatabaseManager
from property_quality_scorer import PropertyQualityScorer


class PropertyTrackingOperations:
    """
    Handles core tracking operations for individual property scraping
    """
    
    def __init__(self, db_manager: PropertyDatabaseManager, quality_scorer: PropertyQualityScorer, config: Dict[str, Any]):
        """Initialize tracking operations"""
        self.db_manager = db_manager
        self.quality_scorer = quality_scorer
        self.config = config
        
        # Statistics tracking
        self.stats = {
            'total_urls_processed': 0,
            'new_properties_found': 0,
            'duplicates_skipped': 0,
            'failed_extractions': 0,
            'quality_rescraped': 0
        }
    
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
        
        if not self.db_manager.connect_db():
            return -1
        
        try:
            cursor = self.db_manager.connection.cursor()
            
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
            self.db_manager.connection.commit()
            
            print(f"[SUCCESS] Created individual scraping session {session_id} for {total_urls} URLs")
            return session_id
            
        except Exception as e:
            print(f"[ERROR] Failed to create scraping session: {str(e)}")
            return -1
        
        finally:
            self.db_manager.close_connection()
    
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
        
        if not self.db_manager.connect_db():
            return {'success': False, 'error': 'Database connection failed'}
        
        try:
            cursor = self.db_manager.connection.cursor()
            
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
            self.db_manager.close_connection()

    def track_scraped_property(self, property_url: str, property_data: Dict[str, Any],
                              session_id: int, quality_score: float = None) -> bool:
        """Track a successfully scraped individual property"""

        if not self.db_manager.connect_db():
            return False

        try:
            cursor = self.db_manager.connection.cursor()

            normalized_url = self.normalize_url(property_url)
            url_hash = self.generate_url_hash(normalized_url)
            current_time = datetime.now()

            # Calculate quality score if not provided
            if quality_score is None:
                quality_score = self.quality_scorer.calculate_quality_score(property_data)

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

            self.db_manager.connection.commit()
            self.stats['total_urls_processed'] += 1

            return True

        except Exception as e:
            print(f"[ERROR] Failed to track scraped property {property_url}: {str(e)}")
            return False

        finally:
            self.db_manager.close_connection()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current tracking statistics"""
        return self.stats.copy()

