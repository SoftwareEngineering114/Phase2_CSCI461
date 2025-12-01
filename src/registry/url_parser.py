"""
URL parsing and category detection for models, datasets, and code repositories.
Includes metadata fetching from Hugging Face and GitHub.
"""
from __future__ import annotations

import logging
import os
import tempfile
from typing import Any, Dict

from git import GitCommandError, Repo
from huggingface_hub import hf_hub_download, model_info

from .models import ParsedURL, ResourceCategory

LOG = logging.getLogger(__name__)


def classify_url(url: str) -> ResourceCategory:
    """
    Classify a URL into MODEL, DATASET, or CODE category.
    
    Heuristics:
    - huggingface.co/datasets/ → DATASET
    - github.com/ → CODE
    - huggingface.co/<org>/<model> → MODEL (default for HF)
    - default → MODEL
    
    Args:
        url: The URL to classify
        
    Returns:
        ResourceCategory: "MODEL", "DATASET", or "CODE"
    """
    url_lower = url.lower().strip()
    
    if "huggingface.co/datasets/" in url_lower:
        return "DATASET"
    elif "github.com" in url_lower:
        return "CODE"
    else:
        # Default to MODEL for HF URLs and unknowns
        return "MODEL"


def parse_url(url: str) -> ParsedURL:
    """
    Parse a URL and extract its category and name.
    
    Args:
        url: The URL string to parse
        
    Returns:
        ParsedURL object containing category and extracted name
    """
    s = url.strip()
    category = classify_url(s)
    
    # Extract name based on platform
    if "huggingface.co" in s:
        if "/datasets/" in s:
            # Dataset: huggingface.co/datasets/org/dataset
            name = s.split("/datasets/", 1)[1].split("/", 1)[0] if "/datasets/" in s else s
        else:
            # Model: huggingface.co/org/model
            tail = s.split("huggingface.co/", 1)[1]
            parts = [p for p in tail.split("/") if p]
            name = "/".join(parts[:2]) if len(parts) >= 2 else (parts[0] if parts else s)
    elif "github.com" in s:
        # GitHub: github.com/org/repo
        tail = s.split("github.com/", 1)[1]
        parts = [p for p in tail.split("/") if p]
        name = "/".join(parts[:2]) if len(parts) >= 2 else (parts[0] if parts else s)
    else:
        # Use last path component as name
        name = s.rstrip('/').split('/')[-1] if '/' in s else s
    
    return ParsedURL(s, category, name)


def fetch_repo_info(url: str) -> Dict[str, Any]:
    """
    Fetch repository metadata needed for metric computation.
    
    Pulls:
    - README text
    - License information
    - Commit history (if GitHub)
    - Downloads/likes (if Hugging Face)
    - File sizes
    - Tests/CI presence
    
    Args:
        url: The repository URL
        
    Returns:
        Dictionary with repository metadata. Never raises - returns partial
        info on network failure or missing data.
    """
    info: Dict[str, Any] = {
        "url": url,
        "hf_readme": "",
        "license": "",
        "git_contributors": 1,
        "weights_total_bytes": None,
        "has_tests": False,
        "has_ci": False,
        "lint_ok": False,
        "lint_warn": False,
        "dataset_link": "",
        "example_code_present": False,
        "dataset_downloads": 0,
    }
    
    try:
        # Fetch Hugging Face metadata if applicable
        if "huggingface.co" in url:
            _fetch_huggingface_info(url, info)
        
        # Analyze Git repository if applicable
        if "github.com" in url:
            _fetch_github_info(url, info)
            
    except Exception as e:
        LOG.debug("fetch_repo_info error for %s: %s", url, e)
    
    return info


def _fetch_huggingface_info(url: str, info: Dict[str, Any]) -> None:
    """
    Fetch metadata from Hugging Face Hub.
    
    Args:
        url: Hugging Face URL
        info: Dictionary to populate with metadata
    """
    try:
        # Extract model ID
        model_id = url.split('huggingface.co/', 1)[1].strip('/')
        
        LOG.debug("Fetching HF model info for %s", model_id)
        hf_meta = model_info(model_id)
        meta_dict = hf_meta.to_dict()
        
        # Extract README
        try:
            info["hf_readme"] = (
                meta_dict.get("cardData", {}).get("README", "")
                or meta_dict.get("modelId", "")
                or ""
            )
        except Exception:
            info["hf_readme"] = ""
        
        # Extract license
        license_data = meta_dict.get("license", {})
        if isinstance(license_data, dict):
            info["license"] = license_data.get("id", "")
        else:
            info["license"] = str(license_data) if license_data else ""
        
        # Extract download count (if available)
        info["dataset_downloads"] = meta_dict.get("downloads", 0)
        
        # TODO: Extract file sizes from model card or API
        # TODO: Detect example code in model card
        
    except Exception as e:
        LOG.info("Hugging Face fetch failed for %s: %s", url, e)


def _fetch_github_info(url: str, info: Dict[str, Any]) -> None:
    """
    Clone and analyze a GitHub repository.
    
    Args:
        url: GitHub repository URL
        info: Dictionary to populate with metadata
    """
    try:
        tmpd = tempfile.mkdtemp(prefix="modelrepo_")
        LOG.debug("Cloning %s into %s", url, tmpd)
        
        # Shallow clone for efficiency
        Repo.clone_from(url, tmpd, depth=20)
        repo = Repo(tmpd)
        
        # Count unique contributors
        contributors = set()
        for commit in repo.iter_commits(max_count=200):
            try:
                contributors.add(commit.author.email)
            except Exception:
                continue
        info["git_contributors"] = len(contributors)
        
        # Analyze repository contents
        total_weights = 0
        has_tests = False
        has_ci = False
        
        for root, _, files in os.walk(tmpd):
            for f in files:
                # Detect model weight files
                if f.endswith(('.bin', '.pt', '.safetensors', '.h5', '.ckpt', '.pth')):
                    try:
                        total_weights += os.path.getsize(os.path.join(root, f))
                    except Exception:
                        continue
                
                # Detect test files
                if f.startswith('test_') or f.endswith('_test.py') or 'test' in root.lower():
                    has_tests = True
                
                # Detect CI/CD configuration
                if (f.endswith('.yml') or f.endswith('.yaml')) and ('.github' in root or 'workflows' in root):
                    has_ci = True
                
                # Detect README
                if f.lower() == 'readme.md' or f.lower() == 'readme':
                    try:
                        with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as rf:
                            info["hf_readme"] = rf.read()
                    except Exception:
                        pass
        
        info["weights_total_bytes"] = total_weights if total_weights > 0 else None
        info["has_tests"] = has_tests
        info["has_ci"] = has_ci
        
        # TODO: Run linter and set lint_ok/lint_warn
        # TODO: Detect dataset links in README
        # TODO: Detect example code files
        
    except GitCommandError as e:
        LOG.info("Git clone failed for %s: %s", url, e)
    except Exception as e:
        LOG.debug("GitHub repo analysis error for %s: %s", url, e)
