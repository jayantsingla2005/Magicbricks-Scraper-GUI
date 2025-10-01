#!/usr/bin/env python3
"""
Unit Tests for BotDetectionHandler Module
Tests bot detection, recovery strategies, and user agent rotation
"""

import unittest
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.bot_detection_handler import BotDetectionHandler


class TestBotDetectionHandler(unittest.TestCase):
    """Test suite for BotDetectionHandler class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.handler = BotDetectionHandler(logger=None)
    
    def test_initialization(self):
        """Test BotDetectionHandler initialization"""
        self.assertIsNotNone(self.handler)
        self.assertEqual(self.handler.bot_detection_count, 0)
        self.assertIsNone(self.handler.last_detection_time)
        self.assertEqual(self.handler.consecutive_failures, 0)
    
    def test_detect_bot_detection_with_captcha(self):
        """Test bot detection with captcha indicator"""
        page_source = "<html><body>Please solve this captcha</body></html>"
        current_url = "https://www.magicbricks.com/property"
        
        result = self.handler.detect_bot_detection(page_source, current_url)
        
        self.assertTrue(result)
    
    def test_detect_bot_detection_with_cloudflare(self):
        """Test bot detection with Cloudflare indicator"""
        page_source = "<html><body>Cloudflare security check</body></html>"
        current_url = "https://www.magicbricks.com/property"
        
        result = self.handler.detect_bot_detection(page_source, current_url)
        
        self.assertTrue(result)
    
    def test_detect_bot_detection_with_access_denied(self):
        """Test bot detection with access denied"""
        page_source = "<html><body>Access Denied</body></html>"
        current_url = "https://www.magicbricks.com/property"
        
        result = self.handler.detect_bot_detection(page_source, current_url)
        
        self.assertTrue(result)
    
    def test_detect_bot_detection_no_indicators(self):
        """Test bot detection without any indicators"""
        page_source = "<html><body>Normal property page content</body></html>"
        current_url = "https://www.magicbricks.com/property-123"
        
        result = self.handler.detect_bot_detection(page_source, current_url)
        
        self.assertFalse(result)
    
    def test_detect_bot_detection_case_insensitive(self):
        """Test bot detection is case insensitive"""
        page_source = "<html><body>CAPTCHA verification required</body></html>"
        current_url = "https://www.magicbricks.com/property"
        
        result = self.handler.detect_bot_detection(page_source, current_url)
        
        self.assertTrue(result)
    
    def test_handle_bot_detection_strategy_1(self):
        """Test bot detection handling - Strategy 1 (first 2 detections)"""
        mock_callback = Mock()
        
        # First detection
        with patch('time.sleep'):  # Mock sleep to speed up test
            self.handler.handle_bot_detection(mock_callback)
        
        self.assertEqual(self.handler.bot_detection_count, 1)
        self.assertIsNotNone(self.handler.last_detection_time)
        mock_callback.assert_called_once()
    
    def test_handle_bot_detection_strategy_2(self):
        """Test bot detection handling - Strategy 2 (3-4 detections)"""
        mock_callback = Mock()
        
        # Simulate 3 detections
        self.handler.bot_detection_count = 2
        
        with patch('time.sleep'):
            self.handler.handle_bot_detection(mock_callback)
        
        self.assertEqual(self.handler.bot_detection_count, 3)
        mock_callback.assert_called_once()
    
    def test_handle_bot_detection_strategy_3(self):
        """Test bot detection handling - Strategy 3 (5+ detections)"""
        mock_callback = Mock()
        
        # Simulate 5 detections
        self.handler.bot_detection_count = 4
        
        with patch('time.sleep'):
            self.handler.handle_bot_detection(mock_callback)
        
        self.assertEqual(self.handler.bot_detection_count, 5)
        mock_callback.assert_called_once()
    
    def test_get_enhanced_user_agents(self):
        """Test user agent list retrieval"""
        user_agents = self.handler.get_enhanced_user_agents()
        
        self.assertIsInstance(user_agents, list)
        self.assertGreater(len(user_agents), 0)
        self.assertTrue(all(isinstance(ua, str) for ua in user_agents))
        self.assertTrue(all('Mozilla' in ua for ua in user_agents))
    
    def test_user_agent_rotation(self):
        """Test user agent rotation during bot detection"""
        mock_callback = Mock()
        initial_index = self.handler.current_user_agent_index
        
        with patch('time.sleep'):
            self.handler.handle_bot_detection(mock_callback)
        
        # User agent index should have rotated
        self.assertNotEqual(self.handler.current_user_agent_index, initial_index)
    
    def test_calculate_enhanced_delay_no_failures(self):
        """Test delay calculation with no failures"""
        delay = self.handler.calculate_enhanced_delay(2.0, 5.0)
        
        self.assertGreaterEqual(delay, 2.0)
        self.assertLessEqual(delay, 5.0)
    
    def test_calculate_enhanced_delay_with_failures(self):
        """Test delay calculation with consecutive failures"""
        self.handler.consecutive_failures = 3
        
        delay = self.handler.calculate_enhanced_delay(2.0, 5.0)
        
        # Should be longer due to failures
        self.assertGreater(delay, 2.0)
    
    def test_calculate_enhanced_delay_with_bot_detection(self):
        """Test delay calculation after bot detection"""
        self.handler.bot_detection_count = 2
        self.handler.last_detection_time = time.time()
        
        delay = self.handler.calculate_enhanced_delay(2.0, 5.0)
        
        # Should be longer due to recent bot detection
        self.assertGreater(delay, 2.0)
    
    def test_record_failure(self):
        """Test failure recording"""
        initial_failures = self.handler.consecutive_failures
        
        self.handler.record_failure()
        
        self.assertEqual(self.handler.consecutive_failures, initial_failures + 1)
    
    def test_reset_failures(self):
        """Test failure reset"""
        self.handler.consecutive_failures = 5
        
        self.handler.reset_failures()
        
        self.assertEqual(self.handler.consecutive_failures, 0)
    
    def test_get_bot_detection_stats(self):
        """Test bot detection statistics retrieval"""
        self.handler.bot_detection_count = 3
        self.handler.consecutive_failures = 2
        
        stats = self.handler.get_bot_detection_stats()
        
        self.assertIn('bot_detection_count', stats)
        self.assertIn('consecutive_failures', stats)
        self.assertEqual(stats['bot_detection_count'], 3)
        self.assertEqual(stats['consecutive_failures'], 2)
    
    def test_reset_bot_detection_stats(self):
        """Test bot detection statistics reset"""
        self.handler.bot_detection_count = 5
        self.handler.consecutive_failures = 3
        
        self.handler.reset_bot_detection_stats()
        
        self.assertEqual(self.handler.bot_detection_count, 0)
        self.assertEqual(self.handler.consecutive_failures, 0)
        self.assertIsNone(self.handler.last_detection_time)


if __name__ == '__main__':
    unittest.main()

