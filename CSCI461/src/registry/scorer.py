"""
Orchestrates metric computation in parallel with latency measurement.
"""
from __future__ import annotations

import logging
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict

import requests
from git import GitCommandError, Repo
from huggingface_hub import model_info

from .metrics import (
    BusFactorMetric,
    CodeQualityMetric,
    DatasetAndCodeScoreMetric,
    DatasetQualityMetric,
    LicenseMetric,
    PerformanceClaimsMetric,
    RampUpTimeMetric,
    SizeScoreMetric,
)
from .models import MetricResult, ResourceScore

LOG = logging.getLogger(__name__)


def fetch_huggingface_metadata(model_id: str) -> Dict[str, Any]:
    """
    Fetch metadata from Hugging Face Hub for a given model ID.
    
    Args:
        model_id: The Hugging Face model identifier (e.g., "org/model")
        
    Returns:
        Dictionary containing model metadata
    """
    try:
        LOG.debug("Fetching HF model info for %s", model_id)
        info = model_info(model_id)
        return info.to_dict()
    except Exception as e:
        LOG.info("Hugging Face fetch failed for %s: %s", model_id, e)
        return {}


def analyze_git_repository(url: str, ctx: Dict[str, Any]) -> None:
    """
    Clone and analyze a Git repository to extract metadata.
    
    Args:
        url: The Git repository URL
        ctx: Context dictionary to populate with analysis results
    """
    try:
        tmpd = tempfile.mkdtemp(prefix="modelrepo_")
        LOG.debug("Cloning %s into %s", url, tmpd)
        Repo.clone_from(url, tmpd, depth=20)
        repo = Repo(tmpd)
        
        # Count unique contributors
        contributors = set()
        for commit in repo.iter_commits(max_count=200):
            try:
                contributors.add(commit.author.email)
            except Exception:
                continue
        ctx["git_contributors"] = len(contributors)
        
        # Analyze repository contents
        total_weights = 0
        has_tests = False
        has_ci = False
        
        for root, _, files in os.walk(tmpd):
            for f in files:
                # Detect model weight files
                if f.endswith(('.bin', '.pt', '.safetensors', '.h5', '.ckpt')):
                    try:
                        total_weights += os.path.getsize(os.path.join(root, f))
                    except Exception:
                        continue
                
                # Detect test files
                if f.startswith('test_') or f.endswith('_test.py'):
                    has_tests = True
                
                # Detect CI/CD configuration
                if f.endswith('.yml') and ('.github' in root or 'workflows' in root):
                    has_ci = True
        
        ctx["weights_total_bytes"] = total_weights
        ctx["has_tests"] = has_tests
        ctx["has_ci"] = has_ci
        
    except GitCommandError as e:
        LOG.info("Git clone failed for %s: %s", url, e)
    except Exception as e:
        LOG.debug("Repo analysis error for %s: %s", url, e)


def populate_context(url: str, name: str) -> Dict[str, Any]:
    """
    Build context dictionary with all necessary metadata for scoring.
    
    Args:
        url: The URL to analyze
        name: The name/identifier of the resource
        
    Returns:
        Context dictionary populated with metadata
    """
    ctx: Dict[str, Any] = {"url": url, "name": name}
    
    # Fetch Hugging Face metadata if applicable
    if "huggingface.co" in url:
        model_id = url.split('huggingface.co/', 1)[1].strip('/')
        hf_meta = fetch_huggingface_metadata(model_id)
        ctx["hf_meta"] = hf_meta
        
        # Extract README text
        try:
            ctx["hf_readme"] = (
                hf_meta.get("cardData", {}).get("README", "")
                or hf_meta.get("pipeline_tag", "")
            )
        except Exception:
            ctx["hf_readme"] = ""
        
        # Extract license information
        license_data = hf_meta.get("license", {})
        if isinstance(license_data, dict):
            ctx["license"] = license_data.get("id")
        else:
            ctx["license"] = license_data
    
    # Analyze Git repository if applicable
    if "github.com" in url:
        analyze_git_repository(url, ctx)
    
    return ctx


def compute_all_metrics(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute all metrics in parallel.
    
    Args:
        ctx: Context dictionary containing all necessary metadata
        
    Returns:
        Dictionary with metric values and latencies
    """
    # Initialize metric instances
    metrics = {
        "ramp_up_time": RampUpTimeMetric(),
        "bus_factor": BusFactorMetric(),
        "performance_claims": PerformanceClaimsMetric(),
        "license": LicenseMetric(),
        "size_score": SizeScoreMetric(),
        "dataset_and_code_score": DatasetAndCodeScoreMetric(),
        "dataset_quality": DatasetQualityMetric(),
        "code_quality": CodeQualityMetric(),
    }
    
    results: Dict[str, Any] = {}
    
    # Execute metrics in parallel
    max_workers = min(8, (os.cpu_count() or 1) * 2)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(metric.compute_with_timing, ctx): name
            for name, metric in metrics.items()
        }
        
        for fut in as_completed(futures):
            name = futures[fut]
            try:
                value, latency_ms = fut.result()
                results[name] = value
                results[f"{name}_latency"] = latency_ms
            except Exception as e:
                LOG.info("Metric %s failed: %s", name, e)
                results[name] = 0.0
                results[f"{name}_latency"] = 0
    
    return results


def compute_net_score(metrics: Dict[str, Any]) -> tuple[float, int]:
    """
    Compute the overall net score as a weighted combination of metrics.
    
    Args:
        metrics: Dictionary containing all computed metric values
        
    Returns:
        Tuple of (net_score, latency_ms)
    """
    import time
    
    t0 = time.perf_counter()
    
    # Weights for each metric
    weights = {
        "size_score": 0.15,
        "license": 0.15,
        "ramp_up_time": 0.15,
        "bus_factor": 0.10,
        "dataset_and_code_score": 0.10,
        "dataset_quality": 0.10,
        "code_quality": 0.10,
        "performance_claims": 0.15,
    }
    
    def get_metric_value(key: str) -> float:
        """Extract metric value, handling size_score dict specially."""
        if key == "size_score":
            value = metrics.get("size_score", {})
            if isinstance(value, dict):
                return float(value.get("desktop_pc", 1.0))
            return float(value)
        return float(metrics.get(key, 0.0))
    
    net_score = sum(weights[k] * get_metric_value(k) for k in weights)
    
    t1 = time.perf_counter()
    latency_ms = int(round((t1 - t0) * 1000))
    
    return net_score, latency_ms

