#!/usr/bin/env bash
# Reproduce every number, table and figure in the manuscript from the released
# metric JSONs shipped in inputs/batch/.
#
#   bash run_all.sh
#
# No arguments, no environment variables, no path editing. All paths are resolved
# relative to this script, so the package may be extracted anywhere.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

PY="${PYTHON:-python3}"
export PYTHONDONTWRITEBYTECODE=1
export MPLCONFIGDIR="$(mktemp -d "${TMPDIR:-/tmp}/msd-repro-mplconfig.XXXXXX")"
echo "== environment =="
"$PY" - <<'PYV'
import sys, numpy, pandas, matplotlib
print(f"python     {sys.version.split()[0]}")
print(f"numpy      {numpy.__version__}")
print(f"pandas     {pandas.__version__}")
print(f"matplotlib {matplotlib.__version__}")
PYV

mkdir -p outputs figures

echo
echo "== stage 1/6  build_dataset.py =="
"$PY" src/build_dataset.py

echo
echo "== stage 2/6  export_supplementary_provenance.py =="
"$PY" src/export_supplementary_provenance.py

echo
echo "== stage 3/6  analyze.py =="
"$PY" src/analyze.py | tee outputs/analysis_console.txt

echo
echo "== stage 4/6  figures_v2.py =="
"$PY" src/figures_v2.py

echo
echo "== stage 5/6  verify.py =="
"$PY" src/verify.py | tee outputs/verification_report.txt

echo
echo "== stage 6/6  checksums =="
"$PY" src/make_manifest.py

echo
echo "REPRODUCTION COMPLETE"
