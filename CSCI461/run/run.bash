#!/usr/bin/env bash
set -euo pipefail

cmd="${1:-}"

usage() {
  echo "Usage:"
  echo "  ./run install"
  echo "  ./run test"
  echo "  ./run /absolute/path/to/URL_FILE"
}

if [[ -z "$cmd" ]]; then usage; exit 1; fi

if [[ "$cmd" == "install" ]]; then
  python3 -m pip install --user -U pip
  python3 -m pip install --user -r requirements.txt
  echo "Install complete."
  exit 0
elif [[ "$cmd" == "test" ]]; then
  # Run pytest with coverage and print summary line expected by autograder
  python3 -m coverage run -m pytest -q --maxfail=1 --disable-warnings
  rc=$?
  # Count tests run and passed (pytest -q exit 0 means all passed)
  total=$(python3 - <<'PY'
import pytest
from _pytest.config import get_config
config = get_config()
session = pytest.main(['-q', '--maxfail=1', '--disable-warnings', '--collect-only'])
print(0)
PY
)
  # Instead of attempting to re-run pytest to count tests, infer from collected tests file or default to a placeholder
  # Use coverage report to get line coverage
  cov=$(python3 - <<'PY'
import coverage,sys
cov = coverage.Coverage()
cov.load()
report = cov.report(show_missing=False)
print(int(round(report)))
PY
  # Fallback values: if pytest failed rc!=0, still try to print something
  # For now, use a simple heuristic: count test functions in tests/ directory
  total_tests=$(python3 - <<'PY'
import os,re
cnt=0
for root,_,files in os.walk('tests'):
  for f in files:
    if f.endswith('.py'):
      for ln in open(os.path.join(root,f),'r',encoding='utf-8').read().splitlines():
        if ln.strip().startswith('def test_'):
          cnt+=1
print(cnt)
PY
)
  # Assume all passed if rc==0
  if [[ $rc -eq 0 ]]; then
    passed=$total_tests
  else
    passed=0
  fi
  echo "${passed}/${total_tests} test cases passed. ${cov}% line coverage achieved."
  exit $rc
elif [[ -f "$cmd" ]]; then
  python3 -m cli.main "$cmd"
  exit $?
else
  usage
  exit 1
fi
