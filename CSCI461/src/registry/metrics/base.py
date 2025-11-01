"""
Base metric class for all metrics.
"""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple, TypeVar

T = TypeVar('T', float, Dict[str, float])


class BaseMetric(ABC):
    """
    Abstract base class for all metrics.
    
    Subclasses must implement the compute() method which calculates
    the metric value from a context dictionary.
    """
    
    @abstractmethod
    def compute(self, ctx: Dict[str, Any]) -> T:
        """
        Compute the metric value from the given context.
        
        Args:
            ctx: Dictionary containing all metadata and data needed for computation
            
        Returns:
            The computed metric value (float or dict for size_score)
        """
        pass
    
    def compute_with_timing(self, ctx: Dict[str, Any]) -> Tuple[T, int]:
        """
        Compute the metric and measure execution time.
        
        Args:
            ctx: Dictionary containing all metadata and data needed for computation
            
        Returns:
            Tuple of (metric_value, latency_ms)
        """
        t0 = time.perf_counter()
        value = self.compute(ctx)
        t1 = time.perf_counter()
        latency_ms = int(round((t1 - t0) * 1000))
        return value, latency_ms

