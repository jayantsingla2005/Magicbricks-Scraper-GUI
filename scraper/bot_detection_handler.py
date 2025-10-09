#!/usr/bin/env python3
"""
Bot Detection Handler Module
Handles bot detection, recovery strategies, and anti-scraping measures.
Extracted from integrated_magicbricks_scraper.py for better maintainability.
"""

import time
import random
import logging
from typing import List


class BotDetectionHandler:
    """
    Handles bot detection and implements recovery strategies
    """
    
    def __init__(self, logger=None):
        """
        Initialize bot detection handler
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Bot detection tracking
        self.bot_detection_count = 0
        self.last_detection_time = None
        self.consecutive_failures = 0
        self.current_user_agent_index = 0
    
    def detect_bot_detection(self, page_source: str, current_url: str) -> bool:
        """
        Detect if we've been flagged as a bot
        
        Args:
            page_source: HTML source of the page
            current_url: Current URL being accessed
            
        Returns:
            True if bot detection is detected, False otherwise
        """
        # Check for explicit bot detection indicators
        bot_indicators = [
            'captcha', 'robot', 'bot detection', 'access denied',
            'cloudflare', 'please verify', 'security check',
            'unusual traffic', 'automated requests'
        ]

        page_lower = page_source.lower()
        url_lower = current_url.lower()

        # Check explicit bot indicators
        for indicator in bot_indicators:
            if indicator in page_lower or indicator in url_lower:
                return True

        # SPECIFIC CHECK: "About Magicbricks" redirect (not just footer links)
        # Bot detection redirects property URLs to About page with specific title/URL pattern
        if 'about-magicbricks' in url_lower or '/about' in url_lower:
            # URL was redirected to About page - this is bot detection
            return True

        # Check if page title is "About Magicbricks" (not just footer link)
        if '<title>' in page_lower and 'about magicbricks</title>' in page_lower:
            # Page title is "About Magicbricks" - this is bot detection redirect
            return True

        return False
    
    def handle_bot_detection(self, restart_browser_callback):
        """
        Handle bot detection with recovery strategies
        
        Args:
            restart_browser_callback: Callback function to restart browser session
        """
        self.bot_detection_count += 1
        self.last_detection_time = time.time()
        
        self.logger.warning(f"🚨 Bot detection #{self.bot_detection_count} - Implementing recovery strategy")
        
        if self.bot_detection_count <= 2:
            # Strategy 1: Extended delay and user agent rotation
            delay = min(45 + (self.bot_detection_count * 15), 90)  # 45s to 90s
            self.logger.info(f"   🔄 Strategy 1: Extended delay ({delay}s) + User agent rotation")
            
            # Rotate user agent
            self.current_user_agent_index = (self.current_user_agent_index + 1) % len(self.get_enhanced_user_agents())
            
            time.sleep(delay)
            
            # Restart browser session
            restart_browser_callback()
            
        elif self.bot_detection_count <= 4:
            # Strategy 2: Longer delay and session reset
            delay = 120 + (self.bot_detection_count * 30)  # 2-4 minutes
            self.logger.info(f"   🔄 Strategy 2: Long delay ({delay}s) + Complete session reset")
            
            time.sleep(delay)
            restart_browser_callback()
            
        else:
            # Strategy 3: Very long break - likely need to stop
            delay = 300  # 5 minutes
            self.logger.warning(f"   ⏸️ Strategy 3: Extended break ({delay}s) - Multiple detections")
            self.logger.warning(f"   ⚠️ Consider stopping scraper - persistent bot detection")
            time.sleep(delay)
            restart_browser_callback()
    
    def get_enhanced_user_agents(self) -> List[str]:
        """
        Get a large, diverse list of realistic user agents for rotation.
        """
        return [
            # Windows Chrome
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',

            # Windows Firefox
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',

            # Windows Edge
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',

            # macOS Chrome
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',

            # macOS Safari
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',

            # macOS Firefox
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:124.0) Gecko/20100101 Firefox/124.0',

            # Linux Chrome
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',

            # Linux Firefox
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0',
        ]
    
    def get_current_user_agent(self) -> str:
        """
        Get the current user agent based on rotation index
        
        Returns:
            Current user agent string
        """
        user_agents = self.get_enhanced_user_agents()
        return user_agents[self.current_user_agent_index % len(user_agents)]
    
    def calculate_enhanced_delay(self, page_number: int, base_min: float = 2.0, base_max: float = 5.0) -> float:
        """
        Calculate enhanced delay based on session health and page number
        
        Args:
            page_number: Current page number
            base_min: Minimum base delay in seconds
            base_max: Maximum base delay in seconds
            
        Returns:
            Calculated delay in seconds
        """
        base_delay = random.uniform(base_min, base_max)
        
        # Increase delays if we've had recent bot detection
        if self.last_detection_time and (time.time() - self.last_detection_time) < 300:  # 5 minutes
            base_delay *= 1.5
        
        # Increase delays for consecutive failures
        if self.consecutive_failures > 0:
            base_delay *= (1 + self.consecutive_failures * 0.3)
        
        # Longer delays for later pages in session
        if page_number > 10:
            base_delay *= 1.2
        if page_number > 20:
            base_delay *= 1.3
        
        return base_delay
    
    def record_failure(self):
        """Record a consecutive failure"""
        self.consecutive_failures += 1
    
    def reset_failures(self):
        """Reset consecutive failures counter"""
        self.consecutive_failures = 0
    
    def get_bot_detection_stats(self) -> dict:
        """
        Get bot detection statistics
        
        Returns:
            Dictionary with bot detection stats
        """
        return {
            'total_detections': self.bot_detection_count,
            'last_detection_time': self.last_detection_time,
            'consecutive_failures': self.consecutive_failures,
            'current_user_agent_index': self.current_user_agent_index
        }
    
    def reset_bot_detection_stats(self):
        """Reset all bot detection statistics"""
        self.bot_detection_count = 0
        self.last_detection_time = None
        self.consecutive_failures = 0
        self.current_user_agent_index = 0

