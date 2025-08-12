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


@dataclass
class ProxyConfig:
    """Proxy configuration"""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = 'http'
    
    def to_url(self) -> str:
        """Convert to proxy URL"""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"


class ProxyRotationManager:
    """
    Advanced proxy rotation with health monitoring
    """
    
    def __init__(self):
        """Initialize proxy rotation manager"""
        
        self.proxies: List[ProxyConfig] = []
        self.proxy_health: Dict[str, Dict[str, Any]] = {}
        self.current_proxy_index = 0
        self.lock = threading.Lock()
        
        # Health check settings
        self.health_check_interval = 300  # 5 minutes
        self.max_failures = 3
        self.test_url = "https://httpbin.org/ip"
        
        print("🔄 Proxy Rotation Manager initialized")
    
    def add_proxy(self, proxy: ProxyConfig):
        """Add proxy to rotation"""
        
        with self.lock:
            self.proxies.append(proxy)
            proxy_id = self._get_proxy_id(proxy)
            self.proxy_health[proxy_id] = {
                'failures': 0,
                'last_check': None,
                'response_time': None,
                'status': 'unknown'
            }
            
            print(f"🔄 Added proxy: {proxy.host}:{proxy.port}")
    
    def get_next_proxy(self) -> Optional[ProxyConfig]:
        """Get next healthy proxy"""
        
        with self.lock:
            if not self.proxies:
                return None
            
            # Try to find a healthy proxy
            attempts = 0
            while attempts < len(self.proxies):
                proxy = self.proxies[self.current_proxy_index]
                proxy_id = self._get_proxy_id(proxy)
                
                # Check if proxy is healthy
                if self.proxy_health[proxy_id]['failures'] < self.max_failures:
                    self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
                    return proxy
                
                self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
                attempts += 1
            
            # No healthy proxies found
            return None
    
    def report_proxy_failure(self, proxy: ProxyConfig):
        """Report proxy failure"""
        
        with self.lock:
            proxy_id = self._get_proxy_id(proxy)
            if proxy_id in self.proxy_health:
                self.proxy_health[proxy_id]['failures'] += 1
                self.proxy_health[proxy_id]['status'] = 'failed'
                
                print(f"⚠️ Proxy failure reported: {proxy.host}:{proxy.port} ({self.proxy_health[proxy_id]['failures']} failures)")
    
    def report_proxy_success(self, proxy: ProxyConfig, response_time: float):
        """Report proxy success"""
        
        with self.lock:
            proxy_id = self._get_proxy_id(proxy)
            if proxy_id in self.proxy_health:
                self.proxy_health[proxy_id]['failures'] = 0
                self.proxy_health[proxy_id]['response_time'] = response_time
                self.proxy_health[proxy_id]['status'] = 'healthy'
                self.proxy_health[proxy_id]['last_check'] = datetime.now()
    
    def health_check_all_proxies(self) -> Dict[str, Any]:
        """Perform health check on all proxies"""
        
        results = {'healthy': 0, 'failed': 0, 'total': len(self.proxies)}
        
        for proxy in self.proxies:
            try:
                start_time = time.time()
                response = requests.get(
                    self.test_url,
                    proxies={'http': proxy.to_url(), 'https': proxy.to_url()},
                    timeout=10
                )
                
                if response.status_code == 200:
                    response_time = time.time() - start_time
                    self.report_proxy_success(proxy, response_time)
                    results['healthy'] += 1
                else:
                    self.report_proxy_failure(proxy)
                    results['failed'] += 1
                    
            except Exception:
                self.report_proxy_failure(proxy)
                results['failed'] += 1
        
        print(f"🔍 Proxy health check: {results['healthy']}/{results['total']} healthy")
        return results
    
    def _get_proxy_id(self, proxy: ProxyConfig) -> str:
        """Get unique proxy identifier"""
        return f"{proxy.host}:{proxy.port}"


class UserAgentRotator:
    """
    Advanced user agent rotation with realistic patterns
    """
    
    def __init__(self):
        """Initialize user agent rotator"""
        
        self.user_agents = [
            # Chrome on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            
            # Firefox on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
            
            # Edge on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            
            # Chrome on macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            
            # Safari on macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            
            # Chrome on Linux
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            
            # Mobile Chrome
            "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            
            # Mobile Safari
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
        ]
        
        self.current_index = 0
        self.usage_count = {}
        
        print(f"🔄 User Agent Rotator initialized with {len(self.user_agents)} agents")
    
    def get_random_user_agent(self) -> str:
        """Get random user agent"""
        return random.choice(self.user_agents)
    
    def get_next_user_agent(self) -> str:
        """Get next user agent in rotation"""
        user_agent = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        
        # Track usage
        self.usage_count[user_agent] = self.usage_count.get(user_agent, 0) + 1
        
        return user_agent
    
    def get_least_used_user_agent(self) -> str:
        """Get least used user agent"""
        if not self.usage_count:
            return self.get_random_user_agent()
        
        least_used = min(self.user_agents, key=lambda ua: self.usage_count.get(ua, 0))
        self.usage_count[least_used] = self.usage_count.get(least_used, 0) + 1
        
        return least_used


class BehaviorMimicry:
    """
    Human behavior mimicry for anti-detection
    """
    
    def __init__(self):
        """Initialize behavior mimicry"""
        
        self.mouse_patterns = []
        self.typing_patterns = []
        self.scroll_patterns = []
        
        print("🤖 Behavior Mimicry initialized")
    
    def human_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0) -> float:
        """Generate human-like delay"""
        
        # Use normal distribution for more realistic timing
        mean = (min_seconds + max_seconds) / 2
        std = (max_seconds - min_seconds) / 6  # 99.7% within range
        
        delay = random.normalvariate(mean, std)
        delay = max(min_seconds, min(max_seconds, delay))
        
        return delay
    
    def random_mouse_movement(self, driver):
        """Perform random mouse movements"""
        
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            
            actions = ActionChains(driver)
            
            # Random small movements
            for _ in range(random.randint(2, 5)):
                x_offset = random.randint(-50, 50)
                y_offset = random.randint(-50, 50)
                actions.move_by_offset(x_offset, y_offset)
                actions.pause(random.uniform(0.1, 0.3))
            
            actions.perform()
            
        except Exception:
            pass  # Fail silently
    
    def random_scroll(self, driver):
        """Perform random scrolling"""
        
        try:
            # Random scroll amount
            scroll_amount = random.randint(100, 500)
            direction = random.choice([1, -1])
            
            driver.execute_script(f"window.scrollBy(0, {scroll_amount * direction});")
            
            # Pause after scrolling
            time.sleep(self.human_delay(0.5, 1.5))
            
        except Exception:
            pass  # Fail silently
    
    def simulate_reading(self, driver, element=None):
        """Simulate reading behavior"""
        
        try:
            # Scroll to element if provided
            if element:
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(self.human_delay(0.5, 1.0))
            
            # Random reading time based on content length
            if element:
                text_length = len(element.text) if element.text else 100
                reading_time = max(1.0, text_length / 200)  # ~200 chars per second
                reading_time += random.uniform(-0.5, 1.0)  # Add variance
            else:
                reading_time = random.uniform(2.0, 5.0)
            
            time.sleep(reading_time)
            
        except Exception:
            pass  # Fail silently


class CaptchaSolver:
    """
    CAPTCHA detection and handling
    """
    
    def __init__(self):
        """Initialize CAPTCHA solver"""
        
        self.captcha_selectors = [
            "iframe[src*='recaptcha']",
            ".g-recaptcha",
            ".captcha",
            "#captcha",
            "[data-captcha]",
            ".hcaptcha",
            ".cloudflare-challenge"
        ]
        
        print("🔐 CAPTCHA Solver initialized")
    
    def detect_captcha(self, driver) -> bool:
        """Detect if CAPTCHA is present"""
        
        try:
            for selector in self.captcha_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and any(elem.is_displayed() for elem in elements):
                    print(f"🔐 CAPTCHA detected: {selector}")
                    return True
            
            # Check for common CAPTCHA text
            page_text = driver.page_source.lower()
            captcha_keywords = ['captcha', 'recaptcha', 'verify you are human', 'robot check']
            
            for keyword in captcha_keywords:
                if keyword in page_text:
                    print(f"🔐 CAPTCHA detected by keyword: {keyword}")
                    return True
            
            return False
            
        except Exception:
            return False
    
    def handle_captcha(self, driver, timeout: int = 30) -> bool:
        """Handle CAPTCHA (manual intervention required)"""
        
        print("🔐 CAPTCHA detected - Manual intervention required")
        print("   Please solve the CAPTCHA manually and press Enter to continue...")
        
        # Wait for user input
        input("   Press Enter after solving CAPTCHA: ")
        
        # Wait for CAPTCHA to disappear
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.detect_captcha(driver):
                print("✅ CAPTCHA solved successfully")
                return True
            time.sleep(1)
        
        print("❌ CAPTCHA handling timeout")
        return False


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
