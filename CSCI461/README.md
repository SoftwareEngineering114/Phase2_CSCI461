# CSCI461 CLI — Phase 1

Quick start

1. Clone the repository (if you haven't already), create a local virtual environment, and activate it:

```bash
# Replace <repo-url> with the origin URL for your team's repo
git clone <repo-url>

# Change into the cloned repository directory. Replace <repo-dir> with the directory name
# created by the git clone command (for example: CSCI461)
cd <repo-dir>/CSCI461

# Create and activate a local virtual environment
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies and the package in editable mode:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

3. Run tests:

```bash
pytest -q
```

4. Run the CLI (example):

```bash
# Use the wrapper script or run the module directly
bash run/run.bash run path/to/urls.txt
# or
python -m cli.main path/to/urls.txt
```

Environment variables
- `HUGGINGFACE_HUB_TOKEN` (optional) — improves Hugging Face API rate limits
- `GITHUB_TOKEN` (optional) — for private repo access or higher GitHub rate limits

Notes
- Do not commit local virtual environments. `.venv/` is ignored in `.gitignore`.
- See `CSCI461/.env.sample` for environment variable examples.
