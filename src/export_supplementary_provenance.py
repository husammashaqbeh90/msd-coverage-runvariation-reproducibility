#!/usr/bin/env python3
"""Export the machine-readable source table for Supplementary Table S5."""

import csv
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
SOURCE = PACKAGE / "inputs" / "provenance" / "evaluation_group_provenance.tsv"
OUTPUT = PACKAGE / "outputs" / "Supplement_evaluation_group_provenance.tsv"
FIELDS = [
    "number",
    "source_archive",
    "runs",
    "evaluation_group",
    "trajectory_artifact_evaluated",
    "status_in_this_study",
]


with SOURCE.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle, delimiter="\t"))

if list(rows[0]) != FIELDS:
    raise SystemExit("Unexpected Supplementary Table S5 input columns")
if len(rows) != 14:
    raise SystemExit(f"Expected 14 evaluation groups, found {len(rows)}")
if len({row["source_archive"] for row in rows}) != 6:
    raise SystemExit("Expected six source archives")
analysed = [row for row in rows if row["status_in_this_study"] == "Analyzed"]
if len(analysed) != 5 or sum(int(row["runs"]) for row in analysed) != 968:
    raise SystemExit("The analysed-group provenance does not match 968 source records")
if sum(row["status_in_this_study"] == "Fallback only" for row in rows) != 1:
    raise SystemExit("Expected one released fallback group")

with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t")
    writer.writeheader()
    writer.writerows(rows)

print(f"wrote {OUTPUT.relative_to(PACKAGE)} ({len(rows)} evaluation groups)")
