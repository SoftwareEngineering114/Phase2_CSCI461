"""
Pytest configuration and shared fixtures.
"""
from __future__ import annotations

import os
from typing import Any, Dict

import pytest


@pytest.fixture(autouse=True)
def disable_logging(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Automatically disable logging for all tests to prevent log file creation.
    
    Sets LOG_LEVEL=0 so tests don't write log files.
    """
    monkeypatch.setenv("LOG_LEVEL", "0")


@pytest.fixture
def sample_context() -> Dict[str, Any]:
    """
    Provide a sample context dictionary for testing metrics.
    """
    return {
        "url": "https://huggingface.co/example/model",
        "name": "example/model",
        "hf_readme": "This is a sample README with example code and quickstart guide. "
                     "The model achieves 95% accuracy on benchmark datasets. "
                     "We evaluate on multiple tasks.",
        "license": "MIT",
        "git_contributors": 3,
        "weights_total_bytes": 500 * 1024 * 1024,  # 500 MB
        "has_tests": True,
        "has_ci": True,
        "lint_ok": True,
        "dataset_link": "https://huggingface.co/datasets/example",
        "example_code_present": True,
        "dataset_downloads": 1000,
    }


@pytest.fixture
def minimal_context() -> Dict[str, Any]:
    """
    Provide a minimal context with default/missing values.
    """
    return {
        "url": "https://huggingface.co/minimal/model",
        "name": "minimal/model",
        "hf_readme": "",
        "license": "",
        "git_contributors": 1,
    }

