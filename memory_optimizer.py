"""
Memory Optimizer module extracted from performance_optimization_system.py
"""
from __future__ import annotations
import psutil
import gc
import weakref
from typing import Dict, Any


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
            'increase_percent': ((current - self.initial_memory) / self.initial_memory) * 100,
        }

    def optimize_memory(self) -> Dict[str, Any]:
        """Perform memory optimization"""
        before = self.get_memory_usage()
        # Force garbage collection
        collected = gc.collect()
        # Clear weak references
        try:
            weakref.finalize._registry.clear()  # type: ignore[attr-defined]
        except Exception:
            pass
        after = self.get_memory_usage()
        freed = before - after
        result = {
            'before_mb': before,
            'after_mb': after,
            'freed_mb': freed,
            'objects_collected': collected,
            'success': freed > 0,
        }
        print(f"🧹 Memory optimization: {freed:.1f}MB freed, {collected} objects collected")
        return result

    def should_optimize(self) -> bool:
        """Check if memory optimization is needed"""
        current = self.get_memory_usage()
        return (current - self.initial_memory) > (self.gc_threshold / (1024 * 1024))

