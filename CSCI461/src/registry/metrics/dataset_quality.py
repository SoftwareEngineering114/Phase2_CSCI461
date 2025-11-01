"""
Dataset quality metric: evaluates quality based on download count and popularity.
"""
from __future__ import annotations

import math
from typing import Any, Dict

from .base import BaseMetric


class DatasetQualityMetric(BaseMetric):
    """
    Dataset quality metric based on download count.
    
    Uses logarithmic scaling:
    - 0 downloads: 0.2
    - Higher downloads: log scale up to 1.0
    """
    
    def compute(self, ctx: Dict[str, Any]) -> float:
        """
        Compute dataset quality score.
        
        Args:
            ctx: Context containing 'dataset_downloads' key
            
        Returns:
            Score from 0.2 to 1.0
        """
        downloads = ctx.get("dataset_downloads", 0)
        
        if downloads <= 0:
            return 0.2
        
        # Log scale normalization
        score = min(1.0, math.log1p(downloads) / 10.0)
        return score

