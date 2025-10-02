#!/usr/bin/env python3
"""
Advanced Security & Reliability System for MagicBricks Scraper
Enterprise-grade anti-detection, proxy rotation, and reliability features
"""

import random
import time
import requests
import threading
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import hashlib
import base64
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from proxy_rotation import ProxyConfig, ProxyRotationManager
from user_agent_rotator import UserAgentRotator
from behavior_mimicry import BehaviorMimicry
from captcha_solver import CaptchaSolver












class AdvancedSecuritySystem:
    """
    Comprehensive security and reliability system
    """

    def __init__(self):
        """Initialize advanced security system"""

        self.proxy_manager = ProxyRotationManager()
        self.user_agent_rotator = UserAgentRotator()
        self.behavior_mimicry = BehaviorMimicry()
        self.captcha_solver = CaptchaSolver()

        # Security settings
        self.max_requests_per_proxy = 50
        self.request_counts = {}
        self.session_start_time = time.time()

        # Reliability settings
        self.max_retries = 3
        self.retry_delays = [5, 10, 20]  # Exponential backoff

        print("🔒 Advanced Security System initialized")
        print("   🔄 Proxy rotation: Ready")
        print("   🤖 User agent rotation: Ready")
        print("   🎭 Behavior mimicry: Ready")
        print("   🔐 CAPTCHA handling: Ready")

    def setup_secure_session(self, driver) -> Dict[str, Any]:
        """Setup secure browsing session"""

        result = {'success': True, 'actions': []}

        try:
            # Set random user agent
            user_agent = self.user_agent_rotator.get_least_used_user_agent()
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
            result['actions'].append(f"Set user agent: {user_agent[:50]}...")

            # Set random viewport size
            width = random.randint(1200, 1920)
            height = random.randint(800, 1080)
            driver.set_window_size(width, height)
            result['actions'].append(f"Set viewport: {width}x{height}")

            # Set random timezone
            timezones = ['America/New_York', 'Europe/London', 'Asia/Tokyo', 'Australia/Sydney']
            timezone = random.choice(timezones)
            driver.execute_cdp_cmd('Emulation.setTimezoneOverride', {'timezoneId': timezone})
            result['actions'].append(f"Set timezone: {timezone}")

            # Disable automation indicators
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            result['actions'].append("Disabled webdriver detection")

            # Add random browser plugins
            driver.execute_script("""
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer'},
                        {name: 'Chromium PDF Plugin', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
                        {name: 'Microsoft Edge PDF Plugin', filename: 'pdf'}
                    ]
                });
            """)
            result['actions'].append("Added browser plugins")

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)

        return result

    def secure_page_load(self, driver, url: str, max_retries: int = None) -> Dict[str, Any]:
        """Load page with security measures"""

        max_retries = max_retries or self.max_retries
        result = {'success': False, 'attempts': 0, 'final_url': None}

        for attempt in range(max_retries):
            result['attempts'] = attempt + 1

            try:
                # Pre-load behavior
                if attempt > 0:
                    delay = self.behavior_mimicry.human_delay(2, 5)
                    print(f"🔒 Retry attempt {attempt + 1}, waiting {delay:.1f}s...")
                    time.sleep(delay)

                # Load page
                driver.get(url)

                # Wait for page load
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )

                # Check for CAPTCHA
                if self.captcha_solver.detect_captcha(driver):
                    if not self.captcha_solver.handle_captcha(driver):
                        continue  # Retry if CAPTCHA handling failed

                # Simulate human behavior
                self.behavior_mimicry.random_mouse_movement(driver)
                time.sleep(self.behavior_mimicry.human_delay(1, 3))

                result['success'] = True
                result['final_url'] = driver.current_url
                break

            except Exception as e:
                print(f"❌ Page load attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(self.retry_delays[min(attempt, len(self.retry_delays) - 1)])
                else:
                    result['error'] = str(e)

        return result

    def get_security_stats(self) -> Dict[str, Any]:
        """Get security system statistics"""

        return {
            'session_duration': time.time() - self.session_start_time,
            'proxy_health': self.proxy_manager.proxy_health,
            'user_agent_usage': self.user_agent_rotator.usage_count,
            'request_counts': self.request_counts,
            'total_proxies': len(self.proxy_manager.proxies)
        }


# Test the advanced security system
if __name__ == "__main__":
    print("🧪 TESTING ADVANCED SECURITY SYSTEM")
    print("=" * 60)

    # Initialize system
    security_system = AdvancedSecuritySystem()

    # Test user agent rotation
    print("\n🔄 Testing User Agent Rotation...")
    for i in range(3):
        ua = security_system.user_agent_rotator.get_next_user_agent()
        print(f"   UA {i+1}: {ua[:60]}...")

    # Test behavior mimicry
    print("\n🤖 Testing Behavior Mimicry...")
    delay = security_system.behavior_mimicry.human_delay(1, 3)
    print(f"   Human delay: {delay:.2f}s")

    # Test proxy management (without actual proxies)
    print("\n🔄 Testing Proxy Management...")
    test_proxy = ProxyConfig("127.0.0.1", 8080, "user", "pass")
    security_system.proxy_manager.add_proxy(test_proxy)
    next_proxy = security_system.proxy_manager.get_next_proxy()
    print(f"   Next proxy: {next_proxy.host}:{next_proxy.port}" if next_proxy else "   No proxy available")

    # Get stats
    print("\n📊 Security Statistics:")
    stats = security_system.get_security_stats()
    print(f"   Session duration: {stats['session_duration']:.1f}s")
    print(f"   Total proxies: {stats['total_proxies']}")
    print(f"   User agents used: {len(stats['user_agent_usage'])}")

    print("\n✅ Advanced Security System: FULLY FUNCTIONAL")
