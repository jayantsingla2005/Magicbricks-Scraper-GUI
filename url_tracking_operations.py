#!/usr/bin/env python3
"""
URL Tracking Operations Module
Provides core URL tracking functionality for incremental scraping.
Handles tracking, batch processing, and database operations.
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
from url_normalization import URLNormalizer


class URLTrackingOperations:
    """
    Core URL tracking operations
    """
    
    def __init__(self, db_path: str, normalizer: URLNormalizer = None):
        """
        Initialize URL tracking operations
        
        Args:
            db_path: Path to SQLite database
            normalizer: URLNormalizer instance (creates new if None)
        """
        self.db_path = db_path
        self.normalizer = normalizer or URLNormalizer()
        
        # Tracking statistics
        self.stats = {
            'urls_processed': 0,
            'new_urls_found': 0,
            'duplicate_urls_found': 0,
            'urls_updated': 0
        }
    
    def connect_db(self) -> Optional[sqlite3.Connection]:
        """
        Connect to database
        
        Returns:
            Database connection or None if failed
        """
        try:
            return sqlite3.connect(self.db_path)
        except Exception as e:
            print(f"[ERROR] Database connection failed: {str(e)}")
            return None
    
    def track_property_url(
        self, 
        url: str, 
        title: str = None, 
        city: str = None, 
        session_id: int = None
    ) -> Dict[str, Any]:
        """
        Track a property URL and return tracking information
        
        Args:
            url: Property URL to track
            title: Property title (optional)
            city: City name (optional)
            session_id: Scraping session ID (optional)
            
        Returns:
            Dictionary with tracking result:
            - success: bool
            - url: normalized URL
            - url_hash: MD5 hash
            - property_id: extracted property ID
            - is_new_url: bool
            - is_duplicate: bool
            - seen_count: int
            - first_seen_date: datetime
            - action_taken: str
        """
        connection = self.connect_db()
        if not connection:
            return {'success': False, 'error': 'Database connection failed'}
        
        try:
            cursor = connection.cursor()
            
            # Normalize and process URL
            normalized_url = self.normalizer.normalize_url(url)
            url_hash = self.normalizer.generate_url_hash(url)
            property_id = self.normalizer.extract_property_id_from_url(url)
            current_time = datetime.now()
            
            # Check if URL already exists
            cursor.execute('''
                SELECT url_id, first_seen_date, seen_count, is_active 
                FROM property_urls_seen 
                WHERE property_url = ?
            ''', (normalized_url,))
            
            existing_record = cursor.fetchone()
            
            # Initialize tracking result
            tracking_result = {
                'success': True,
                'url': normalized_url,
                'url_hash': url_hash,
                'property_id': property_id,
                'is_new_url': False,
                'is_duplicate': False,
                'seen_count': 1,
                'first_seen_date': current_time,
                'action_taken': None
            }
            
            if existing_record:
                # URL already exists - update it
                url_id, first_seen_date, seen_count, is_active = existing_record
                new_seen_count = seen_count + 1
                
                cursor.execute('''
                    UPDATE property_urls_seen 
                    SET last_seen_date = ?, 
                        seen_count = ?, 
                        title = ?, 
                        city = ?, 
                        is_active = 1
                    WHERE property_url = ?
                ''', (current_time, new_seen_count, title, city, normalized_url))
                
                tracking_result.update({
                    'is_duplicate': True,
                    'seen_count': new_seen_count,
                    'first_seen_date': datetime.fromisoformat(first_seen_date),
                    'action_taken': 'updated_existing'
                })
                
                self.stats['duplicate_urls_found'] += 1
                self.stats['urls_updated'] += 1
                
            else:
                # New URL - insert it
                cursor.execute('''
                    INSERT INTO property_urls_seen 
                    (property_url, first_seen_date, last_seen_date, seen_count, 
                     property_id, title, city, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    normalized_url, current_time, current_time, 1, 
                    property_id, title, city, 1, current_time
                ))
                
                tracking_result.update({
                    'is_new_url': True,
                    'action_taken': 'inserted_new'
                })
                
                self.stats['new_urls_found'] += 1
            
            connection.commit()
            self.stats['urls_processed'] += 1
            
            return tracking_result
            
        except Exception as e:
            connection.rollback()
            return {'success': False, 'error': str(e)}
        
        finally:
            if connection:
                connection.close()
    
    def batch_track_urls(
        self, 
        url_data: List[Dict[str, Any]], 
        session_id: int = None
    ) -> Dict[str, Any]:
        """
        Track multiple URLs in batch for efficiency
        
        Args:
            url_data: List of dictionaries with 'url', 'title', 'city' keys
            session_id: Scraping session ID (optional)
            
        Returns:
            Dictionary with batch results:
            - total_urls: int
            - new_urls: int
            - duplicate_urls: int
            - errors: int
            - processing_time: float (seconds)
            - url_results: list of individual results
        """
        print(f"[URL] Batch tracking {len(url_data)} URLs...")
        
        batch_results = {
            'total_urls': len(url_data),
            'new_urls': 0,
            'duplicate_urls': 0,
            'errors': 0,
            'processing_time': 0,
            'url_results': []
        }
        
        start_time = datetime.now()
        
        for i, url_info in enumerate(url_data):
            url = url_info.get('url', '')
            title = url_info.get('title', '')
            city = url_info.get('city', '')
            posting_text = url_info.get('posting_date_text')
            parsed_posting = url_info.get('parsed_posting_date')

            result = self.track_property_url(url, title, city, session_id)

            # Persist posting dates when available
            if result.get('success') and (posting_text or parsed_posting):
                try:
                    conn2 = self.connect_db()
                    if conn2:
                        cur2 = conn2.cursor()
                        cur2.execute('''
                            INSERT INTO property_posting_dates
                            (property_url, posting_date_text, parsed_posting_date, extraction_date, confidence_score, parsing_method)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            result.get('url') or url,
                            posting_text or '',
                            parsed_posting if isinstance(parsed_posting, str) else (parsed_posting.isoformat() if parsed_posting else None),
                            datetime.now(),
                            1.0,
                            'extractor'
                        ))
                        conn2.commit()
                        conn2.close()
                except Exception:
                    pass

            if result['success']:
                if result['is_new_url']:
                    batch_results['new_urls'] += 1
                elif result['is_duplicate']:
                    batch_results['duplicate_urls'] += 1
            else:
                batch_results['errors'] += 1

            batch_results['url_results'].append(result)

            # Progress reporting every 100 URLs
            if (i + 1) % 100 == 0:
                print(f"   [SUCCESS] Processed {i + 1}/{len(url_data)} URLs")

        batch_results['processing_time'] = (
            datetime.now() - start_time
        ).total_seconds()
        
        print(
            f"   [STATS] Batch tracking complete: "
            f"{batch_results['new_urls']} new, "
            f"{batch_results['duplicate_urls']} duplicates"
        )
        
        return batch_results
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get current tracking statistics
        
        Returns:
            Dictionary with tracking stats
        """
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset tracking statistics"""
        self.stats = {
            'urls_processed': 0,
            'new_urls_found': 0,
            'duplicate_urls_found': 0,
            'urls_updated': 0
        }

