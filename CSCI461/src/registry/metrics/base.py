"""
Base metric Protocol for all metrics.
"""
from __future__ import annotations

from typing import Any, Dict, Protocol, Tuple, Union, runtime_checkable


@runtime_checkable
class Metric(Protocol):
    """
    Protocol for all metrics.
    
    Each metric must have:
    - name: str attribute matching the NDJSON key (e.g., "ramp_up_time")
    - compute() method that returns (score, latency_ms)
    
    Requirements:
    - Score MUST be clamped to [0, 1] (or dict[str, float] for size_score)
    - Latency MUST be an int number of milliseconds, rounded
    - MUST NOT raise on missing data; degrade gracefully (return 0, latency)
    """
    
    name: str
    
    def compute(self, repo_info: Dict[str, Any]) -> Tuple[Union[float, Dict[str, float]], int]:
        """
        Compute the metric score and latency.
        
        Args:
            repo_info: Dictionary containing all metadata and data for computation.
                      May have missing keys or network failures.
        
        Returns:
            Tuple of (score_between_0_and_1, latency_ms_int_rounded)
            - score: float in [0, 1] or dict[str, float] for size_score
            - latency_ms: int milliseconds, rounded
        
        MUST NOT raise exceptions. On error, return (0.0, latency).
        """
        ...

