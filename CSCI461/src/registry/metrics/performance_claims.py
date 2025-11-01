"""
Performance claims metric: measures presence of benchmarks and evaluations.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Tuple


class PerformanceClaimsMetric:
    """
    Performance claims metric based on README content.
    
    Evaluates:
    - Presence of benchmarks
    - Accuracy metrics
    - Evaluation results
    """
    
    name: str = "performance_claims"
    
    def compute(self, repo_info: Dict[str, Any]) -> Tuple[float, int]:
        """
        Compute performance claims score.
        
        Args:
            repo_info: Context containing 'hf_readme' key
            
        Returns:
            Tuple of (score, latency_ms) where score is 0.0 or 1.0
        """
        t0 = time.perf_counter()
        
        try:
            readme = repo_info.get("hf_readme", "")
            readme_lower = readme.lower()
            
            has_claims = (
                "benchmark" in readme_lower
                or "accuracy" in readme_lower
                or "eval" in readme_lower
            )
            
            score = 1.0 if has_claims else 0.0
            
        except Exception:
            score = 0.0
        
        t1 = time.perf_counter()
        latency_ms = int(round((t1 - t0) * 1000))
        
        return score, latency_ms
