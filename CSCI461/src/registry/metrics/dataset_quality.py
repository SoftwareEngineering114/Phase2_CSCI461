"""
Dataset quality metric: evaluates quality based on download count and popularity.
"""
from __future__ import annotations

import math
import time
from typing import Any, Dict, Tuple


class DatasetQualityMetric:
    """
    Dataset quality metric based on download count.
    
    Uses logarithmic scaling:
    - 0 downloads: 0.2
    - Higher downloads: log scale up to 1.0
    """
    
    name: str = "dataset_quality"
    
    def compute(self, repo_info: Dict[str, Any]) -> Tuple[float, int]:
        """
        Compute dataset quality score with timing.
        
        Args:
            repo_info: Context containing 'dataset_downloads' key
            
        Returns:
            Tuple of (score from 0.2 to 1.0, latency_ms)
        """
        t0 = time.perf_counter()
        
        try:
            downloads = repo_info.get("dataset_downloads", 0)
            
            if downloads <= 0:
                score = 0.2
            else:
                # Log scale normalization
                score = min(1.0, math.log1p(downloads) / 10.0)
            
            score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
            
        except Exception:
            score = 0.0
        
        t1 = time.perf_counter()
        latency_ms = int(round((t1 - t0) * 1000))
        
        return score, latency_ms

