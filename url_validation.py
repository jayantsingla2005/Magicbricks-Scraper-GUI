#!/usr/bin/env python3
"""
URL Validation Module
Provides validation and maintenance functionality for URL tracking.
Handles incremental scraping validation, cleanup, and statistics.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from url_normalization import URLNormalizer


class URLValidator:
    """
    URL validation and maintenance operations
    """
    
    def __init__(self, db_path: str, normalizer: URLNormalizer = None):
        """
        Initialize URL validator
        
        Args:
            db_path: Path to SQLite database
            normalizer: URLNormalizer instance (creates new if None)
        """
        self.db_path = db_path
        self.normalizer = normalizer or URLNormalizer()
        
        # Validation statistics
        self.validation_stats = {
            'validation_checks': 0,
            'validation_matches': 0
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
    
    def validate_incremental_scraping(
        self, 
        current_urls: List[str], 
        last_scrape_date: datetime
    ) -> Dict[str, Any]:
        """
        Validate incremental scraping by checking URL overlap with previous scrapes
        
        Args:
            current_urls: List of URLs from current scrape
            last_scrape_date: Date of last scraping session
            
        Returns:
            Dictionary with validation results:
            - success: bool
            - total_urls_checked: int
            - urls_seen_before: int
            - urls_seen_after_last_scrape: int
            - new_urls_found: int
            - validation_confidence: float (0-1)
            - recommendation: str
            - detailed_analysis: list of URL analysis
        """
        connection = self.connect_db()
        if not connection:
            return {'success': False, 'error': 'Database connection failed'}
        
        print(f"🔍 Validating incremental scraping with {len(current_urls)} URLs...")
        
        try:
            cursor = connection.cursor()
            
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
                normalized_url = self.normalizer.normalize_url(url)
                
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
                
                self.validation_stats['validation_checks'] += 1
                if url_analysis['seen_before']:
                    self.validation_stats['validation_matches'] += 1
            
            # Calculate validation confidence
            if validation_result['total_urls_checked'] > 0:
                new_or_recent_urls = (
                    validation_result['new_urls_found'] + 
                    validation_result['urls_seen_after_last_scrape']
                )
                validation_result['validation_confidence'] = (
                    new_or_recent_urls / validation_result['total_urls_checked']
                )
            
            # Generate recommendation
            confidence = validation_result['validation_confidence']
            if confidence > 0.8:
                validation_result['recommendation'] = (
                    'High confidence - mostly new properties found'
                )
            elif confidence > 0.5:
                validation_result['recommendation'] = (
                    'Medium confidence - mixed new and old properties'
                )
            elif confidence > 0.2:
                validation_result['recommendation'] = (
                    'Low confidence - mostly old properties, consider stopping'
                )
            else:
                validation_result['recommendation'] = (
                    'Very low confidence - likely reached old territory, should stop'
                )
            
            print(f"   [STATS] Validation confidence: {confidence:.2f}")
            print(f"   [INFO] Recommendation: {validation_result['recommendation']}")
            
            return validation_result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
        finally:
            if connection:
                connection.close()
    
    def cleanup_old_urls(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """
        Clean up old URLs to maintain database performance
        
        Marks URLs as inactive instead of deleting them to preserve history.
        
        Args:
            days_to_keep: Number of days to keep URLs active
            
        Returns:
            Dictionary with cleanup results:
            - success: bool
            - urls_marked_inactive: int
            - cutoff_date: datetime
        """
        connection = self.connect_db()
        if not connection:
            return {'success': False, 'error': 'Database connection failed'}
        
        try:
            cursor = connection.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Mark old URLs as inactive instead of deleting
            cursor.execute('''
                UPDATE property_urls_seen 
                SET is_active = 0 
                WHERE last_seen_date < ? AND is_active = 1
            ''', (cutoff_date,))
            
            inactive_count = cursor.rowcount
            
            connection.commit()
            
            print(f"🧹 Marked {inactive_count} old URLs as inactive")
            
            return {
                'success': True,
                'urls_marked_inactive': inactive_count,
                'cutoff_date': cutoff_date
            }
            
        except Exception as e:
            connection.rollback()
            return {'success': False, 'error': str(e)}
        
        finally:
            if connection:
                connection.close()
    
    def get_tracking_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive URL tracking statistics from database
        
        Returns:
            Dictionary with statistics:
            - success: bool
            - statistics: dict with database_stats and runtime_stats
        """
        connection = self.connect_db()
        if not connection:
            return {'success': False, 'error': 'Database connection failed'}
        
        try:
            cursor = connection.cursor()
            
            # Get database statistics
            cursor.execute(
                'SELECT COUNT(*) FROM property_urls_seen WHERE is_active = 1'
            )
            active_urls = cursor.fetchone()[0]
            
            cursor.execute(
                'SELECT COUNT(*) FROM property_urls_seen WHERE is_active = 0'
            )
            inactive_urls = cursor.fetchone()[0]
            
            cursor.execute(
                'SELECT AVG(seen_count) FROM property_urls_seen WHERE is_active = 1'
            )
            avg_seen_count = cursor.fetchone()[0] or 0
            
            stats = {
                'database_stats': {
                    'active_urls': active_urls,
                    'inactive_urls': inactive_urls,
                    'total_urls': active_urls + inactive_urls,
                    'average_seen_count': round(avg_seen_count, 2)
                },
                'validation_stats': self.validation_stats
            }
            
            return {'success': True, 'statistics': stats}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
        finally:
            if connection:
                connection.close()
    
    def get_validation_stats(self) -> Dict[str, int]:
        """
        Get current validation statistics
        
        Returns:
            Dictionary with validation stats
        """
        return self.validation_stats.copy()
    
    def reset_validation_stats(self):
        """Reset validation statistics"""
        self.validation_stats = {
            'validation_checks': 0,
            'validation_matches': 0
        }

