"""
Base metric Protocol for all metrics.
"""
from __future__ import annotations

from typing import Any, Dict, Protocol, Tuple, Union, runtime_checkable


@runtime_checkable
class Metric(Protocol):
    """
    Protocol for metric computation.
    
    All metrics must implement:
    - name: str attribute matching NDJSON field name
    - compute(repo_info) method returning (score, latency_ms)
    
    Requirements:
    - Score MUST be clamped to [0.0, 1.0] (or dict[str, float] for size_score)
    - Latency MUST be int milliseconds, rounded
    - MUST NOT raise on missing data; degrade gracefully (return 0.0)
    - Must handle network failures and return valid score + latency
    """
    
    name: str  # e.g. "ramp_up_time", "bus_factor", etc.
    
    def compute(self, repo_info: Dict[str, Any]) -> Tuple[Union[float, Dict[str, float]], int]:
        """
        Compute the metric score and latency.
        
        Args:
            repo_info: Dictionary containing all metadata about the repository/model
            
        Returns:
            Tuple of (score, latency_ms) where:
            - score is float between 0.0 and 1.0 (or dict for size_score)
            - latency_ms is int milliseconds (rounded)
            
        Note:
            MUST NOT raise exceptions. On error, return (0.0, latency) where
            latency is still measured. Must degrade gracefully on missing data.
        """
        ...
