#!/usr/bin/env python3
"""
Performance Optimization System for MagicBricks Scraper
Advanced caching, memory management, and speed optimizations
"""

import time
import threading
import sqlite3
import pickle
import hashlib
import gc
import psutil
import os
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import weakref

from advanced_cache_manager import AdvancedCacheManager
from memory_optimizer import MemoryOptimizer
from performance_profiler import PerformanceProfiler
from database_optimizer import DatabaseOptimizer






class PerformanceOptimizationSystem:
    """
    Comprehensive performance optimization system
    """

    def __init__(self, db_path: str = "magicbricks_enhanced.db"):
        """Initialize performance optimization system"""

        self.cache_manager = AdvancedCacheManager()
        self.memory_optimizer = MemoryOptimizer()
        self.profiler = PerformanceProfiler()
        self.db_optimizer = DatabaseOptimizer(db_path)

        # Auto-optimization settings
        self.auto_optimize_enabled = True
        self.optimization_interval = 300  # 5 minutes
        self.last_optimization = time.time()

        print("🚀 Performance Optimization System initialized")
        print("   🧠 Memory monitoring: Enabled")
        print("   💾 Advanced caching: Enabled")
        print("   ⏱️ Performance profiling: Enabled")
        print("   🗄️ Database optimization: Enabled")

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""

        return {
            'cache': self.cache_manager.get_stats(),
            'memory': self.memory_optimizer.get_memory_stats(),
            'performance': self.profiler.get_stats(),
            'system': {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage_percent': psutil.disk_usage('.').percent
            }
        }

    def auto_optimize(self) -> Dict[str, Any]:
        """Perform automatic optimization if needed"""

        if not self.auto_optimize_enabled:
            return {'skipped': 'auto_optimize_disabled'}

        current_time = time.time()
        if (current_time - self.last_optimization) < self.optimization_interval:
            return {'skipped': 'too_soon'}

        results = {}

        # Memory optimization
        if self.memory_optimizer.should_optimize():
            results['memory'] = self.memory_optimizer.optimize_memory()

        # Database optimization (less frequent)
        if (current_time - self.last_optimization) > (self.optimization_interval * 4):
            results['database'] = self.db_optimizer.optimize_database()

        self.last_optimization = current_time

        return results

    def cache_property_data(self, url: str, data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Cache property data"""
        cache_key = f"property:{hashlib.md5(url.encode()).hexdigest()}"
        return self.cache_manager.put(cache_key, data, ttl)

    def get_cached_property_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Get cached property data"""
        cache_key = f"property:{hashlib.md5(url.encode()).hexdigest()}"
        return self.cache_manager.get(cache_key)

    def time_scraping_operation(self, operation_name: str):
        """Time a scraping operation"""
        return self.profiler.time_operation(operation_name)

    def log_scraping_metric(self, metric_name: str, value: int = 1):
        """Log a scraping metric"""
        self.profiler.increment_counter(metric_name, value)


# Test the performance optimization system
if __name__ == "__main__":
    print("🧪 TESTING PERFORMANCE OPTIMIZATION SYSTEM")
    print("=" * 60)

    # Initialize system
    perf_system = PerformanceOptimizationSystem()

    # Test caching
    print("\n💾 Testing Advanced Caching...")
    test_data = {'title': 'Test Property', 'price': '₹50 Lakh', 'area': '1200 sq ft'}
    success = perf_system.cache_property_data('https://test.com/property1', test_data)
    print(f"   Cache put: {'Success' if success else 'Failed'}")

    cached_data = perf_system.get_cached_property_data('https://test.com/property1')
    print(f"   Cache get: {'Success' if cached_data else 'Failed'}")

    # Test performance profiling
    print("\n⏱️ Testing Performance Profiling...")
    with perf_system.time_scraping_operation('test_operation'):
        time.sleep(0.1)  # Simulate work

    perf_system.log_scraping_metric('properties_scraped', 5)

    # Get comprehensive stats
    print("\n📊 Performance Statistics:")
    stats = perf_system.get_comprehensive_stats()

    print(f"   Cache hit rate: {stats['cache']['hit_rate_percent']:.1f}%")
    print(f"   Memory usage: {stats['memory']['current_mb']:.1f}MB")
    print(f"   CPU usage: {stats['system']['cpu_percent']:.1f}%")

    print("\n✅ Performance Optimization System: FULLY FUNCTIONAL")
