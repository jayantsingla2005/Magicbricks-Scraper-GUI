#!/usr/bin/env python3
"""
Unit tests for P0-1: Smart PDP Filtering
Tests the smart filtering logic that reduces PDP volume by 50-80%
"""
import unittest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.individual_property_scraper import IndividualPropertyScraper


class TestSmartFiltering(unittest.TestCase):
    """Test smart filtering functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_driver = Mock()
        self.mock_extractor = Mock()
        self.mock_bot_handler = Mock()
        self.mock_tracker = Mock()
        self.mock_logger = Mock()
        
        self.scraper = IndividualPropertyScraper(
            driver=self.mock_driver,
            property_extractor=self.mock_extractor,
            bot_handler=self.mock_bot_handler,
            individual_tracker=self.mock_tracker,
            logger=self.mock_logger
        )
    
    def test_smart_filter_new_urls(self):
        """Test that new URLs (never scraped) are included"""
        test_urls = [
            'https://www.magicbricks.com/property-1',
            'https://www.magicbricks.com/property-2',
            'https://www.magicbricks.com/property-3'
        ]
        
        # Mock database connection
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.connection.cursor.return_value = mock_cursor
        
        # All URLs return None (never scraped)
        mock_cursor.fetchone.return_value = None
        
        self.mock_tracker.db_manager = mock_db
        self.mock_tracker.db_manager.connect_db.return_value = True
        self.mock_tracker.normalize_url = lambda url: url
        self.mock_tracker.generate_url_hash = lambda url: f"hash_{url}"
        
        result = self.scraper._smart_filter_urls(test_urls, quality_threshold=60.0, ttl_days=30)
        
        # All new URLs should be included
        self.assertEqual(len(result), 3)
        self.assertEqual(result, test_urls)
    
    def test_smart_filter_low_quality(self):
        """Test that low quality URLs are included for re-scraping"""
        test_urls = ['https://www.magicbricks.com/property-1']
        
        # Mock database connection
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.connection.cursor.return_value = mock_cursor
        
        # URL exists with low quality score (40%)
        scraped_at = datetime.now().isoformat()
        mock_cursor.fetchone.return_value = (scraped_at, 40.0, True)
        
        self.mock_tracker.db_manager = mock_db
        self.mock_tracker.db_manager.connect_db.return_value = True
        self.mock_tracker.normalize_url = lambda url: url
        self.mock_tracker.generate_url_hash = lambda url: f"hash_{url}"
        
        result = self.scraper._smart_filter_urls(test_urls, quality_threshold=60.0, ttl_days=30)
        
        # Low quality URL should be included
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], test_urls[0])
    
    def test_smart_filter_stale_data(self):
        """Test that stale URLs (older than TTL) are included"""
        test_urls = ['https://www.magicbricks.com/property-1']
        
        # Mock database connection
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.connection.cursor.return_value = mock_cursor
        
        # URL exists with good quality but old data (45 days ago)
        scraped_at = (datetime.now() - timedelta(days=45)).isoformat()
        mock_cursor.fetchone.return_value = (scraped_at, 80.0, True)
        
        self.mock_tracker.db_manager = mock_db
        self.mock_tracker.db_manager.connect_db.return_value = True
        self.mock_tracker.normalize_url = lambda url: url
        self.mock_tracker.generate_url_hash = lambda url: f"hash_{url}"
        
        result = self.scraper._smart_filter_urls(test_urls, quality_threshold=60.0, ttl_days=30)
        
        # Stale URL should be included
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], test_urls[0])
    
    def test_smart_filter_skip_good_fresh(self):
        """Test that good quality + fresh URLs are skipped"""
        test_urls = ['https://www.magicbricks.com/property-1']
        
        # Mock database connection
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.connection.cursor.return_value = mock_cursor
        
        # URL exists with good quality and fresh data (5 days ago)
        scraped_at = (datetime.now() - timedelta(days=5)).isoformat()
        mock_cursor.fetchone.return_value = (scraped_at, 85.0, True)
        
        self.mock_tracker.db_manager = mock_db
        self.mock_tracker.db_manager.connect_db.return_value = True
        self.mock_tracker.normalize_url = lambda url: url
        self.mock_tracker.generate_url_hash = lambda url: f"hash_{url}"
        
        result = self.scraper._smart_filter_urls(test_urls, quality_threshold=60.0, ttl_days=30)
        
        # Good + fresh URL should be skipped
        self.assertEqual(len(result), 0)
    
    def test_smart_filter_failed_extraction(self):
        """Test that URLs with failed extraction are included"""
        test_urls = ['https://www.magicbricks.com/property-1']
        
        # Mock database connection
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.connection.cursor.return_value = mock_cursor
        
        # URL exists but extraction failed
        scraped_at = datetime.now().isoformat()
        mock_cursor.fetchone.return_value = (scraped_at, 0.0, False)  # extraction_success = False
        
        self.mock_tracker.db_manager = mock_db
        self.mock_tracker.db_manager.connect_db.return_value = True
        self.mock_tracker.normalize_url = lambda url: url
        self.mock_tracker.generate_url_hash = lambda url: f"hash_{url}"
        
        result = self.scraper._smart_filter_urls(test_urls, quality_threshold=60.0, ttl_days=30)
        
        # Failed extraction URL should be included
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], test_urls[0])
    
    def test_smart_filter_mixed_batch(self):
        """Test filtering with mixed batch (new, low quality, stale, good)"""
        test_urls = [
            'https://www.magicbricks.com/new-property',
            'https://www.magicbricks.com/low-quality-property',
            'https://www.magicbricks.com/stale-property',
            'https://www.magicbricks.com/good-fresh-property'
        ]
        
        # Mock database connection
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.connection.cursor.return_value = mock_cursor
        
        # Define different responses for each URL
        def mock_fetchone_side_effect():
            responses = [
                None,  # new-property: never scraped
                (datetime.now().isoformat(), 45.0, True),  # low-quality: 45% quality
                ((datetime.now() - timedelta(days=40)).isoformat(), 75.0, True),  # stale: 40 days old
                ((datetime.now() - timedelta(days=5)).isoformat(), 85.0, True)  # good-fresh: 5 days old, 85% quality
            ]
            for response in responses:
                yield response
        
        mock_cursor.fetchone.side_effect = mock_fetchone_side_effect()
        
        self.mock_tracker.db_manager = mock_db
        self.mock_tracker.db_manager.connect_db.return_value = True
        self.mock_tracker.normalize_url = lambda url: url
        self.mock_tracker.generate_url_hash = lambda url: f"hash_{url}"
        
        result = self.scraper._smart_filter_urls(test_urls, quality_threshold=60.0, ttl_days=30)
        
        # Should include: new, low-quality, stale (3 URLs)
        # Should skip: good-fresh (1 URL)
        self.assertEqual(len(result), 3)
        self.assertIn('https://www.magicbricks.com/new-property', result)
        self.assertIn('https://www.magicbricks.com/low-quality-property', result)
        self.assertIn('https://www.magicbricks.com/stale-property', result)
        self.assertNotIn('https://www.magicbricks.com/good-fresh-property', result)


if __name__ == '__main__':
    unittest.main()

