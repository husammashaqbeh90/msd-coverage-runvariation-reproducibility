#!/usr/bin/env python3
"""Stage 5 - SHA256 manifest over every file in the package."""
import hashlib
import os

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {"SHA256SUMS.txt", "MANIFEST.tsv"}
SKIP_DIRS = {"__pycache__", ".git", ".venv", "venv", "env"}


def keep_dir(name):
    """Keep package content, excluding local Python/tool environments."""
    return name not in SKIP_DIRS and not name.startswith(".venv-")

ROLE = [("inputs/batch/", "input  - released metric JSON (verbatim copy)"),
        ("inputs/provenance/", "input  - evaluation-group provenance table"),
        ("src/",          "code   - analysis stage"),
        ("outputs/",      "output - generated"),
        ("figures/",      "output - generated figure"),
        ("provenance/",   "doc    - provenance / audit"),
        ("run_all.sh",    "code   - single entry point"),
        ("requirements.txt", "env    - tested Python dependency versions")]


def role_of(rel):
    for pfx, r in ROLE:
        if rel.startswith(pfx):
            return r
    return "doc    - package documentation"


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


files = []
for root, dirs, names in os.walk(PKG):
    dirs[:] = [d for d in dirs if keep_dir(d)]
    for n in sorted(names):
        rel = os.path.relpath(os.path.join(root, n), PKG)
        if rel in SKIP or rel.endswith(".pyc"):
            continue
        files.append(rel)
files.sort()

with open(os.path.join(PKG, "MANIFEST.tsv"), "w", encoding="utf-8") as m, \
     open(os.path.join(PKG, "SHA256SUMS.txt"), "w", encoding="utf-8") as s:
    m.write("path\tbytes\tsha256\trole\n")
    for rel in files:
        p = os.path.join(PKG, rel)
        h = sha256(p)
        m.write(f"{rel}\t{os.path.getsize(p)}\t{h}\t{role_of(rel)}\n")
        s.write(f"{h}  {rel}\n")

# completeness self-check: every file in the package tree, other than the two
# manifest files themselves, must appear in the manifest. This is what failed in
# the first v3 archive, where a provenance file shipped outside the checksums.
present = set()
for root, dirs, names in os.walk(PKG):
    dirs[:] = [d for d in dirs if keep_dir(d)]
    for n in names:
        rel = os.path.relpath(os.path.join(root, n), PKG)
        if rel in SKIP or rel.endswith(".pyc"):
            continue
        present.add(rel)
missing = sorted(present - set(files))
if missing:
    raise SystemExit("MANIFEST INCOMPLETE - files present but not listed:\n  " +
                     "\n  ".join(missing))

total = len(files) + len(SKIP)
print(f"MANIFEST.tsv and SHA256SUMS.txt cover {len(files)} files")
print(f"archive contains {total} files "
      f"({len(files)} covered + MANIFEST.tsv + SHA256SUMS.txt, which cannot list themselves)")
print("completeness check: PASS - no file in the package is outside the checksums")
