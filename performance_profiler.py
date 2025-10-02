"""
Performance Profiler module extracted from performance_optimization_system.py
"""
from __future__ import annotations
import time
import threading
from typing import Dict, List, Any


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
            stats: Dict[str, Any] = {
                'timings': {},
                'counters': self.counters.copy(),
            }
            for operation, times in self.timings.items():
                if times:
                    stats['timings'][operation] = {
                        'count': len(times),
                        'avg_ms': (sum(times) / len(times)) * 1000,
                        'min_ms': min(times) * 1000,
                        'max_ms': max(times) * 1000,
                        'total_ms': sum(times) * 1000,
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

