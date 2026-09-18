# Changelog

## 4.1.1 — 2026-09-18

Authorship, funding, and verification-robustness update. No inputs, analysis code, derived tables, figures, or reported numerical results changed.

### Changed
- `CITATION.cff`, `README.md`, and `VERSION` now identify all four manuscript authors.
- The release records support from the Multimedia University (MMU) Postdoc Fellowship Fund (grant no. MMUI/260011).
- `verify_package.sh` now compares regenerated files against the checksum snapshot created by that invocation, preventing an unrelated stale temporary checksum file from affecting the result.

## 4.1.0 — 2026-09-17

Figure-generation and release-metadata update. No input data, statistical-analysis
code, derived table, or reported numerical result changed; every output in
`outputs/` is byte-identical to v4.0.0.

### Added
- `src/figures_v2.py` — the figure script for the revised manuscript.
- `figures/Figure2_coverage_and_ATE.{pdf,png}` — replaces
  `Figure2_high_coverage_ATE_distribution`. Panel A now carries a per-system
  ECDF alongside the aggregate; panel B is new and plots output coverage against
  ATE for all 861 evaluable records.
- `figures/Figure3_repeated_run_variation.{pdf,png}` — panel A is the ECDF of the
  within-triplet max/min ratio for ATE and RTE; panel B shows the 11 triplets
  that crossed a threshold.
- `figures/FigureS1_repeated_run_ATE_ranges.{pdf,png}` — the 122-row triplet
  chart, previously Figure 3, now the supplementary figure. Produced by the
  legacy `figure3()` in `src/figures.py`; its annotation now uses “runs” to
  match the manuscript terminology.

### Changed
- `figures/Figure1_study_design.{pdf,png}` — PRISMA-style flow with explicit
  exclusion boxes (968 → 861 → 612), and the sensitivity block attached to the
  RQ1 arm only.
- `VERSION`, `CITATION.cff` — new manuscript title.

### Retained
- `src/figures.py` remains available as the legacy figure generator. The only
  source change is the terminology update in the supplementary annotation;
  analytical inputs and plotted values are unchanged.

### Verification
Both figure scripts read the same two files, `outputs/records_primary.csv` and
`outputs/Supplement_repeated_triplet_details.csv`. The 22 headline values in the
revised figures were recomputed from those files and match the manuscript tables
exactly.

## 4.0.0 — 2026-09-16
Initial released package.
