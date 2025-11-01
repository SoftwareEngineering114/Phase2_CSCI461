#!/usr/bin/env python3
"""
Executable CLI entrypoint for the registry scoring system.
Satisfies the autograder spec.

Usage:
    ./run.py install              # Install dependencies
    ./run.py test                 # Run tests with coverage
    ./run.py /path/to/URL_FILE    # Score models from URL file
"""
from __future__ import annotations

import os
import subprocess
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import logging after path setup
from registry.logging_setup import get_logger

LOG = get_logger(__name__)


def run_install() -> int:
    """
    Install dependencies from requirements.txt.
    
    Returns:
        0 on success, 1 on failure
    """
    LOG.info("Starting dependency installation")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--user", "-r", "requirements.txt"],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        LOG.info("Installation completed successfully")
        return 0
    except subprocess.CalledProcessError as e:
        LOG.error("Installation failed: %s", e.stderr)
        print(f"Installation failed: {e.stderr}", file=sys.stderr)
        return 1
    except Exception as e:
        LOG.error("Installation error: %s", e)
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


def run_test() -> int:
    """
    Run tests with coverage and report results.
    
    Prints: "X/Y test cases passed. Z% line coverage achieved."
    
    Returns:
        0 if all tests passed, 1 if any tests failed
    """
    LOG.info("Starting test run with coverage")
    try:
        # First, collect test count
        collect_result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            capture_output=True,
            text=True
        )
        
        total = 0
        for line in collect_result.stdout.split('\n'):
            # Look for line like "3 tests collected" or similar
            if 'test' in line.lower() and ('collected' in line or 'selected' in line):
                parts = line.split()
                if parts and parts[0].isdigit():
                    total = int(parts[0])
                    break
        
        # Run pytest with coverage
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "--maxfail=1",
                "--disable-warnings",
                "-q",
                "--cov=src",
                "--cov-report=term-missing",
            ],
            capture_output=True,
            text=True
        )
        
        # Parse output to extract results
        output_lines = result.stdout + result.stderr
        
        passed = 0
        failed = 0
        coverage_percent = 0
        
        # Look for pytest summary line (e.g., "5 passed in 0.23s" or "3 passed, 1 failed")
        for line in output_lines.split('\n'):
            # Parse test results
            if 'passed' in line.lower() and ('failed' in line.lower() or 'error' in line.lower() or 'in' in line):
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.isdigit():
                        next_word = parts[i+1].lower() if i+1 < len(parts) else ""
                        if 'passed' in next_word:
                            passed = int(part)
                        elif 'failed' in next_word or 'error' in next_word:
                            failed = int(part)
            
            # Look for coverage line (e.g., "TOTAL ... 85%")
            if 'TOTAL' in line and '%' in line:
                parts = line.split()
                for part in parts:
                    if '%' in part:
                        try:
                            coverage_percent = int(part.rstrip('%'))
                        except ValueError:
                            pass
        
        # If we didn't parse passed/failed correctly, use return code
        if result.returncode == 0 and passed == 0:
            passed = total
            failed = 0
        elif passed == 0 and failed == 0:
            # Parse failed - try to count from verbose output
            if result.returncode != 0:
                failed = total
                passed = 0
            else:
                passed = total
                failed = 0
        
        # Calculate actual total if we have partial info
        if passed > 0 or failed > 0:
            total = max(total, passed + failed)
        
        # Print formatted output
        print(f"{passed}/{total} test cases passed. {coverage_percent}% line coverage achieved.")
        
        LOG.info("Test run completed: %d/%d passed, %d%% coverage", passed, total, coverage_percent)
        
        # Return 0 if all tests passed, 1 otherwise
        return 0 if result.returncode == 0 else 1
        
    except Exception as e:
        LOG.error("Test run failed: %s", e)
        print(f"ERROR running tests: {e}", file=sys.stderr)
        return 1


def run_scoring(url_file: str) -> int:
    """
    Score models from URL file and output NDJSON.
    
    Args:
        url_file: Absolute path to URL file
        
    Returns:
        0 on success, 1 on error
    """
    LOG.info("Starting scoring for URL file: %s", url_file)
    try:
        # Import here to avoid issues if dependencies not installed
        from registry.ndjson_output import modelscore_to_ndjson_line
        from registry.scorer import process_url_list
        
        # Validate URL file path
        if not os.path.isabs(url_file):
            LOG.error("URL_FILE must be an absolute path: %s", url_file)
            print("ERROR: URL_FILE must be an absolute path", file=sys.stderr)
            return 1
        
        if not os.path.exists(url_file):
            LOG.error("URL_FILE does not exist: %s", url_file)
            print(f"ERROR: URL_FILE does not exist: {url_file}", file=sys.stderr)
            return 1
        
        # Read URLs from file
        LOG.debug("Reading URLs from file")
        with open(url_file, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
        
        LOG.info("Read %d URLs from file", len(urls))
        
        # Process URLs and get ModelScore objects
        model_scores = process_url_list(urls)
        
        LOG.info("Writing NDJSON output for %d models", len(model_scores))
        
        # Output NDJSON for each model
        for i, model_score in enumerate(model_scores, 1):
            ndjson_line = modelscore_to_ndjson_line(model_score)
            print(ndjson_line)
            LOG.debug("Wrote NDJSON line %d: %s", i, model_score.name)
        
        LOG.info("Scoring completed successfully")
        return 0
        
    except Exception as e:
        LOG.error("Scoring failed: %s", e, exc_info=True)
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1


def main() -> int:
    """
    Main entry point.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    if len(sys.argv) < 2:
        print("Usage:", file=sys.stderr)
        print("  python run.py install", file=sys.stderr)
        print("  python run.py test", file=sys.stderr)
        print("  python run.py /absolute/path/to/URL_FILE", file=sys.stderr)
        return 1
    
    command = sys.argv[1]
    
    if command == "install":
        return run_install()
    elif command == "test":
        return run_test()
    else:
        # Treat as URL_FILE path
        return run_scoring(command)


if __name__ == "__main__":
    sys.exit(main())

