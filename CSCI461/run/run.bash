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
  # Run pytest with coverage and create machine-readable outputs for autograder
  # 1) run tests with coverage
  python3 -m coverage run -m pytest -q --maxfail=1 --disable-warnings || rc=$?
  rc=${rc:-0}

  # 2) total tests collected (use pytest --collect-only)
  total_tests=$(pytest --collect-only -q 2>/dev/null | tail -n1 | awk '{print $1}' || true)
  # For older pytest versions the collect-only output may differ; fallback to counting test_ defs
  if [[ -z "$total_tests" || "$total_tests" == "collected" ]]; then
    total_tests=$(python3 - <<'PY'
import os
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
  fi

  # 3) passed tests: if rc==0 assume all passed, else 0 (we avoid re-running tests)
  if [[ $rc -eq 0 ]]; then
    passed=$total_tests
  else
    passed=0
  fi

  # 4) coverage percent
  cov_percent=$(coverage report -m | tail -n1 | awk '{print $4}' | sed 's/%//') || cov_percent=0

  echo "${passed}/${total_tests} test cases passed. ${cov_percent}% line coverage achieved."
  exit $rc
elif [[ -f "$cmd" ]]; then
  python3 -m cli.main "$cmd"
  exit $?
else
  usage
  exit 1
fi
