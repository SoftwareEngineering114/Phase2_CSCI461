# CSCI461 Registry — Phase 2 Refactored Package

<!-- Test comment: CI/CD pipeline active -->
<!-- CD workflow updated: EC2 Docker deployment -->

A Python package for trustworthy model reuse scoring with comprehensive metrics.

## Quick Start

1. Clone the repository (if you haven't already), create a local virtual environment, and activate it:

```bash
# Replace <repo-url> with the origin URL for your team's repo
git clone <repo-url>

# Change into the cloned repository directory. Replace <repo-dir> with the directory name
# created by the git clone command (for example: CSCI461)
cd <repo-dir>/CSCI461

# Create and activate a local virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies and the package in editable mode:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

3. Run tests:

```bash
# Quick test run
pytest -q

# With coverage report
pytest --cov=registry --cov-report=term-missing
```

4. Run the CLI:

```bash
# Using the wrapper script
bash run/run.bash /absolute/path/to/urls.txt

# Using Python module directly
python -m registry.cli /absolute/path/to/urls.txt

# Using the run.py script
python run.py /absolute/path/to/urls.txt
```

## Package Structure

```
.
├─ run.py                   # Executable CLI entrypoint
├─ requirements.txt         # Python dependencies
├─ pyproject.toml          # Package configuration + tool configs
├─ setup.cfg               # Flake8 configuration
├─ src/
│   └─ registry/
│       ├─ __init__.py
│       ├─ models.py        # Dataclasses for scores + resources
│       ├─ url_parser.py    # URL detection and metadata extraction
│       ├─ metrics/
│       │    ├─ __init__.py
│       │    ├─ base.py
│       │    ├─ ramp_up_time.py
│       │    ├─ bus_factor.py
│       │    ├─ performance_claims.py
│       │    ├─ license_metric.py
│       │    ├─ size_score.py
│       │    ├─ dataset_and_code_score.py
│       │    ├─ dataset_quality.py
│       │    └─ code_quality.py
│       ├─ scorer.py        # Orchestrates metrics in parallel
│       ├─ ndjson_output.py # NDJSON formatting
│       ├─ logging_setup.py # LOG_FILE and LOG_LEVEL handling
│       └─ cli.py           # Main CLI interface
├─ tests/
│   ├─ conftest.py          # Shared fixtures
│   ├─ test_ndjson_output.py
│   └─ test_scorer_ranges.py
```

## Metrics

The package computes the following metrics for MODEL resources:

- **Ramp-up Time**: Documentation quality and ease of getting started
- **Bus Factor**: Contributor diversity and project resilience
- **Performance Claims**: Presence of benchmarks and evaluations
- **License**: License permissiveness and clarity
- **Size Score**: Hardware compatibility (Raspberry Pi, Jetson Nano, Desktop PC, AWS Server)
- **Dataset & Code Score**: Availability of training data and example code
- **Dataset Quality**: Quality based on download counts
- **Code Quality**: Engineering practices (tests, CI/CD, linting)
- **Net Score**: Weighted combination of all metrics

## Environment Variables

- `LOG_FILE`: Path to log file (optional, defaults to stderr)
- `LOG_LEVEL`: Logging verbosity (0=CRITICAL, 1=INFO, 2+=DEBUG)
- `HUGGINGFACE_HUB_TOKEN`: Improves Hugging Face API rate limits (optional)
- `GITHUB_TOKEN`: For private repo access or higher GitHub rate limits (optional)

## Development

### Type Checking

```bash
mypy src/registry
```

### Code Formatting

```bash
isort src tests
flake8 src tests
```

### Running Specific Tests

```bash
pytest tests/test_ndjson_output.py -v
pytest tests/test_scorer_ranges.py -v
```

## CI Pipeline (Pull Request Validation)

Every pull request into `main` triggers a GitHub Actions workflow defined in `.github/workflows/ci.yml`.

The workflow:
- Installs dependencies
- Runs `flake8` for linting/style
- Runs `mypy` for static type checking
- Runs `pytest` with coverage against:
  - the scoring / metrics code
  - NDJSON compliance
  - FastAPI endpoints (upload, ingest, enumerate)

Long-running performance tests (e.g. multiple concurrent clients) are intentionally excluded from CI and are run manually, which matches course expectations.

## CD Pipeline (Automatic Deploy on Merge)

After code is merged into `main`, GitHub Actions runs `.github/workflows/cd.yml`.

The CD workflow:
1. Builds a Docker image of our FastAPI service (the Trustworthy Model Registry API).
2. Logs in to Amazon ECR and pushes the new `:latest` image.
3. SSHs into our AWS EC2 host.
4. On EC2, it:
   - Logs in to ECR
   - Pulls the latest image
   - Stops the old container
   - Runs the new container on port 80 → 8000 with our service
   - Passes `LOG_FILE` and `LOG_LEVEL` so logs are captured, which satisfies the logging requirement from the spec.

This screenshot (the Actions run for 'CD - Deploy to AWS') will be used in our Milestone 8 report under 'Automated service deployment (CD)'.

## Notes

- All code includes type annotations for strong typing
- Tests use pytest with coverage reporting
- Package follows standard Python packaging conventions
- Do not commit local virtual environments (`.venv/` is gitignored)
# Phase 2 Complete - CI/CD Enabled
# CI Test
