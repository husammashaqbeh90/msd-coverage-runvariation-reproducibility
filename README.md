# Reproducibility package v4.0.0

Companion package for the manuscript:

> **Trajectory Error and Run-to-Run Variation at High Output Coverage: Evidence from Released Monado SLAM Benchmark Results**

## Release scope

This is the submission companion package for the released-artifact secondary
analysis reported in the manuscript. It reconstructs the analysis population,
all reported numerical summaries, Supplementary Tables S1–S5, and Figures 1–3
from the released metric JSON files included here. It does not download data,
modify the released source tree, or execute a VIO/SLAM system.

The permanent repository URL and archival DOI are publication metadata to be
added to the manuscript when this exact release is deposited. They do not alter
the inputs, code, or reported results in this archive.

## Reproduce everything

Create the tested environment, then run:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
bash run_all.sh
```

`run_all.sh` takes no arguments, needs no network connection, and resolves every
path relative to itself. It may therefore be run from a fresh extraction in any
directory. To verify both archive integrity and regenerated outputs against the
shipped checksums, run:

```bash
bash verify_package.sh
```

## Tested environment

The release was generated and byte-checked with Python 3.12.13, NumPy 2.3.5,
pandas 2.2.3, and Matplotlib 3.10.8. `requirements.txt` pins these versions.
The scripts print the active environment at the beginning of each run so that a
departure from the tested environment is visible in the execution record.

## Pipeline

| Stage | Script | Primary outputs |
|---|---|---|
| 1 | `src/build_dataset.py` | parsed record tables from released metric JSON files |
| 2 | `src/export_supplementary_provenance.py` | Supplementary Table S5 provenance table |
| 3 | `src/analyze.py` | manuscript Tables 1–4 and Supplementary Tables S1–S4 |
| 4 | `src/figures.py` | Figures 1–3 in PNG and PDF |
| 5 | `src/verify.py` | external and structural checks |
| 6 | `src/make_manifest.py` | complete SHA-256 manifest |

`src/make_manifest.py` aborts if a package file other than the two manifest
files themselves is absent from the manifest. `SHA256SUMS.txt` and
`MANIFEST.tsv` cannot contain hashes of their own current contents.

## Inputs and analysis groups

`inputs/batch/` contains verbatim copies of the released metric JSON files read
from the MSD run release. The five groups used for the primary analysis are
`basalt`, `dmvio.scaled`, `okvis2.vio`, `orbslam3.rt`, and `snakeslam.causal`.
For the fourteen records in which the released causal Snake-SLAM result is
unavailable, `snakeslam.rtvalid` is used as the released fallback. The raw
`snakeslam.rt` and `dmvio.rt` groups are retained only as auditable comparison
groups and are not used as primary-analysis coverage data.

`inputs/provenance/evaluation_group_provenance.tsv` records the fourteen
evaluation groups derived from the six released source archives. It is exported
unchanged as `outputs/Supplement_evaluation_group_provenance.tsv` for
Supplementary Table S5.

## Supplementary-table files

| Manuscript table | Machine-readable file |
|---|---|
| S1 | `outputs/Supplement_system_stratification.csv` |
| S2 | `outputs/Supplement_leave_one_system_out.csv` |
| S3 | `outputs/Supplement_benchmark_selected_population.csv` |
| S4 | `outputs/Supplement_repeated_triplet_details.csv` |
| S5 | `outputs/Supplement_evaluation_group_provenance.tsv` |

## Metric convention

`ate` and `rte` entries are `[rmse, std]` pairs; this analysis uses element 0,
the RMSE. `success` and `completion` entries are scalar values. The metric-file
convention was checked against the publicly released `xrtslam-metrics`
implementation.

## Scope and limitations

The study limitations are documented in
`provenance/RELEASE_SCOPE_AND_LIMITATIONS.md`. They are interpretation bounds,
not unresolved computational failures. Historical corrections from the earlier
analysis are retained in `provenance/MANUSCRIPT_CHANGES_v1_to_v3.md`.
