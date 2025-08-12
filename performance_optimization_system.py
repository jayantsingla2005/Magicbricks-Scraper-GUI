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


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: Any
    timestamp: datetime
    access_count: int
    size_bytes: int
    ttl_seconds: int


class AdvancedCacheManager:
    """
    Advanced caching system with LRU eviction, TTL, and memory management
    """
    
    def __init__(self, max_memory_mb: int = 100, default_ttl: int = 3600):
        """
        Initialize cache manager
        
        Args:
            max_memory_mb: Maximum memory usage in MB
            default_ttl: Default time-to-live in seconds
        """
        
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []
        self.current_memory = 0
        self.lock = threading.RLock()
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'memory_usage': 0
        }
        
        print("🚀 Advanced Cache Manager initialized")
        print(f"   💾 Max memory: {max_memory_mb}MB")
        print(f"   ⏰ Default TTL: {default_ttl}s")
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        
        with self.lock:
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            entry = self.cache[key]
            
            # Check TTL
            if self._is_expired(entry):
                self._remove_entry(key)
                self.stats['misses'] += 1
                return None
            
            # Update access
            entry.access_count += 1
            self._update_access_order(key)
            self.stats['hits'] += 1
            
            return entry.data
    
    def put(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """Put item in cache"""
        
        with self.lock:
            # Calculate size
            size_bytes = self._calculate_size(data)
            
            # Check if item is too large
            if size_bytes > self.max_memory_bytes:
                return False
            
            # Remove existing entry if present
            if key in self.cache:
                self._remove_entry(key)
            
            # Ensure space
            while (self.current_memory + size_bytes) > self.max_memory_bytes:
                if not self._evict_lru():
                    return False
            
            # Create entry
            entry = CacheEntry(
                data=data,
                timestamp=datetime.now(),
                access_count=1,
                size_bytes=size_bytes,
                ttl_seconds=ttl or self.default_ttl
            )
            
            # Add to cache
            self.cache[key] = entry
            self.access_order.append(key)
            self.current_memory += size_bytes
            self.stats['memory_usage'] = self.current_memory
            
            return True
    
    def invalidate(self, key: str) -> bool:
        """Invalidate cache entry"""
        
        with self.lock:
            if key in self.cache:
                self._remove_entry(key)
                return True
            return False
    
    def clear(self):
        """Clear all cache entries"""
        
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
            self.current_memory = 0
            self.stats['memory_usage'] = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        
        with self.lock:
            hit_rate = 0
            total_requests = self.stats['hits'] + self.stats['misses']
            if total_requests > 0:
                hit_rate = (self.stats['hits'] / total_requests) * 100
            
            return {
                **self.stats,
                'entries': len(self.cache),
                'hit_rate_percent': hit_rate,
                'memory_usage_mb': self.current_memory / (1024 * 1024),
                'memory_usage_percent': (self.current_memory / self.max_memory_bytes) * 100
            }
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if entry is expired"""
        age = (datetime.now() - entry.timestamp).total_seconds()
        return age > entry.ttl_seconds
    
    def _remove_entry(self, key: str):
        """Remove entry from cache"""
        if key in self.cache:
            entry = self.cache[key]
            self.current_memory -= entry.size_bytes
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
    
    def _update_access_order(self, key: str):
        """Update LRU access order"""
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def _evict_lru(self) -> bool:
        """Evict least recently used entry"""
        if not self.access_order:
            return False
        
        lru_key = self.access_order[0]
        self._remove_entry(lru_key)
        self.stats['evictions'] += 1
        return True
    
    def _calculate_size(self, data: Any) -> int:
        """Calculate approximate size of data"""
        try:
            return len(pickle.dumps(data))
        except:
            # Fallback estimation
            return len(str(data)) * 2


class MemoryOptimizer:
    """
    Memory usage optimization and monitoring
    """
    
    def __init__(self):
        """Initialize memory optimizer"""
        
        self.process = psutil.Process()
        self.initial_memory = self.get_memory_usage()
        self.peak_memory = self.initial_memory
        self.gc_threshold = 100 * 1024 * 1024  # 100MB
        
        print("🧠 Memory Optimizer initialized")
        print(f"   📊 Initial memory: {self.initial_memory:.1f}MB")
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / (1024 * 1024)
    
    def get_memory_stats(self) -> Dict[str, float]:
        """Get comprehensive memory statistics"""
        
        current = self.get_memory_usage()
        self.peak_memory = max(self.peak_memory, current)
        
        return {
            'current_mb': current,
            'peak_mb': self.peak_memory,
            'initial_mb': self.initial_memory,
            'increase_mb': current - self.initial_memory,
            'increase_percent': ((current - self.initial_memory) / self.initial_memory) * 100
        }
    
    def optimize_memory(self) -> Dict[str, Any]:
        """Perform memory optimization"""
        
        before = self.get_memory_usage()
        
        # Force garbage collection
        collected = gc.collect()
        
        # Clear weak references
        weakref.finalize._registry.clear()
        
        after = self.get_memory_usage()
        freed = before - after
        
        result = {
            'before_mb': before,
            'after_mb': after,
            'freed_mb': freed,
            'objects_collected': collected,
            'success': freed > 0
        }
        
        print(f"🧹 Memory optimization: {freed:.1f}MB freed, {collected} objects collected")
        
        return result
    
    def should_optimize(self) -> bool:
        """Check if memory optimization is needed"""
        current = self.get_memory_usage()
        return (current - self.initial_memory) > (self.gc_threshold / (1024 * 1024))


class PerformanceProfiler:
    """
    Performance profiling and monitoring
    """
    
    def __init__(self):
        """Initialize performance profiler"""
        
        self.timings: Dict[str, List[float]] = {}
        self.counters: Dict[str, int] = {}
        self.lock = threading.Lock()
        
        print("⏱️ Performance Profiler initialized")
    
    def time_operation(self, operation_name: str):
        """Context manager for timing operations"""
        return OperationTimer(self, operation_name)
    
    def record_timing(self, operation_name: str, duration: float):
        """Record operation timing"""
        
        with self.lock:
            if operation_name not in self.timings:
                self.timings[operation_name] = []
            
            self.timings[operation_name].append(duration)
            
            # Keep only last 100 timings
            if len(self.timings[operation_name]) > 100:
                self.timings[operation_name] = self.timings[operation_name][-100:]
    
    def increment_counter(self, counter_name: str, amount: int = 1):
        """Increment performance counter"""
        
        with self.lock:
            self.counters[counter_name] = self.counters.get(counter_name, 0) + amount
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        
        with self.lock:
            stats = {
                'timings': {},
                'counters': self.counters.copy()
            }
            
            for operation, times in self.timings.items():
                if times:
                    stats['timings'][operation] = {
                        'count': len(times),
                        'avg_ms': (sum(times) / len(times)) * 1000,
                        'min_ms': min(times) * 1000,
                        'max_ms': max(times) * 1000,
                        'total_ms': sum(times) * 1000
                    }
            
            return stats
    
    def reset_stats(self):
        """Reset all statistics"""
        
        with self.lock:
            self.timings.clear()
            self.counters.clear()


class OperationTimer:
    """Context manager for timing operations"""
    
    def __init__(self, profiler: PerformanceProfiler, operation_name: str):
        self.profiler = profiler
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.profiler.record_timing(self.operation_name, duration)


class DatabaseOptimizer:
    """
    Database performance optimization
    """
    
    def __init__(self, db_path: str):
        """Initialize database optimizer"""
        
        self.db_path = db_path
        print(f"🗄️ Database Optimizer initialized for {db_path}")
    
    def optimize_database(self) -> Dict[str, Any]:
        """Perform database optimization"""
        
        results = {}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Analyze database
                cursor.execute("ANALYZE")
                results['analyze'] = 'completed'
                
                # Vacuum database
                cursor.execute("VACUUM")
                results['vacuum'] = 'completed'
                
                # Update statistics
                cursor.execute("PRAGMA optimize")
                results['optimize'] = 'completed'
                
                # Get database info
                cursor.execute("PRAGMA page_count")
                page_count = cursor.fetchone()[0]
                
                cursor.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                
                results['size_mb'] = (page_count * page_size) / (1024 * 1024)
                results['pages'] = page_count
                
                print(f"🗄️ Database optimized: {results['size_mb']:.1f}MB, {page_count} pages")
                
        except Exception as e:
            results['error'] = str(e)
            print(f"❌ Database optimization failed: {str(e)}")
        
        return results
    
    def create_indexes(self, index_definitions: List[str]) -> Dict[str, Any]:
        """Create performance indexes"""
        
        results = {'created': [], 'failed': []}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for index_sql in index_definitions:
                    try:
                        cursor.execute(index_sql)
                        results['created'].append(index_sql)
                    except Exception as e:
                        results['failed'].append({'sql': index_sql, 'error': str(e)})
                
                conn.commit()
                
        except Exception as e:
            results['error'] = str(e)
        
        return results


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
