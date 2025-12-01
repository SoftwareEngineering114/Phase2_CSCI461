"""
Orchestrates metric computation and scoring for models.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List

from .logging_setup import get_logger
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
from .url_parser import classify_url, fetch_repo_info, parse_url

LOG = get_logger(__name__)


def score_model(url: str, related_context: Dict[str, Any]) -> ModelScore:
    """
    Score a model URL and return complete ModelScore.
    
    Steps:
    1. Fetch repository metadata
    2. Compute all metrics in sequence (TODO: parallelize)
    3. Compute weighted net score
    4. Return ModelScore dataclass
    
    Args:
        url: The model URL to score
        related_context: Dictionary with related DATASET and CODE URLs for context
        
    Returns:
        ModelScore object with all metrics computed
        
    Note:
        Never raises - returns scores of 0.0 for any failures
    """
    LOG.info("Scoring MODEL: %s", url)
    t_start = time.perf_counter()
    
    # Parse URL to extract name
    parsed = parse_url(url)
    name = parsed.name
    category: ResourceCategory = "MODEL"
    
    LOG.debug("Parsed URL - name: %s, category: %s", name, category)
    
    # Fetch repository information
    LOG.debug("Fetching repository metadata for %s", url)
    repo_info = fetch_repo_info(url)
    
    # Merge related context (dataset/code URLs) into repo_info
    repo_info.update(related_context)
    LOG.debug("Context includes dataset_link=%s, code_link=%s", 
              related_context.get("dataset_link", "None"), 
              related_context.get("code_link", "None"))
    
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
    
    # Compute all metrics
    # TODO: Parallelize with ThreadPoolExecutor or asyncio for better performance
    metric_results: Dict[str, Any] = {}
    
    for metric in metrics:
        try:
            LOG.debug("Computing metric: %s", metric.name)
            value, latency_ms = metric.compute(repo_info)
            metric_results[metric.name] = value
            metric_results[f"{metric.name}_latency"] = latency_ms
            
            # Log metric result
            if isinstance(value, dict):
                LOG.debug("Metric %s = %s (latency: %d ms)", metric.name, value, latency_ms)
            else:
                LOG.debug("Metric %s = %.3f (latency: %d ms)", metric.name, value, latency_ms)
                
        except Exception as e:
            LOG.error("Metric %s failed for %s: %s", metric.name, url, e)
            # Metrics should not raise, but handle gracefully
            metric_results[metric.name] = 0.0 if metric.name != "size_score" else {}
            metric_results[f"{metric.name}_latency"] = 0
    
    # Compute net score with Phase 1 weights
    LOG.debug("Computing net score")
    net_score_val, net_score_lat = _compute_net_score(metric_results)
    LOG.info("Net score for %s: %.3f (latency: %d ms)", name, net_score_val, net_score_lat)
    
    t_end = time.perf_counter()
    total_time_ms = int((t_end - t_start) * 1000)
    LOG.info("Total scoring time for %s: %d ms", name, total_time_ms)
    
    # Build and return ModelScore
    return ModelScore(
        name=name,
        category=category,
        ramp_up_time=float(metric_results.get("ramp_up_time", 0.0)),
        ramp_up_time_latency=int(metric_results.get("ramp_up_time_latency", 0)),
        bus_factor=float(metric_results.get("bus_factor", 0.0)),
        bus_factor_latency=int(metric_results.get("bus_factor_latency", 0)),
        performance_claims=float(metric_results.get("performance_claims", 0.0)),
        performance_claims_latency=int(metric_results.get("performance_claims_latency", 0)),
        license=float(metric_results.get("license", 0.0)),
        license_latency=int(metric_results.get("license_latency", 0)),
        size_score=metric_results.get("size_score", {}),
        size_score_latency=int(metric_results.get("size_score_latency", 0)),
        dataset_and_code_score=float(metric_results.get("dataset_and_code_score", 0.0)),
        dataset_and_code_score_latency=int(metric_results.get("dataset_and_code_score_latency", 0)),
        dataset_quality=float(metric_results.get("dataset_quality", 0.0)),
        dataset_quality_latency=int(metric_results.get("dataset_quality_latency", 0)),
        code_quality=float(metric_results.get("code_quality", 0.0)),
        code_quality_latency=int(metric_results.get("code_quality_latency", 0)),
        net_score=net_score_val,
        net_score_latency=net_score_lat,
    )


def _compute_net_score(metric_results: Dict[str, Any]) -> tuple[float, int]:
    """
    Compute weighted net score from individual metrics.
    
    Weights (Phase 1):
    - 0.20 ramp_up_time
    - 0.20 license
    - 0.15 dataset_and_code_score
    - 0.10 size_score_avg (average of all device scores)
    - 0.10 bus_factor
    - 0.10 dataset_quality
    - 0.10 code_quality
    - 0.05 performance_claims
    
    Args:
        metric_results: Dictionary with all computed metric values
        
    Returns:
        Tuple of (net_score, latency_ms)
    """
    t0 = time.perf_counter()
    
    try:
        weights = {
            "ramp_up_time": 0.20,
            "license": 0.20,
            "dataset_and_code_score": 0.15,
            "size_score": 0.10,
            "bus_factor": 0.10,
            "dataset_quality": 0.10,
            "code_quality": 0.10,
            "performance_claims": 0.05,
        }
        
        def get_metric_value(key: str) -> float:
            """Extract metric value, handling size_score dict specially."""
            if key == "size_score":
                size_dict = metric_results.get("size_score", {})
                if isinstance(size_dict, dict) and size_dict:
                    # Average all device scores
                    avg = sum(size_dict.values()) / len(size_dict)
                    LOG.debug("size_score_avg = %.3f (from %s)", avg, size_dict)
                    return avg
                return 1.0  # Default if no size info
            return float(metric_results.get(key, 0.0))
        
        net_score = sum(weights[k] * get_metric_value(k) for k in weights)
        
        # Clamp to [0, 1]
        net_score = max(0.0, min(1.0, net_score))
        
        LOG.debug("Computed net_score = %.3f", net_score)
        
    except Exception as e:
        LOG.error("Net score computation failed: %s", e)
        net_score = 0.0
    
    t1 = time.perf_counter()
    latency_ms = int(round((t1 - t0) * 1000))
    
    return net_score, latency_ms


def process_url_list(urls: List[str]) -> List[ModelScore]:
    """
    Process a list of URLs and score all MODEL URLs.
    
    Maintains context of most recent DATASET and CODE URLs to provide
    related context when scoring models.
    
    Args:
        urls: List of URLs (can be MODEL, DATASET, or CODE)
        
    Returns:
        List of ModelScore objects (only for MODEL URLs)
        
    Note:
        Processes URLs sequentially. TODO: Add parallel processing with
        ThreadPoolExecutor or asyncio for better throughput.
    """
    LOG.info("Processing %d URLs", len(urls))
    results: List[ModelScore] = []
    
    # Track most recent DATASET and CODE URLs for context
    context: Dict[str, Any] = {
        "dataset_link": "",
        "code_link": "",
    }
    
    for i, url in enumerate(urls, 1):
        try:
            category = classify_url(url)
            LOG.debug("URL %d/%d: %s (category: %s)", i, len(urls), url, category)
            
            if category == "DATASET":
                # Update context with most recent dataset
                context["dataset_link"] = url
                LOG.info("Updated context with DATASET: %s", url)
                
            elif category == "CODE":
                # Update context with most recent code repo
                context["code_link"] = url
                context["example_code_present"] = True
                LOG.info("Updated context with CODE: %s", url)
                
            elif category == "MODEL":
                # Score the model with current context
                model_score = score_model(url, context)
                results.append(model_score)
                LOG.info("Completed scoring for MODEL %d: %s (net_score=%.3f)", 
                        len(results), model_score.name, model_score.net_score)
                
        except Exception as e:
            LOG.error("Failed to process URL %s: %s", url, e, exc_info=True)
            # Continue processing remaining URLs
            continue
    
    LOG.info("Completed processing: %d MODEL URLs scored", len(results))
    
    # TODO: Implement parallel processing
    # Future enhancement: Use ThreadPoolExecutor to score multiple models concurrently
    # Example:
    #   with ThreadPoolExecutor(max_workers=4) as executor:
    #       futures = {executor.submit(score_model, url, ctx): url for url in model_urls}
    #       for future in as_completed(futures):
    #           results.append(future.result())
    
    return results
