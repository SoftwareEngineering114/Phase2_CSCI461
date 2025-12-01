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
        Compute dataset quality score.
        
        Args:
            repo_info: Context containing 'dataset_downloads' key
            
        Returns:
            Tuple of (score, latency_ms) where score is 0.2 to 1.0
        """
        t0 = time.perf_counter()
        
        try:
            downloads = repo_info.get("dataset_downloads", 0)
            
            if downloads <= 0:
                score = 0.2
            else:
                # Log scale normalization
                score = min(1.0, math.log1p(downloads) / 10.0)
            
            # Clamp to [0, 1]
            score = max(0.0, min(1.0, score))
            
        except Exception:
            score = 0.2  # Default when data is missing
        
        t1 = time.perf_counter()
        latency_ms = int(round((t1 - t0) * 1000))
        
        return score, latency_ms
