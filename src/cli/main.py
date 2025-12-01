from __future__ import annotations
import argparse, json, os, sys, time, logging
from typing import Any, Dict, List

from .url_types import parse_url
from .metrics import compute_all_metrics, compute_net_score, configure_logging

configure_logging()

def read_lines(p: str) -> List[str]:
    with open(p, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]

def process_model(url: str, name: str) -> Dict[str, Any]:
    ctx: Dict[str, Any] = {"url": url, "name": name}
    metrics = compute_all_metrics(ctx)
    net_val, net_ms = compute_net_score(metrics)

    return {
        "name": name,
        "category": "MODEL",
        "net_score": round(net_val, 3),
        "net_score_latency": net_ms,
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

def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="CLI for trustworthy model re-use")
    ap.add_argument("url_file", help="Absolute path to newline-delimited URLs file")
    args = ap.parse_args(argv)

    if not os.path.isabs(args.url_file) or not os.path.exists(args.url_file):
        print("ERROR: URL_FILE must be an absolute path to an existing file.", file=sys.stderr)
        return 1

    try:
        for u in read_lines(args.url_file):
            p = parse_url(u)
            if p.category == "MODEL":
                _t0 = time.perf_counter()
                nd = process_model(p.raw, p.name)
                _t1 = time.perf_counter()
                print(json.dumps(nd, separators=(",", ":")))
            # per spec: only output for MODEL lines
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())

