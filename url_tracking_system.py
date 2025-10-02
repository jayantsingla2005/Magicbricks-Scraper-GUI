#!/usr/bin/env python3
"""
URL Tracking System Implementation
Refactored modular implementation using composition pattern.
Maintains backward compatibility while delegating to specialized modules.

This is a facade class that provides the same interface as before,
but delegates work to:
- url_normalization.py: URL processing utilities
- url_tracking_operations.py: Core tracking operations
- url_validation.py: Validation and maintenance
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Import refactored modules
from url_normalization import URLNormalizer
from url_tracking_operations import URLTrackingOperations
from url_validation import URLValidator


class URLTrackingSystem:
    """
    URL tracking system for backup validation in incremental scraping

    Refactored to use modular architecture with composition pattern.
    Maintains 100% backward compatibility with original interface.
    """

    def __init__(self, db_path: str = 'magicbricks_enhanced.db'):
        """
        Initialize URL tracking system

        Args:
            db_path: Path to SQLite database
        """
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

        # Initialize modular components
        self.normalizer = URLNormalizer(
            enable_normalization=self.tracking_config['enable_url_normalization']
        )
        self.operations = URLTrackingOperations(db_path, self.normalizer)
        self.validator = URLValidator(db_path, self.normalizer)

        # Tracking statistics (aggregated from modules)
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
        """
        Connect to database

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            return True
        except Exception as e:
            print(f"[ERROR] Database connection failed: {str(e)}")
            return False

    def normalize_url(self, url: str) -> str:
        """
        Normalize URL for consistent tracking

        Delegates to URLNormalizer module.

        Args:
            url: URL to normalize

        Returns:
            Normalized URL string
        """
        return self.normalizer.normalize_url(url)

    def generate_url_hash(self, url: str) -> str:
        """
        Generate hash for URL for efficient storage and lookup

        Delegates to URLNormalizer module.

        Args:
            url: URL to hash

        Returns:
            MD5 hash string
        """
        return self.normalizer.generate_url_hash(url)

    def extract_property_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract property ID from MagicBricks URL if possible

        Delegates to URLNormalizer module.

        Args:
            url: MagicBricks property URL

        Returns:
            Property ID string if found, None otherwise
        """
        return self.normalizer.extract_property_id_from_url(url)

    def track_property_url(
        self,
        url: str,
        title: str = None,
        city: str = None,
        session_id: int = None
    ) -> Dict[str, Any]:
        """
        Track a property URL and return tracking information

        Delegates to URLTrackingOperations module.

        Args:
            url: Property URL to track
            title: Property title (optional)
            city: City name (optional)
            session_id: Scraping session ID (optional)

        Returns:
            Dictionary with tracking result
        """
        result = self.operations.track_property_url(url, title, city, session_id)

        # Update aggregated statistics
        if result['success']:
            ops_stats = self.operations.get_stats()
            self.tracking_stats.update({
                'urls_processed': ops_stats['urls_processed'],
                'new_urls_found': ops_stats['new_urls_found'],
                'duplicate_urls_found': ops_stats['duplicate_urls_found'],
                'urls_updated': ops_stats['urls_updated']
            })

        return result

    def batch_track_urls(
        self,
        url_data: List[Dict[str, Any]],
        session_id: int = None
    ) -> Dict[str, Any]:
        """
        Track multiple URLs in batch for efficiency

        Delegates to URLTrackingOperations module.

        Args:
            url_data: List of dictionaries with 'url', 'title', 'city' keys
            session_id: Scraping session ID (optional)

        Returns:
            Dictionary with batch results
        """
        result = self.operations.batch_track_urls(url_data, session_id)

        # Update aggregated statistics
        ops_stats = self.operations.get_stats()
        self.tracking_stats.update({
            'urls_processed': ops_stats['urls_processed'],
            'new_urls_found': ops_stats['new_urls_found'],
            'duplicate_urls_found': ops_stats['duplicate_urls_found'],
            'urls_updated': ops_stats['urls_updated']
        })

        return result

    def validate_incremental_scraping(
        self,
        current_urls: List[str],
        last_scrape_date: datetime
    ) -> Dict[str, Any]:
        """
        Validate incremental scraping by checking URL overlap with previous scrapes

        Delegates to URLValidator module.

        Args:
            current_urls: List of URLs from current scrape
            last_scrape_date: Date of last scraping session

        Returns:
            Dictionary with validation results
        """
        result = self.validator.validate_incremental_scraping(
            current_urls,
            last_scrape_date
        )

        # Update aggregated statistics
        if result['success']:
            val_stats = self.validator.get_validation_stats()
            self.tracking_stats.update({
                'validation_checks': val_stats['validation_checks'],
                'validation_matches': val_stats['validation_matches']
            })

        return result

    def cleanup_old_urls(self, days_to_keep: int = None) -> Dict[str, Any]:
        """
        Clean up old URLs to maintain database performance

        Delegates to URLValidator module.

        Args:
            days_to_keep: Number of days to keep URLs active (default: from config)

        Returns:
            Dictionary with cleanup results
        """
        if days_to_keep is None:
            days_to_keep = self.tracking_config['url_cache_days']

        return self.validator.cleanup_old_urls(days_to_keep)

    def get_tracking_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive URL tracking statistics

        Delegates to URLValidator module and combines with runtime stats.

        Returns:
            Dictionary with statistics
        """
        result = self.validator.get_tracking_statistics()

        if result['success']:
            # Add runtime stats and configuration
            result['statistics']['runtime_stats'] = self.tracking_stats
            result['statistics']['configuration'] = self.tracking_config

        return result
    
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
