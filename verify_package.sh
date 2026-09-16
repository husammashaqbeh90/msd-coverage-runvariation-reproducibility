#!/usr/bin/env bash
# Independent verification of this package.
#
#   bash verify_package.sh
#
# 1. checks every shipped file against SHA256SUMS.txt as received
# 2. re-runs the full pipeline
# 3. checks the regenerated files against the same checksums
#
# Step 1 proves the archive arrived intact. Step 3 proves the outputs and figures
# are reproduced, not merely shipped. Exits non-zero on any mismatch.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
PY="${PYTHON:-python3}"

check () {
  "$PY" - "$1" <<'PYEOF'
import hashlib, os, sys
label = sys.argv[1]
ship = {}
for line in open("SHA256SUMS.txt", encoding="utf-8"):
    h, p = line.rstrip("\n").split("  ", 1)
    ship[p] = h
bad = []
for p, h in sorted(ship.items()):
    if not os.path.exists(p):
        bad.append(("MISSING", p)); continue
    g = hashlib.sha256(open(p, "rb").read()).hexdigest()
    if g != h:
        bad.append(("DIFFERS", p))
for k, p in bad:
    print(f"  {k}  {p}")
print(f"  {label}: {len(ship)-len(bad)}/{len(ship)} files match")
sys.exit(1 if bad else 0)
PYEOF
}

echo "== 1/3  archive integrity as received =="
cp SHA256SUMS.txt /tmp/_shipped_sums.$$
check "as received"

echo
echo "== 2/3  full re-run =="
bash run_all.sh > /tmp/_verify_run.$$ 2>&1 || { tail -30 /tmp/_verify_run.$$; exit 1; }
echo "  run_all.sh completed"

echo
echo "== 3/3  regenerated files against the shipped checksums =="
cp /tmp/_shipped_sums.$$ /tmp/_cmp_sums.$$
"$PY" - <<'PYEOF'
import hashlib, os, sys, glob
sums = sorted(glob.glob("/tmp/_cmp_sums.*"))[-1]
ship = {}
for line in open(sums, encoding="utf-8"):
    h, p = line.rstrip("\n").split("  ", 1)
    ship[p] = h
bad = []
for p, h in sorted(ship.items()):
    if not os.path.exists(p):
        bad.append(("MISSING", p)); continue
    if hashlib.sha256(open(p, "rb").read()).hexdigest() != h:
        bad.append(("DIFFERS", p))
for k, p in bad:
    print(f"  {k}  {p}")
print(f"  after re-run: {len(ship)-len(bad)}/{len(ship)} files match")
sys.exit(1 if bad else 0)
PYEOF
rm -f /tmp/_shipped_sums.$$ /tmp/_cmp_sums.$$ /tmp/_verify_run.$$
echo
echo "PACKAGE VERIFIED"
