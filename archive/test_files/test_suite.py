#!/usr/bin/env python3
"""
Comprehensive Testing Suite for MagicBricks Scraper
Unit tests, integration tests, and automated testing for all components.
"""

import unittest
import tempfile
import shutil
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from incremental_scraping_system import IncrementalScrapingSystem
from user_mode_options import ScrapingMode, UserModeOptions
from date_parsing_system import DateParsingSystem
from smart_stopping_logic import SmartStoppingLogic
from url_tracking_system import URLTrackingSystem
from multi_city_system import MultiCitySystem, CityTier, Region
from error_handling_system import ErrorHandlingSystem, ErrorSeverity, ErrorCategory
from multi_city_parallel_processor import MultiCityParallelProcessor


class TestDateParsingSystem(unittest.TestCase):
    """Test the date parsing system"""
    
    def setUp(self):
        self.date_parser = DateParsingSystem()
    
    def test_parse_today(self):
        """Test parsing 'today' text"""
        result = self.date_parser.parse_posting_date("Posted today")
        self.assertTrue(result['success'])
        self.assertEqual(result['parsed_datetime'].date(), datetime.now().date())
    
    def test_parse_hours_ago(self):
        """Test parsing 'X hours ago' text"""
        result = self.date_parser.parse_posting_date("Posted 5 hours ago")
        self.assertTrue(result['success'])
        expected_time = datetime.now() - timedelta(hours=5)
        self.assertAlmostEqual(
            result['parsed_datetime'].timestamp(),
            expected_time.timestamp(),
            delta=3600  # 1 hour tolerance
        )
    
    def test_parse_days_ago(self):
        """Test parsing 'X days ago' text"""
        result = self.date_parser.parse_posting_date("Posted 3 days ago")
        self.assertTrue(result['success'])
        expected_time = datetime.now() - timedelta(days=3)
        self.assertAlmostEqual(
            result['parsed_datetime'].timestamp(),
            expected_time.timestamp(),
            delta=86400  # 1 day tolerance
        )
    
    def test_parse_invalid_text(self):
        """Test parsing invalid text"""
        result = self.date_parser.parse_posting_date("Invalid date text")
        self.assertFalse(result['success'])
    
    def test_parse_empty_text(self):
        """Test parsing empty text"""
        result = self.date_parser.parse_posting_date("")
        self.assertFalse(result['success'])


class TestSmartStoppingLogic(unittest.TestCase):
    """Test the smart stopping logic"""
    
    def setUp(self):
        self.stopping_logic = SmartStoppingLogic()
        self.last_scrape_date = datetime.now() - timedelta(days=1)
    
    def test_should_stop_high_old_percentage(self):
        """Test stopping when high percentage of old properties"""
        # Create mock property texts with old dates
        property_texts = [
            "Posted 2 days ago",
            "Posted 3 days ago",
            "Posted 4 days ago",
            "Posted 5 days ago",
            "Posted today"  # Only 1 new property
        ]

        result = self.stopping_logic.analyze_page_for_stopping(
            property_texts, self.last_scrape_date, page_number=2
        )

        self.assertTrue(result['should_stop'])
        self.assertIn('old', result['stop_reason'].lower())
    
    def test_should_continue_low_old_percentage(self):
        """Test continuing when low percentage of old properties"""
        property_texts = [
            "Posted today",
            "Posted 2 hours ago",
            "Posted 4 hours ago",
            "Posted 6 hours ago",
            "Posted 2 days ago"  # Only 1 old property
        ]

        result = self.stopping_logic.analyze_page_for_stopping(
            property_texts, self.last_scrape_date, page_number=2
        )

        self.assertFalse(result['should_stop'])
    
    def test_first_page_never_stops(self):
        """Test that first page never stops regardless of content"""
        property_texts = [
            "Posted 5 days ago",
            "Posted 6 days ago",
            "Posted 7 days ago"
        ]

        result = self.stopping_logic.analyze_page_for_stopping(
            property_texts, self.last_scrape_date, page_number=1
        )

        self.assertFalse(result['should_stop'])


class TestURLTrackingSystem(unittest.TestCase):
    """Test the URL tracking system"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_tracking.db')
        self.url_tracker = URLTrackingSystem(self.db_path)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_track_new_urls(self):
        """Test tracking new URLs"""
        session_id = 1
        url_data = [
            {"url": "https://magicbricks.com/property1", "title": "Property 1"},
            {"url": "https://magicbricks.com/property2", "title": "Property 2"}
        ]

        result = self.url_tracker.batch_track_urls(url_data, session_id)

        self.assertEqual(result['new_urls'], 2)
        self.assertEqual(result['duplicate_urls'], 0)
    
    def test_track_duplicate_urls(self):
        """Test tracking duplicate URLs"""
        session_id = 1
        url_data = [
            {"url": "https://magicbricks.com/property1", "title": "Property 1"},
            {"url": "https://magicbricks.com/property2", "title": "Property 2"}
        ]

        # Track URLs first time
        self.url_tracker.batch_track_urls(url_data, session_id)

        # Track same URLs again
        result = self.url_tracker.batch_track_urls(url_data, session_id)

        self.assertEqual(result['new_urls'], 0)
        self.assertEqual(result['duplicate_urls'], 2)
    
    def test_mixed_new_and_duplicate_urls(self):
        """Test tracking mix of new and duplicate URLs"""
        session_id = 1

        # First batch
        url_data1 = [
            {"url": "https://magicbricks.com/property1", "title": "Property 1"},
            {"url": "https://magicbricks.com/property2", "title": "Property 2"}
        ]
        self.url_tracker.batch_track_urls(url_data1, session_id)

        # Second batch with mix
        url_data2 = [
            {"url": "https://magicbricks.com/property1", "title": "Property 1"},  # Duplicate
            {"url": "https://magicbricks.com/property3", "title": "Property 3"}   # New
        ]
        result = self.url_tracker.batch_track_urls(url_data2, session_id)

        self.assertEqual(result['new_urls'], 1)
        self.assertEqual(result['duplicate_urls'], 1)


class TestMultiCitySystem(unittest.TestCase):
    """Test the multi-city system"""
    
    def setUp(self):
        self.city_system = MultiCitySystem()
    
    def test_get_cities_by_region(self):
        """Test getting cities by region"""
        north_cities = self.city_system.get_cities_by_region(Region.NORTH)
        self.assertGreater(len(north_cities), 0)
        
        # Check all cities are from North region
        for city in north_cities:
            self.assertEqual(city.region, Region.NORTH)
    
    def test_get_cities_by_tier(self):
        """Test getting cities by tier"""
        tier1_cities = self.city_system.get_cities_by_tier(CityTier.TIER_1)
        self.assertGreater(len(tier1_cities), 0)
        
        # Check all cities are Tier 1
        for city in tier1_cities:
            self.assertEqual(city.tier, CityTier.TIER_1)
    
    def test_get_metro_cities(self):
        """Test getting metro cities"""
        metro_cities = self.city_system.get_metro_cities()
        self.assertGreater(len(metro_cities), 0)
        
        # Check all cities are metros
        for city in metro_cities:
            self.assertTrue(city.is_metro)
    
    def test_search_cities(self):
        """Test city search functionality"""
        # Search for Mumbai
        results = self.city_system.search_cities("mumbai")
        self.assertGreater(len(results), 0)
        
        # Check Mumbai is in results
        mumbai_found = any(city.name.lower() == "mumbai" for city in results)
        self.assertTrue(mumbai_found)
    
    def test_validate_city_selection(self):
        """Test city selection validation"""
        # Valid cities
        valid_result = self.city_system.validate_city_selection(['DEL', 'MUM', 'BLR'])
        self.assertEqual(len(valid_result['valid_cities']), 3)
        self.assertEqual(len(valid_result['invalid_cities']), 0)
        
        # Invalid cities
        invalid_result = self.city_system.validate_city_selection(['INVALID1', 'INVALID2'])
        self.assertEqual(len(valid_result['valid_cities']), 3)  # From previous test
        self.assertEqual(len(invalid_result['invalid_cities']), 2)
    
    def test_generate_scraping_urls(self):
        """Test URL generation for cities"""
        urls = self.city_system.generate_scraping_urls(['DEL', 'MUM'], 'sale')
        
        self.assertEqual(len(urls), 2)
        self.assertIn('DEL', urls)
        self.assertIn('MUM', urls)
        
        # Check URL format
        for url in urls.values():
            self.assertIn('magicbricks.com', url)
            self.assertIn('property-for-sale', url)


class TestErrorHandlingSystem(unittest.TestCase):
    """Test the error handling system"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(self.temp_dir, 'test_error_config.json')
        self.error_system = ErrorHandlingSystem(config_file)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_handle_network_error(self):
        """Test handling network errors"""
        error = ConnectionError("Failed to connect to server")
        error_info = self.error_system.handle_error(error, {'url': 'test.com'}, 'test_action')
        
        self.assertEqual(error_info.category, ErrorCategory.NETWORK)
        self.assertEqual(error_info.severity, ErrorSeverity.ERROR)
        self.assertIn('connection', error_info.suggestion.lower())
    
    def test_handle_validation_error(self):
        """Test handling validation errors"""
        error = ValueError("Invalid input parameter")
        error_info = self.error_system.handle_error(error, {'param': 'test'}, 'validation')
        
        self.assertEqual(error_info.category, ErrorCategory.VALIDATION)
        self.assertIn('input', error_info.suggestion.lower())
    
    def test_error_log_management(self):
        """Test error log management"""
        # Add some errors
        for i in range(5):
            error = Exception(f"Test error {i}")
            self.error_system.handle_error(error)
        
        # Check error count
        summary = self.error_system.get_error_summary()
        self.assertEqual(summary['total_errors'], 5)
        
        # Test filtering
        filtered = self.error_system.get_filtered_errors(severity=ErrorSeverity.ERROR)
        self.assertGreater(len(filtered), 0)
    
    def test_error_export(self):
        """Test error log export"""
        # Add an error
        error = Exception("Test export error")
        self.error_system.handle_error(error)
        
        # Export
        export_file = self.error_system.export_error_log()
        self.assertIsNotNone(export_file)
        self.assertTrue(os.path.exists(export_file))
        
        # Clean up
        if export_file and os.path.exists(export_file):
            os.remove(export_file)


class TestUserModeOptions(unittest.TestCase):
    """Test user mode options"""
    
    def setUp(self):
        self.mode_options = UserModeOptions()
    
    def test_get_mode_config(self):
        """Test getting mode configuration"""
        incremental_config = self.mode_options.get_mode_config(ScrapingMode.INCREMENTAL)
        self.assertIn('description', incremental_config)
        self.assertIn('time_savings', incremental_config)
        self.assertIn('recommended_for', incremental_config)
    
    def test_validate_mode_config(self):
        """Test mode configuration validation"""
        # Valid config
        valid_config = {
            'max_pages': 100,
            'city': 'mumbai'
        }
        result = self.mode_options.validate_mode_configuration(ScrapingMode.INCREMENTAL, valid_config)
        self.assertTrue(result['valid'])

        # Invalid config
        invalid_config = {
            'max_pages': -1,  # Invalid
            'city': ''  # Invalid
        }
        result = self.mode_options.validate_mode_configuration(ScrapingMode.INCREMENTAL, invalid_config)
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)


class TestIncrementalScrapingSystem(unittest.TestCase):
    """Test the incremental scraping system"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_incremental.db')
        self.incremental_system = IncrementalScrapingSystem(self.db_path)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_setup_system(self):
        """Test system setup"""
        success = self.incremental_system.setup_system()
        self.assertTrue(success)
        
        # Check database exists
        self.assertTrue(os.path.exists(self.db_path))
    
    def test_start_incremental_scraping(self):
        """Test starting incremental scraping"""
        self.incremental_system.setup_system()
        
        result = self.incremental_system.start_incremental_scraping(
            'mumbai', ScrapingMode.INCREMENTAL
        )
        
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['session_id'])
    
    @patch('incremental_scraping_system.DateParsingSystem')
    def test_analyze_page_for_incremental_decision(self, mock_date_parser):
        """Test page analysis for incremental decision"""
        # Mock date parser
        mock_parser_instance = Mock()
        mock_date_parser.return_value = mock_parser_instance
        
        # Mock old properties
        mock_parser_instance.parse_posting_date.return_value = {
            'success': True,
            'parsed_datetime': datetime.now() - timedelta(days=2)
        }
        
        self.incremental_system.setup_system()
        session_id = "test_session"
        last_scrape_date = datetime.now() - timedelta(days=1)
        
        property_texts = ["Posted 2 days ago"] * 10  # All old properties
        
        result = self.incremental_system.analyze_page_for_incremental_decision(
            property_texts, session_id, 2, last_scrape_date
        )
        
        self.assertTrue(result['should_stop'])
        self.assertGreater(result['date_analysis']['old_percentage'], 80)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_incremental_system_integration(self):
        """Test integration between incremental system components"""
        db_path = os.path.join(self.temp_dir, 'integration_test.db')
        
        # Initialize systems
        incremental_system = IncrementalScrapingSystem(db_path)
        url_tracker = URLTrackingSystem(db_path)
        date_parser = DateParsingSystem()
        
        # Setup
        incremental_system.setup_system()
        
        # Start session
        session_result = incremental_system.start_incremental_scraping(
            'mumbai', ScrapingMode.INCREMENTAL
        )
        self.assertTrue(session_result['success'])
        
        session_id = session_result['session_id']
        
        # Track some URLs
        url_data = [
            {"url": "https://magicbricks.com/property1", "title": "Property 1"},
            {"url": "https://magicbricks.com/property2", "title": "Property 2"}
        ]
        url_result = url_tracker.batch_track_urls(url_data, int(session_id))
        self.assertEqual(url_result['new_urls'], 2)
        
        # Parse some dates
        date_result = date_parser.parse_posting_date("Posted today")
        self.assertTrue(date_result['success'])
    
    def test_multi_city_parallel_integration(self):
        """Test integration of multi-city system with parallel processor"""
        # Mock progress callback
        progress_updates = []
        def progress_callback(data):
            progress_updates.append(data)
        
        # Initialize processor
        processor = MultiCityParallelProcessor(max_workers=2, progress_callback=progress_callback)
        
        # Test configuration
        test_config = {
            'mode': ScrapingMode.INCREMENTAL,
            'max_pages': 1,  # Very small test
            'headless': True,
            'incremental_enabled': True,
            'output_directory': self.temp_dir
        }
        
        # This would normally start actual scraping, but we're just testing the setup
        # In a real test environment, we'd mock the scraper components
        self.assertIsNotNone(processor.city_system)
        self.assertIsNotNone(processor.error_system)


def run_all_tests():
    """Run all tests and generate report"""
    
    print("🧪 RUNNING COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestDateParsingSystem,
        TestSmartStoppingLogic,
        TestURLTrackingSystem,
        TestMultiCitySystem,
        TestErrorHandlingSystem,
        TestUserModeOptions,
        TestIncrementalScrapingSystem,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)
    
    # Generate report
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ FAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\n🚨 ERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    if not result.failures and not result.errors:
        print("\n✅ ALL TESTS PASSED!")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
