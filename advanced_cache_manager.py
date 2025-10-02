"""
Advanced Cache Manager module extracted from performance_optimization_system.py
"""
from __future__ import annotations
import threading
import pickle
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


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
                ttl_seconds=ttl or self.default_ttl,
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
            hit_rate = 0.0
            total_requests = self.stats['hits'] + self.stats['misses']
            if total_requests > 0:
                hit_rate = (self.stats['hits'] / total_requests) * 100

            return {
                **self.stats,
                'entries': len(self.cache),
                'hit_rate_percent': hit_rate,
                'memory_usage_mb': self.current_memory / (1024 * 1024),
                'memory_usage_percent': (self.current_memory / self.max_memory_bytes) * 100,
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
        except Exception:
            # Fallback estimation
            return len(str(data)) * 2

