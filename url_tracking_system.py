#!/usr/bin/env python3
"""
URL Tracking System Implementation
Implement URL tracking system as secondary validation method for incremental scraping.
Provides backup validation when date-based filtering needs confirmation.
"""

import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs


class URLTrackingSystem:
    """
    URL tracking system for backup validation in incremental scraping
    """
    
    def __init__(self, db_path: str = 'magicbricks_enhanced.db'):
        """Initialize URL tracking system"""
        
        self.db_path = db_path
        self.connection = None
        
        # URL tracking configuration
        self.tracking_config = {
            'url_cache_days': 30,              # Keep URLs for 30 days
            'similarity_threshold': 0.8,       # 80% similarity for duplicate detection
            'batch_size': 1000,                # Process URLs in batches
            'enable_url_normalization': True,  # Normalize URLs for better matching
            'track_url_parameters': True,      # Track URL parameters for analysis
            'enable_fuzzy_matching': False     # Fuzzy matching for similar URLs
        }
        
        # Tracking statistics
        self.tracking_stats = {
            'urls_processed': 0,
            'new_urls_found': 0,
            'duplicate_urls_found': 0,
            'urls_updated': 0,
            'validation_checks': 0,
            'validation_matches': 0
        }
        
        print("[URL] URL Tracking System Initialized")
    
    def connect_db(self):
        """Connect to database"""
        
        try:
            self.connection = sqlite3.connect(self.db_path)
            return True
        except Exception as e:
            print(f"[ERROR] Database connection failed: {str(e)}")
            return False
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL for consistent tracking"""
        
        try:
            if not self.tracking_config['enable_url_normalization']:
                return url
            
            # Parse URL
            parsed = urlparse(url)
            
            # Remove common tracking parameters
            tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'ref', 'source']
            query_params = parse_qs(parsed.query)
            
            # Filter out tracking parameters
            filtered_params = {k: v for k, v in query_params.items() 
                             if k not in tracking_params}
            
            # Rebuild query string
            if filtered_params:
                query_string = '&'.join([f"{k}={v[0]}" for k, v in filtered_params.items()])
                normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{query_string}"
            else:
                normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            
            return normalized_url.lower().strip()
            
        except Exception as e:
            print(f"[WARNING] Error normalizing URL {url}: {str(e)}")
            return url.lower().strip()
    
    def generate_url_hash(self, url: str) -> str:
        """Generate hash for URL for efficient storage and lookup"""
        
        normalized_url = self.normalize_url(url)
        return hashlib.md5(normalized_url.encode()).hexdigest()
    
    def extract_property_id_from_url(self, url: str) -> Optional[str]:
        """Extract property ID from MagicBricks URL if possible"""
        
        try:
            # Common MagicBricks URL patterns
            patterns = [
                r'/propertydetail/([^/]+)',
                r'/property-([^/]+)',
                r'propid=([^&]+)',
                r'/([^/]+)\.html'
            ]
            
            import re
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            print(f"[WARNING] Error extracting property ID from {url}: {str(e)}")
            return None
    
    def track_property_url(self, url: str, title: str = None, city: str = None, 
                          session_id: int = None) -> Dict[str, Any]:
        """Track a property URL and return tracking information"""
        
        if not self.connect_db():
            return {'success': False, 'error': 'Database connection failed'}
        
        try:
            cursor = self.connection.cursor()
            
            normalized_url = self.normalize_url(url)
            url_hash = self.generate_url_hash(url)
            property_id = self.extract_property_id_from_url(url)
            current_time = datetime.now()
            
            # Check if URL already exists
            cursor.execute('''
                SELECT url_id, first_seen_date, seen_count, is_active 
                FROM property_urls_seen 
                WHERE property_url = ?
            ''', (normalized_url,))
            
            existing_record = cursor.fetchone()
            
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
                    SET last_seen_date = ?, seen_count = ?, title = ?, city = ?, is_active = 1
                    WHERE property_url = ?
                ''', (current_time, new_seen_count, title, city, normalized_url))
                
                tracking_result.update({
                    'is_duplicate': True,
                    'seen_count': new_seen_count,
                    'first_seen_date': datetime.fromisoformat(first_seen_date),
                    'action_taken': 'updated_existing'
                })
                
                self.tracking_stats['duplicate_urls_found'] += 1
                self.tracking_stats['urls_updated'] += 1
                
            else:
                # New URL - insert it
                cursor.execute('''
                    INSERT INTO property_urls_seen 
                    (property_url, first_seen_date, last_seen_date, seen_count, 
                     property_id, title, city, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (normalized_url, current_time, current_time, 1, 
                      property_id, title, city, 1, current_time))
                
                tracking_result.update({
                    'is_new_url': True,
                    'action_taken': 'inserted_new'
                })
                
                self.tracking_stats['new_urls_found'] += 1
            
            self.connection.commit()
            self.tracking_stats['urls_processed'] += 1
            
            return tracking_result
            
        except Exception as e:
            self.connection.rollback()
            return {'success': False, 'error': str(e)}
        
        finally:
            if self.connection:
                self.connection.close()
    
    def batch_track_urls(self, url_data: List[Dict[str, Any]], session_id: int = None) -> Dict[str, Any]:
        """Track multiple URLs in batch for efficiency"""
        
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
            
            result = self.track_property_url(url, title, city, session_id)
            
            if result['success']:
                if result['is_new_url']:
                    batch_results['new_urls'] += 1
                elif result['is_duplicate']:
                    batch_results['duplicate_urls'] += 1
            else:
                batch_results['errors'] += 1
            
            batch_results['url_results'].append(result)
            
            # Progress reporting
            if (i + 1) % 100 == 0:
                print(f"   [SUCCESS] Processed {i + 1}/{len(url_data)} URLs")
        
        batch_results['processing_time'] = (datetime.now() - start_time).total_seconds()
        
        print(f"   [STATS] Batch tracking complete: {batch_results['new_urls']} new, {batch_results['duplicate_urls']} duplicates")
        
        return batch_results
    
    def validate_incremental_scraping(self, current_urls: List[str], last_scrape_date: datetime) -> Dict[str, Any]:
        """Validate incremental scraping by checking URL overlap with previous scrapes"""
        
        if not self.connect_db():
            return {'success': False, 'error': 'Database connection failed'}
        
        print(f"🔍 Validating incremental scraping with {len(current_urls)} URLs...")
        
        try:
            cursor = self.connection.cursor()
            
            validation_result = {
                'success': True,
                'total_urls_checked': len(current_urls),
                'urls_seen_before': 0,
                'urls_seen_after_last_scrape': 0,
                'new_urls_found': 0,
                'validation_confidence': 0.0,
                'recommendation': '',
                'detailed_analysis': []
            }
            
            for url in current_urls:
                normalized_url = self.normalize_url(url)
                
                # Check if URL was seen before
                cursor.execute('''
                    SELECT first_seen_date, last_seen_date, seen_count 
                    FROM property_urls_seen 
                    WHERE property_url = ?
                ''', (normalized_url,))
                
                result = cursor.fetchone()
                
                url_analysis = {
                    'url': normalized_url,
                    'seen_before': False,
                    'first_seen_date': None,
                    'last_seen_date': None,
                    'seen_count': 0,
                    'is_new_since_last_scrape': False
                }
                
                if result:
                    first_seen_str, last_seen_str, seen_count = result
                    first_seen_date = datetime.fromisoformat(first_seen_str)
                    last_seen_date = datetime.fromisoformat(last_seen_str)
                    
                    url_analysis.update({
                        'seen_before': True,
                        'first_seen_date': first_seen_date,
                        'last_seen_date': last_seen_date,
                        'seen_count': seen_count,
                        'is_new_since_last_scrape': first_seen_date > last_scrape_date
                    })
                    
                    validation_result['urls_seen_before'] += 1
                    
                    if first_seen_date > last_scrape_date:
                        validation_result['urls_seen_after_last_scrape'] += 1
                else:
                    validation_result['new_urls_found'] += 1
                    url_analysis['is_new_since_last_scrape'] = True
                
                validation_result['detailed_analysis'].append(url_analysis)
                
                self.tracking_stats['validation_checks'] += 1
                if url_analysis['seen_before']:
                    self.tracking_stats['validation_matches'] += 1
            
            # Calculate validation confidence
            if validation_result['total_urls_checked'] > 0:
                new_or_recent_urls = (validation_result['new_urls_found'] + 
                                    validation_result['urls_seen_after_last_scrape'])
                validation_result['validation_confidence'] = (new_or_recent_urls / 
                                                            validation_result['total_urls_checked'])
            
            # Generate recommendation
            if validation_result['validation_confidence'] > 0.8:
                validation_result['recommendation'] = 'High confidence - mostly new properties found'
            elif validation_result['validation_confidence'] > 0.5:
                validation_result['recommendation'] = 'Medium confidence - mixed new and old properties'
            elif validation_result['validation_confidence'] > 0.2:
                validation_result['recommendation'] = 'Low confidence - mostly old properties, consider stopping'
            else:
                validation_result['recommendation'] = 'Very low confidence - likely reached old territory, should stop'
            
            print(f"   [STATS] Validation confidence: {validation_result['validation_confidence']:.2f}")
            print(f"   [INFO] Recommendation: {validation_result['recommendation']}")
            
            return validation_result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
        finally:
            if self.connection:
                self.connection.close()
    
    def cleanup_old_urls(self, days_to_keep: int = None) -> Dict[str, Any]:
        """Clean up old URLs to maintain database performance"""
        
        if days_to_keep is None:
            days_to_keep = self.tracking_config['url_cache_days']
        
        if not self.connect_db():
            return {'success': False, 'error': 'Database connection failed'}
        
        try:
            cursor = self.connection.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Mark old URLs as inactive instead of deleting
            cursor.execute('''
                UPDATE property_urls_seen 
                SET is_active = 0 
                WHERE last_seen_date < ? AND is_active = 1
            ''', (cutoff_date,))
            
            inactive_count = cursor.rowcount
            
            self.connection.commit()
            
            print(f"🧹 Marked {inactive_count} old URLs as inactive")
            
            return {
                'success': True,
                'urls_marked_inactive': inactive_count,
                'cutoff_date': cutoff_date
            }
            
        except Exception as e:
            self.connection.rollback()
            return {'success': False, 'error': str(e)}
        
        finally:
            if self.connection:
                self.connection.close()
    
    def get_tracking_statistics(self) -> Dict[str, Any]:
        """Get comprehensive URL tracking statistics"""
        
        if not self.connect_db():
            return {'success': False, 'error': 'Database connection failed'}
        
        try:
            cursor = self.connection.cursor()
            
            # Get database statistics
            cursor.execute('SELECT COUNT(*) FROM property_urls_seen WHERE is_active = 1')
            active_urls = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM property_urls_seen WHERE is_active = 0')
            inactive_urls = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(seen_count) FROM property_urls_seen WHERE is_active = 1')
            avg_seen_count = cursor.fetchone()[0] or 0
            
            # Combine with runtime statistics
            stats = {
                'database_stats': {
                    'active_urls': active_urls,
                    'inactive_urls': inactive_urls,
                    'total_urls': active_urls + inactive_urls,
                    'average_seen_count': round(avg_seen_count, 2)
                },
                'runtime_stats': self.tracking_stats,
                'configuration': self.tracking_config
            }
            
            return {'success': True, 'statistics': stats}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
        finally:
            if self.connection:
                self.connection.close()
    
    def test_url_tracking_system(self) -> Dict[str, Any]:
        """Test the URL tracking system with sample data"""
        
        print("🧪 TESTING URL TRACKING SYSTEM")
        print("="*50)
        
        # Test URLs (simulated MagicBricks URLs)
        test_urls = [
            {
                'url': 'https://www.magicbricks.com/property-details/2-bhk-apartment-for-sale-in-gurgaon-123456',
                'title': '2 BHK Apartment in Gurgaon',
                'city': 'gurgaon'
            },
            {
                'url': 'https://www.magicbricks.com/property-details/3-bhk-apartment-for-sale-in-mumbai-789012',
                'title': '3 BHK Apartment in Mumbai',
                'city': 'mumbai'
            },
            {
                'url': 'https://www.magicbricks.com/property-details/2-bhk-apartment-for-sale-in-gurgaon-123456?ref=search',
                'title': '2 BHK Apartment in Gurgaon (duplicate with tracking param)',
                'city': 'gurgaon'
            }
        ]
        
        test_results = {
            'urls_tested': len(test_urls),
            'tracking_successful': 0,
            'new_urls_detected': 0,
            'duplicates_detected': 0,
            'validation_test_passed': False
        }
        
        print(f"[TEST] Testing URL tracking with {len(test_urls)} URLs...")
        
        # Test batch tracking
        batch_result = self.batch_track_urls(test_urls)
        
        test_results['tracking_successful'] = batch_result['total_urls'] - batch_result['errors']
        test_results['new_urls_detected'] = batch_result['new_urls']
        test_results['duplicates_detected'] = batch_result['duplicate_urls']
        
        # Test validation
        current_urls = [url_info['url'] for url_info in test_urls]
        last_scrape_date = datetime.now() - timedelta(days=1)
        
        validation_result = self.validate_incremental_scraping(current_urls, last_scrape_date)
        test_results['validation_test_passed'] = validation_result['success']
        
        # Get statistics
        stats_result = self.get_tracking_statistics()
        
        print(f"\n[STATS] URL TRACKING SYSTEM TEST RESULTS")
        print("="*50)
        print(f"[SUCCESS] URLs tested: {test_results['urls_tested']}")
        print(f"[SUCCESS] Tracking successful: {test_results['tracking_successful']}")
        print(f"[NEW] New URLs detected: {test_results['new_urls_detected']}")
        print(f"[DUP] Duplicates detected: {test_results['duplicates_detected']}")
        print(f"[SUCCESS] Validation test passed: {test_results['validation_test_passed']}")
        
        if stats_result['success']:
            db_stats = stats_result['statistics']['database_stats']
            print(f"[STATS] Total URLs in database: {db_stats['total_urls']}")
            print(f"[STATS] Active URLs: {db_stats['active_urls']}")
        
        return test_results


def main():
    """Main function for URL tracking system testing"""
    
    try:
        url_tracker = URLTrackingSystem()
        test_results = url_tracker.test_url_tracking_system()
        
        if (test_results['tracking_successful'] >= test_results['urls_tested'] * 0.8 and
            test_results['validation_test_passed']):
            print("\n[SUCCESS] URL tracking system test successful!")
            return True
        else:
            print("\n[WARNING] URL tracking system needs improvement!")
            return False
            
    except Exception as e:
        print(f"[ERROR] URL tracking system test failed: {str(e)}")
        return False


if __name__ == "__main__":
    main()
