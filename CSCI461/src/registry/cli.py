"""
Command-line interface for the registry scoring system.
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import List

from .logging_setup import configure_logging
from .models import ResourceScore
from .ndjson_output import format_ndjson_line
from .scorer import compute_all_metrics, compute_net_score, populate_context
from .url_parser import parse_url

# Configure logging based on environment variables
configure_logging()


def read_url_file(path: str) -> List[str]:
    """
    Read URLs from a file, one per line.
    
    Args:
        path: Absolute path to the URL file
        
    Returns:
        List of URL strings
    """
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def process_model_url(url: str, name: str) -> None:
    """
    Process a single MODEL URL and output NDJSON result.
    
    Args:
        url: The model URL to process
        name: The model name/identifier
    """
    # Build context with metadata
    ctx = populate_context(url, name)
    
    # Compute all metrics
    metrics = compute_all_metrics(ctx)
    
    # Compute net score
    net_score, net_latency = compute_net_score(metrics)
    
    # Build output dictionary
    output = {
        "name": name,
        "category": "MODEL",
        "net_score": round(net_score, 3),
        "net_score_latency": net_latency,
        "ramp_up_time": round(metrics["ramp_up_time"], 3),
        "ramp_up_time_latency": metrics["ramp_up_time_latency"],
        "bus_factor": round(metrics["bus_factor"], 3),
        "bus_factor_latency": metrics["bus_factor_latency"],
        "performance_claims": round(metrics["performance_claims"], 3),
        "performance_claims_latency": metrics["performance_claims_latency"],
        "license": round(metrics["license"], 3),
        "license_latency": metrics["license_latency"],
        "size_score": metrics["size_score"],
        "size_score_latency": metrics["size_score_latency"],
        "dataset_and_code_score": round(metrics["dataset_and_code_score"], 3),
        "dataset_and_code_score_latency": metrics["dataset_and_code_score_latency"],
        "dataset_quality": round(metrics["dataset_quality"], 3),
        "dataset_quality_latency": metrics["dataset_quality_latency"],
        "code_quality": round(metrics["code_quality"], 3),
        "code_quality_latency": metrics["code_quality_latency"],
    }
    
    # Output NDJSON line
    print(format_ndjson_line(output))


def main(argv: List[str] | None = None) -> int:
    """
    Main CLI entry point.
    
    Args:
        argv: Command line arguments (for testing)
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="CLI for trustworthy model re-use scoring"
    )
    parser.add_argument(
        "url_file",
        help="Absolute path to newline-delimited URLs file"
    )
    args = parser.parse_args(argv)
    
    # Validate input file
    if not os.path.isabs(args.url_file) or not os.path.exists(args.url_file):
        print(
            "ERROR: URL_FILE must be an absolute path to an existing file.",
            file=sys.stderr
        )
        return 1
    
    try:
        urls = read_url_file(args.url_file)
        
        for url in urls:
            parsed = parse_url(url)
            
            # Only process MODEL URLs per spec
            if parsed.category == "MODEL":
                process_model_url(parsed.raw, parsed.name)
        
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

