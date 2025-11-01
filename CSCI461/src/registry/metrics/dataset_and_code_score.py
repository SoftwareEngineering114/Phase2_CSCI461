"""
Dataset and code score: evaluates availability of training data and example code.
"""
from __future__ import annotations

from typing import Any, Dict

from .base import BaseMetric


class DatasetAndCodeScoreMetric(BaseMetric):
    """
    Dataset and code availability metric.
    
    Scoring:
    - Both dataset and example code: 1.0
    - Either dataset or code: 0.5
    - Neither: 0.0
    """
    
    def compute(self, ctx: Dict[str, Any]) -> float:
        """
        Compute dataset and code score.
        
        Args:
            ctx: Context containing 'dataset_link' and 'example_code_present' keys
            
        Returns:
            Score from 0.0 to 1.0
        """
        has_dataset = bool(ctx.get("dataset_link"))
        has_example_code = bool(ctx.get("example_code_present"))
        
        if has_dataset and has_example_code:
            return 1.0
        elif has_dataset or has_example_code:
            return 0.5
        else:
            return 0.0

