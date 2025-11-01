"""
Bus factor metric: measures project resilience based on contributor diversity.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Tuple


class BusFactorMetric:
    """
    Bus factor metric based on number of contributors.
    
    Evaluates project resilience:
    - 1 contributor: 0.1
    - 5+ contributors: 1.0
    - Linear scaling between
    """
    
    name: str = "bus_factor"
    
    def compute(self, repo_info: Dict[str, Any]) -> Tuple[float, int]:
        """
        Compute bus factor score.
        
        Args:
            repo_info: Context containing 'git_contributors' key
            
        Returns:
            Tuple of (score, latency_ms) where score is 0.1 to 1.0
        """
        t0 = time.perf_counter()
        
        try:
            contributors = repo_info.get("git_contributors", 1)
            
            if contributors <= 1:
                score = 0.1
            else:
                score = min(1.0, contributors / 5.0)
            
            # Clamp to [0, 1]
            score = max(0.0, min(1.0, score))
            
        except Exception:
            score = 0.0
        
        t1 = time.perf_counter()
        latency_ms = int(round((t1 - t0) * 1000))
        
        return score, latency_ms
