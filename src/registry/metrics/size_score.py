"""
Size score metric: evaluates model compatibility with different hardware platforms.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Tuple


class SizeScoreMetric:
    """
    Size score metric based on total model weights size.
    
    Evaluates compatibility with:
    - Raspberry Pi (< 50 MB)
    - Jetson Nano (< 700 MB)
    - Desktop PC (< 8 GB)
    - AWS Server (< 100 GB)
    """
    
    name: str = "size_score"
    
    def compute(self, repo_info: Dict[str, Any]) -> Tuple[Dict[str, float], int]:
        """
        Compute size score for each hardware target.
        
        Args:
            repo_info: Context containing 'weights_total_bytes' key
            
        Returns:
            Tuple of (score_dict, latency_ms) where score_dict maps hardware to scores
        """
        t0 = time.perf_counter()
        
        try:
            total = repo_info.get("weights_total_bytes", None)
            
            if total is None:
                # No size information available - assume works on larger hardware
                score_dict = {
                    "raspberry_pi": 0.0,
                    "jetson_nano": 0.0,
                    "desktop_pc": 1.0,
                    "aws_server": 1.0,
                }
            else:
                # Thresholds in bytes
                thresholds = {
                    "raspberry_pi": 50 * 1024 * 1024,      # 50 MB
                    "jetson_nano": 700 * 1024 * 1024,      # 700 MB
                    "desktop_pc": 8 * 1024 * 1024 * 1024,  # 8 GB
                    "aws_server": 100 * 1024 * 1024 * 1024,  # 100 GB
                }
                
                score_dict = {}
                for k, thresh in thresholds.items():
                    if total <= thresh:
                        score_dict[k] = 1.0
                    else:
                        # Gradual degradation up to 10x the threshold
                        val = 1.0 - (total - thresh) / (thresh * 10)
                        score_dict[k] = max(0.0, min(1.0, val))
            
        except Exception:
            # On error, return safe defaults
            score_dict = {
                "raspberry_pi": 0.0,
                "jetson_nano": 0.0,
                "desktop_pc": 1.0,
                "aws_server": 1.0,
            }
        
        t1 = time.perf_counter()
        latency_ms = int(round((t1 - t0) * 1000))
        
        return score_dict, latency_ms
