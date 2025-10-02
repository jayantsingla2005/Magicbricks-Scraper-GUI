#!/usr/bin/env python3
"""
Proxy rotation utilities for MagicBricks scraper
"""
from __future__ import annotations

import time
import threading
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

import requests


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
                # use time.time for last_check to avoid tz serialization issues
                self.proxy_health[proxy_id]['last_check'] = time.time()

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

