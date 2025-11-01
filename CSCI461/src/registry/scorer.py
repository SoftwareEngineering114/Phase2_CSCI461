"""
Orchestrates metric computation in parallel with latency measurement.
"""
from __future__ import annotations

import logging
import os
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

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
from .metrics.base import Metric
from .models import ModelScore, ResourceCategory

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


def compute_all_metrics(repo_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute all metrics in parallel using the Metric protocol.
    
    Args:
        repo_info: Context dictionary containing all necessary metadata
        
    Returns:
        Dictionary with metric values and latencies
    """
    # Initialize all metrics
    metrics: List[Metric] = [
        RampUpTimeMetric(),
        BusFactorMetric(),
        PerformanceClaimsMetric(),
        LicenseMetric(),
        SizeScoreMetric(),
        DatasetAndCodeScoreMetric(),
        DatasetQualityMetric(),
        CodeQualityMetric(),
    ]
    
    results: Dict[str, Any] = {}
    
    # Execute metrics in parallel
    max_workers = min(8, (os.cpu_count() or 1) * 2)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(metric.compute, repo_info): metric
            for metric in metrics
        }
        
        for fut in as_completed(futures):
            metric = futures[fut]
            try:
                value, latency_ms = fut.result()
                results[metric.name] = value
                results[f"{metric.name}_latency"] = latency_ms
            except Exception as e:
                LOG.error("Metric %s failed: %s", metric.name, e)
                # Metrics should not raise, but handle it gracefully
                results[metric.name] = 0.0
                results[f"{metric.name}_latency"] = 0
    
    return results


def compute_net_score(metrics: Dict[str, Any]) -> tuple[float, int]:
    """
    Compute the overall net score as a weighted combination of metrics.
    
    Args:
        metrics: Dictionary containing all computed metric values
        
    Returns:
        Tuple of (net_score, latency_ms)
    """
    t0 = time.perf_counter()
    
    try:
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
        
        # Clamp to [0, 1]
        net_score = max(0.0, min(1.0, net_score))
        
    except Exception as e:
        LOG.error("Net score computation failed: %s", e)
        net_score = 0.0
    
    t1 = time.perf_counter()
    latency_ms = int(round((t1 - t0) * 1000))
    
    return net_score, latency_ms


def score_model(url: str, name: str, category: ResourceCategory) -> ModelScore:
    """
    Score a model and return a ModelScore dataclass.
    
    Args:
        url: The model URL to process
        name: The model name/identifier
        category: The resource category (should be "MODEL")
        
    Returns:
        ModelScore object with all metrics computed
    """
    # Build context with metadata
    repo_info = populate_context(url, name)
    
    # Compute all metrics
    metrics = compute_all_metrics(repo_info)
    
    # Compute net score
    net_score_val, net_score_lat = compute_net_score(metrics)
    
    # Build ModelScore
    return ModelScore(
        name=name,
        category=category,
        ramp_up_time=metrics.get("ramp_up_time", 0.0),
        ramp_up_time_latency=metrics.get("ramp_up_time_latency", 0),
        bus_factor=metrics.get("bus_factor", 0.0),
        bus_factor_latency=metrics.get("bus_factor_latency", 0),
        performance_claims=metrics.get("performance_claims", 0.0),
        performance_claims_latency=metrics.get("performance_claims_latency", 0),
        license=metrics.get("license", 0.0),
        license_latency=metrics.get("license_latency", 0),
        size_score=metrics.get("size_score", {}),
        size_score_latency=metrics.get("size_score_latency", 0),
        dataset_and_code_score=metrics.get("dataset_and_code_score", 0.0),
        dataset_and_code_score_latency=metrics.get("dataset_and_code_score_latency", 0),
        dataset_quality=metrics.get("dataset_quality", 0.0),
        dataset_quality_latency=metrics.get("dataset_quality_latency", 0),
        code_quality=metrics.get("code_quality", 0.0),
        code_quality_latency=metrics.get("code_quality_latency", 0),
        net_score=net_score_val,
        net_score_latency=net_score_lat,
    )
