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
            Tuple of (score, latency_ms).
            Conservative scoring:
            - 1.0: dataset + code both present AND referenced in README
            - 0.5: dataset OR code present AND referenced in README
            - 0.25: dataset OR code provided via context only (not referenced)
            - 0.0: neither present
        """
        t0 = time.perf_counter()
        
        try:
            dataset_link = str(repo_info.get("dataset_link") or "")
            code_link = str(repo_info.get("code_link") or "")
            has_dataset = bool(dataset_link)
            has_code = bool(code_link) or bool(repo_info.get("example_code_present"))

            readme = (repo_info.get("hf_readme", "") or "").lower()

            def mentioned(link: str) -> bool:
                if not link:
                    return False
                # Accept either the full URL or a reasonable slug being mentioned.
                slug = link.rstrip("/").split("/")[-1].lower()
                return (link.lower() in readme) or (slug and slug in readme)

            dataset_mentioned = has_dataset and mentioned(dataset_link)
            code_mentioned = has_code and mentioned(code_link)

            if dataset_mentioned and code_mentioned:
                score = 1.0
            elif dataset_mentioned or code_mentioned:
                score = 0.5
            elif has_dataset or has_code:
                score = 0.25
            else:
                score = 0.0
            
        except Exception:
            score = 0.0
        
        t1 = time.perf_counter()
        latency_ms = int(round((t1 - t0) * 1000))
        
        return score, latency_ms
