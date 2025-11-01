"""
Command-line interface for the registry scoring system.
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import List

from .logging_setup import configure_logging
from .ndjson_output import modelscore_to_ndjson_line
from .scorer import process_url_list

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
        
        # Process all URLs and get ModelScore objects for MODEL URLs
        model_scores = process_url_list(urls)
        
        # Output NDJSON for each model
        for model_score in model_scores:
            print(modelscore_to_ndjson_line(model_score))
        
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
