"""
Ramp-up time metric: measures documentation quality and ease of getting started.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Tuple


class RampUpTimeMetric:
    """
    Ramp-up time metric based on README quality.
    
    Evaluates:
    - Presence of examples or quickstart guides
    - Length and completeness of documentation
    """
    
    name: str = "ramp_up_time"
    
    def compute(self, repo_info: Dict[str, Any]) -> Tuple[float, int]:
        """
        Compute ramp-up time score.
        
        Args:
            repo_info: Context containing 'hf_readme' key
            
        Returns:
            Tuple of (score, latency_ms) where score is 0.0 to 1.0
        """
        t0 = time.perf_counter()
        
        try:
            readme = repo_info.get("hf_readme", "")
            
            # Check for examples or quickstart
            examples = 1.0 if ("example" in readme.lower() or "quickstart" in readme.lower()) else 0.0
            
            # Score based on documentation length (300 words = 1.0)
            length_score = min(1.0, len(readme.split()) / 300.0)
            
            score = 0.5 * length_score + 0.5 * examples
            
            # Clamp to [0, 1]
            score = max(0.0, min(1.0, score))
            
        except Exception:
            score = 0.0
        
        t1 = time.perf_counter()
        latency_ms = int(round((t1 - t0) * 1000))
        
        return score, latency_ms
