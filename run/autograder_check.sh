#!/usr/bin/env bash
set -euo pipefail

# Lightweight helper for graders/CI to validate the repo on a fresh machine (e.g. ECEPROG server)
# Usage: ./run/autograder_check.sh [optional-path-to-urls-file]

echo "=== Autograder check: environment validation ==="

PYTHON=$(command -v python3 || true)
if [[ -z "$PYTHON" ]]; then
  echo "python3 not found in PATH. Please install Python 3.8+ and retry." >&2
  exit 2
fi

echo "Using python: $PYTHON"
echo "Python version: $($PYTHON --version 2>&1)"

echo "Installing requirements (user site) ..."
$PYTHON -m pip install --user --upgrade pip setuptools wheel
$PYTHON -m pip install --user -r requirements.txt

echo "Running the project's test/coverage flow via ./run test"
./run/run.bash test
rc=$?

if [[ $rc -ne 0 ]]; then
  echo "Autograder check: tests failed (exit $rc)." >&2
  exit $rc
fi

echo "Tests passed. If you want to run the CLI on a URLs file, pass it as the first argument."
if [[ -n "${1:-}" ]]; then
  infile="$1"
  echo "Running CLI: ./run/run.bash $infile"
  ./run/run.bash "$infile"
fi

echo "Autograder check completed successfully."
exit 0
