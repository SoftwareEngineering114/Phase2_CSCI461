"""
Dataset and code score: evaluates availability of training data and example code.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Tuple


class DatasetAndCodeScoreMetric:
    """
    Dataset and code availability metric.
    
    Scoring:
    - Both dataset and example code: 1.0
    - Either dataset or code: 0.5
    - Neither: 0.0
    """
    
    name: str = "dataset_and_code_score"
    
    def compute(self, repo_info: Dict[str, Any]) -> Tuple[float, int]:
        """
        Compute dataset and code score.
        
        Args:
            repo_info: Context containing 'dataset_link' and 'example_code_present' keys
            
        Returns:
            Tuple of (score, latency_ms) where score is 0.0, 0.5, or 1.0
        """
        t0 = time.perf_counter()
        
        try:
            has_dataset = bool(repo_info.get("dataset_link"))
            has_example_code = bool(repo_info.get("example_code_present"))
            
            if has_dataset and has_example_code:
                score = 1.0
            elif has_dataset or has_example_code:
                score = 0.5
            else:
                score = 0.0
            
        except Exception:
            score = 0.0
        
        t1 = time.perf_counter()
        latency_ms = int(round((t1 - t0) * 1000))
        
        return score, latency_ms
