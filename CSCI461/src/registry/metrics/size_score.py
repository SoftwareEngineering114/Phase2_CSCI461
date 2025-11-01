"""
Size score metric: evaluates model compatibility with different hardware platforms.
"""
from __future__ import annotations

from typing import Any, Dict

from .base import BaseMetric


class SizeScoreMetric(BaseMetric):
    """
    Size score metric based on total model weights size.
    
    Evaluates compatibility with:
    - Raspberry Pi (< 50 MB)
    - Jetson Nano (< 700 MB)
    - Desktop PC (< 8 GB)
    - AWS Server (< 100 GB)
    """
    
    def compute(self, ctx: Dict[str, Any]) -> Dict[str, float]:
        """
        Compute size score for each hardware target.
        
        Args:
            ctx: Context containing 'weights_total_bytes' key
            
        Returns:
            Dictionary mapping hardware targets to compatibility scores (0.0-1.0)
        """
        total = ctx.get("weights_total_bytes", None)
        
        if total is None:
            # No size information available - assume works on larger hardware
            return {
                "raspberry_pi": 0.0,
                "jetson_nano": 0.0,
                "desktop_pc": 1.0,
                "aws_server": 1.0,
            }
        
        # Thresholds in bytes
        thresholds = {
            "raspberry_pi": 50 * 1024 * 1024,      # 50 MB
            "jetson_nano": 700 * 1024 * 1024,      # 700 MB
            "desktop_pc": 8 * 1024 * 1024 * 1024,  # 8 GB
            "aws_server": 100 * 1024 * 1024 * 1024,  # 100 GB
        }
        
        out = {}
        for k, thresh in thresholds.items():
            if total <= thresh:
                out[k] = 1.0
            else:
                # Gradual degradation up to 10x the threshold
                out[k] = min(1.0, max(0.0, 1.0 - (total - thresh) / (thresh * 10)))
        
        return out

