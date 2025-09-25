from __future__ import annotations
import logging
import os
import time
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Tuple

import requests
from huggingface_hub import hf_hub_download, model_info
from git import Repo, GitCommandError

LOG = logging.getLogger(__name__)


def configure_logging() -> None:
    # Respect environment variables $LOG_FILE and $LOG_LEVEL
    log_file = os.environ.get("LOG_FILE")
    level = int(os.environ.get("LOG_LEVEL", "0"))
    lvl = logging.CRITICAL
    if level >= 2:
        lvl = logging.DEBUG
    elif level == 1:
        lvl = logging.INFO
    else:
        lvl = logging.CRITICAL

    handlers = []
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    else:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(level=lvl, handlers=handlers, format="%(asctime)s %(levelname)s %(message)s")


def _timed(fn, *args, **kwargs) -> Tuple[float, int]:
    t0 = time.perf_counter()
    v = fn(*args, **kwargs)
    t1 = time.perf_counter()
    try:
        fv = float(v)
    except Exception:
        fv = v
    return fv, int(round((t1 - t0) * 1000))


def _fetch_hf_metadata(model_id: str) -> Dict[str, Any]:
    try:
        LOG.debug("Fetching HF model info for %s", model_id)
        info = model_info(model_id)
        return info.to_dict()
    except Exception as e:
        LOG.info("Hugging Face fetch failed for %s: %s", model_id, e)
        return {}


def ramp_up_time(ctx: Dict[str, Any]) -> Tuple[float, int]:
    def logic(c: Dict[str, Any]) -> float:
        # Simple heuristic: presence of README text and examples
        readme = c.get("hf_readme", "")
        examples = 1.0 if ("example" in readme.lower() or "quickstart" in readme.lower()) else 0.0
        length_score = min(1.0, len(readme.split()) / 300.0)
        return 0.5 * length_score + 0.5 * examples

    return _timed(lambda: logic(ctx))


def bus_factor(ctx: Dict[str, Any]) -> Tuple[float, int]:
    def logic(c: Dict[str, Any]) -> float:
        # Use local git contributors if available
        contributors = c.get("git_contributors", 1)
        if contributors <= 1:
            return 0.1
        return min(1.0, contributors / 5.0)

    return _timed(lambda: logic(ctx))


def performance_claims(ctx: Dict[str, Any]) -> Tuple[float, int]:
    def logic(c: Dict[str, Any]) -> float:
        readme = c.get("hf_readme", "")
        score = 1.0 if ("benchmark" in readme.lower() or "accuracy" in readme.lower() or "eval" in readme.lower()) else 0.0
        return score

    return _timed(lambda: logic(ctx))


def license_score(ctx: Dict[str, Any]) -> Tuple[float, int]:
    def logic(c: Dict[str, Any]) -> float:
        lic = c.get("license", "").lower() if c.get("license") else ""
        if not lic:
            # try readme
            rd = c.get("hf_readme", "").lower()
            if "license" in rd:
                return 0.5
            return 0.0
        if "lgpl" in lic or "mit" in lic or "apache" in lic or "bsd" in lic:
            return 1.0
        return 0.2

    return _timed(lambda: logic(ctx))


def size_score(ctx: Dict[str, Any]) -> Tuple[Dict[str, float], int]:
    def logic(c: Dict[str, Any]) -> Dict[str, float]:
        # total weight size in bytes (if available)
        total = c.get("weights_total_bytes", None)
        if total is None:
            return {"raspberry_pi": 0.0, "jetson_nano": 0.0, "desktop_pc": 1.0, "aws_server": 1.0}
        # thresholds in bytes
        thresholds = {"raspberry_pi": 50 * 1024 * 1024, "jetson_nano": 700 * 1024 * 1024, "desktop_pc": 8 * 1024 * 1024 * 1024, "aws_server": 100 * 1024 * 1024 * 1024}
        out = {}
        for k, thresh in thresholds.items():
            out[k] = min(1.0, max(0.0, 1.0 - (total - thresh) / (thresh * 10))) if total > thresh else 1.0
        return out

    return _timed(lambda: logic(ctx))


def dataset_and_code_score(ctx: Dict[str, Any]) -> Tuple[float, int]:
    def logic(c: Dict[str, Any]) -> float:
        has_dataset = bool(c.get("dataset_link"))
        has_example_code = bool(c.get("example_code_present"))
        return 1.0 if (has_dataset and has_example_code) else (0.5 if (has_dataset or has_example_code) else 0.0)

    return _timed(lambda: logic(ctx))


def dataset_quality(ctx: Dict[str, Any]) -> Tuple[float, int]:
    def logic(c: Dict[str, Any]) -> float:
        # Use HF dataset metadata if available
        downloads = c.get("dataset_downloads", 0)
        if downloads <= 0:
            return 0.2
        # log scale normalization
        import math

        score = min(1.0, math.log1p(downloads) / 10.0)
        return score

    return _timed(lambda: logic(ctx))


def code_quality(ctx: Dict[str, Any]) -> Tuple[float, int]:
    def logic(c: Dict[str, Any]) -> float:
        has_tests = c.get("has_tests", False)
        has_ci = c.get("has_ci", False)
        lint_score = 1.0 if c.get("lint_ok", False) else 0.5 if c.get("lint_warn", False) else 0.0
        return min(1.0, 0.4 * has_tests + 0.3 * has_ci + 0.3 * lint_score)

    return _timed(lambda: logic(ctx))


def _analyze_repo_from_url(url: str, ctx: Dict[str, Any]) -> None:
    # If it's a GitHub repo, shallow clone and inspect
    try:
        tmpd = tempfile.mkdtemp(prefix="modelrepo_")
        LOG.debug("Cloning %s into %s", url, tmpd)
        Repo.clone_from(url, tmpd, depth=20)
        repo = Repo(tmpd)
        # contributors
        contributors = set()
        for commit in repo.iter_commits(max_count=200):
            try:
                contributors.add(commit.author.email)
            except Exception:
                continue
        ctx["git_contributors"] = len(contributors)
        # detect weight files
        total = 0
        has_tests = False
        has_ci = False
        for root, _, files in os.walk(tmpd):
            for f in files:
                if f.endswith(('.bin', '.pt', '.safetensors', '.h5', '.ckpt')):
                    try:
                        total += os.path.getsize(os.path.join(root, f))
                    except Exception:
                        continue
                if f.startswith('test_') or f.endswith('_test.py'):
                    has_tests = True
                if f.endswith('.yml') and ('.github' in root or 'workflows' in root):
                    has_ci = True
        ctx["weights_total_bytes"] = total
        ctx["has_tests"] = has_tests
        ctx["has_ci"] = has_ci
    except GitCommandError as e:
        LOG.info("Git clone failed for %s: %s", url, e)
    except Exception as e:
        LOG.debug("Repo analysis error for %s: %s", url, e)


def compute_all_metrics(ctx: Dict[str, Any]) -> Dict[str, Any]:
    # Pre-populate HF metadata when available
    raw = ctx.get("url")
    if raw and "huggingface.co" in raw:
        # derive model id
        model_id = raw.split('huggingface.co/', 1)[1].strip('/')
        md = _fetch_hf_metadata(model_id)
        ctx["hf_meta"] = md
        # try to get README text if present in metadata
        try:
            ctx["hf_readme"] = md.get("cardData", {}).get("README", "") or md.get("pipeline_tag", "")
        except Exception:
            ctx["hf_readme"] = ""
        # license
        ctx["license"] = md.get("license", {}).get("id") if md.get("license") else md.get("license")

    # If URL looks like a github repo, analyze repo locally
    if raw and "github.com" in raw:
        _analyze_repo_from_url(raw, ctx)

    # Run metrics in parallel
    metrics_fns = {
        "ramp_up_time": ramp_up_time,
        "bus_factor": bus_factor,
        "performance_claims": performance_claims,
        "license": license_score,
        "size_score": size_score,
        "dataset_and_code_score": dataset_and_code_score,
        "dataset_quality": dataset_quality,
        "code_quality": code_quality,
    }

    results: Dict[str, Any] = {}
    with ThreadPoolExecutor(max_workers=min(8, (os.cpu_count() or 1) * 2)) as ex:
        futures = {ex.submit(fn, ctx): name for name, fn in metrics_fns.items()}
        for fut in as_completed(futures):
            name = futures[fut]
            try:
                val, ms = fut.result()
                results[name] = val
                results[f"{name}_latency"] = ms
            except Exception as e:
                LOG.info("Metric %s failed: %s", name, e)
                results[name] = 0.0
                results[f"{name}_latency"] = 0

    return results


def compute_net_score(metrics: Dict[str, Any]) -> Tuple[float, int]:
    def logic() -> float:
        w = {
            "size_score": 0.15,
            "license": 0.15,
            "ramp_up_time": 0.15,
            "bus_factor": 0.10,
            "dataset_and_code_score": 0.10,
            "dataset_quality": 0.10,
            "code_quality": 0.10,
            "performance_claims": 0.15,
        }
        # size_score is an object -> use desktop_pc as representative
        def get_val(k: str) -> float:
            if k == "size_score":
                v = metrics.get("size_score", {})
                if isinstance(v, dict):
                    return float(v.get("desktop_pc", 1.0))
                return float(v)
            return float(metrics.get(k, 0.0))

        return sum(w[k] * get_val(k) for k in w)

    return _timed(logic)


