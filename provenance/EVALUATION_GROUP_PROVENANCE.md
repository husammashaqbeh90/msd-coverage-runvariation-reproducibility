# Evaluation-group provenance

**Status:** CLOSED
**Evidence:** `runs/evaluate.fish` (12,572 B), `benchmark_table_source.py`, `runs/OKVIS2-SLAM/README.md`, `runs/README_*.md`, released metric JSONs.
**Method:** direct inspection of the released evaluation script; no inference from file names.

---

## 1. What the released pipeline actually produces

`evaluate.fish` unpacks **six source archives** and derives **fourteen evaluation
groups** from them. Groups derived from the same archive share the same executions;
they differ only in **which estimated-trajectory file is evaluated**. The script
copies the selected file to `tracking.csv`, then runs `batch.py` once per group for
each of the four metrics (`ate`, `rte`, `success`, `completion`).

| # | Source archive | Runs | Evaluation group | Trajectory artifact | evaluate.fish lines | Analysed here |
|---|---|---|---|---|---|---|
| 1 | `Basalt.zip` | 196 | `basalt` | `trajectory.csv` | 27–34 | **YES** |
| 2 | `DM-VIO.zip` | 192 | `dmvio.rt` | `result.rt.csv` | 36–43 | no |
| 3 | `DM-VIO.zip` | 192 | `dmvio.scaled` | `resultScaled.txt` → `traj_dm2euroc` | 45–52 | **YES** |
| 4 | `OKVIS2.zip` | 192 | `okvis2.vio` | `tracking.vio.csv` | 54–61 | **YES** |
| 5 | `OKVIS2.zip` | 192 | `okvis2.final` | `tracking.vio.final.csv` | 63–70 | no |
| 6 | `OKVIS2-SLAM.zip` | 192 | `okvis2.slamfinal` | `tracking.slam.final.csv` | 72–79 | no |
| 7 | `OKVIS2-SLAM.zip` | 192 | `okvis2.slamfull` | `tracking.slam.full.csv` | 81–88 | no |
| 8 | `OKVIS2-SLAM.zip` | 192 | `okvis2.slam` | `tracking.slam.csv` | 90–97 | no |
| 9 | `ORB_SLAM3.zip` | 192 | `orbslam3.rt` | `rt_tracking.csv` | 99–106 | **YES** |
| 10 | `ORB_SLAM3.zip` | 192 | `orbslam3.ba` | `f_tracking.csv` | 108–116 | no |
| 11 | `Snake-SLAM.zip` | 196 | `snakeslam.rtvalid` | `trajectory.rt.valid.csv` | 118–125 | fallback only |
| 12 | `Snake-SLAM.zip` | 196 | `snakeslam.causal` | `trajectory.causal.csv` | 127–135 | **YES** |
| 13 | `Snake-SLAM.zip` | 196 | `snakeslam.rt` | `trajectory.rt.csv` | 137–145 | no (**used in v1 — corrected**) |
| 14 | `Snake-SLAM.zip` | 196 | `snakeslam.ba` | `trajectory.ba.csv` | 147–155 | no |

- Distinct executions across the six archives: **1160**
- Evaluation records across all fourteen groups: **2708**
- Records in the five analysed groups: **968**

## 2. Why five groups, stated per group

The analysed set is **one online/causal evaluation group per system family**.
Mixing causal output with post-processed or bundle-adjusted output inside one ATE
distribution would describe two different operating regimes at once, so the
selection criterion is: *the group whose trajectory artifact is the estimate the
system emits under causal operation.*

| Excluded group | Reason | Source of the reason |
|---|---|---|
| `dmvio.rt` | Not comparable under the released protocol. `result.rt.csv` carries a zero-norm quaternion in the large majority of rows (MOO16: 19,663/19,932 = 98.7%; MIO03: 80.4%; MOO01: 59.2%; MGO01: 63.9%), and it is the pre-scale trajectory: `resultScaled.txt` equals `result.txt` with the estimated metric scale applied (MOO16 median ratio 1.264). ATE is computed with `correct_scale=False`, so only the scaled artifact is metrically comparable. | direct file inspection |
| `okvis2.final` | Post-processed final estimate, not the causal VIO estimate. | `evaluate.fish` artifact name; `benchmark_table_source.py` uses `okvis2.vio` under `CAUSAL=True` |
| `okvis2.slam`, `okvis2.slamfull`, `okvis2.slamfinal` | Derived from `OKVIS2-SLAM.zip`, a **different execution configuration**: "These runs were done with all possible optimizations enabled. Representative of cases in which the tracking can be done offline." Built by applying `slam.patch` on top of commit 42438c0. | `runs/OKVIS2-SLAM/README.md` verbatim |
| `orbslam3.ba` | Bundle-adjusted (non-causal) output. Selected only by the `CAUSAL=False` branch. | `benchmark_table_source.py` lines 140–145 |
| `snakeslam.ba` | Bundle-adjusted (non-causal) output. Selected only by the `CAUSAL=False` branch. | `benchmark_table_source.py` lines 156–160 |
| `snakeslam.rt` | Raw real-time pose stream: one row per camera frame regardless of estimate validity. Coverage measures computed on it are ≈1.0 by construction and do not measure output availability. See §3. | direct file inspection + Table IV mismatch |

**A note on wording.** This population is *not* identical to "the causal branch of
the released benchmark table". That branch selects a **single run per sequence** by
an outcome-dependent rule; the present population retains **all released runs and
configuration variants** of the same groups. The two agree on *which evaluation
group* is used for every system, and differ on *which runs within it* are kept.
The manuscript must state it that way and must not use "causal benchmark branch"
as a description of the sample.

## 3. Snake-SLAM: why `causal`, established numerically

The MSD paper's Table IV *Completed frames [%]* column for Snake-SLAM was matched
against the released `success.snakeslam.*` files:

| Sequence | Table IV | `causal.det` | `rtvalid.det` | `rt.det` |
|---|---|---|---|---|
| MIO01 | 65 | **0.6484 → 65** | 0.7342 | 1.0000 → 100 |
| MIO02 | 78 | **0.7816 → 78** | 0.8187 | 1.0000 → 100 |
| MIO03 | 92 | **0.9182 → 92** | 0.9541 | 1.0000 → 100 |
| MIO04 | 15 | `null` | **0.1517 → 15** | 1.0000 → 100 |
| MIO05 | 89 | **0.8866 → 89** | 0.9209 | 1.0000 → 100 |
| MIO06 | 79 | **0.7857 → 79** | 0.8975 | 1.0000 → 100 |
| MIO07 | 84 | **0.8420 → 84** | 0.9463 | 1.0000 → 100 |

Six of seven match `snakeslam.causal.det` exactly. The seventh is `null` in
`causal` and matches `rtvalid.det`, which is precisely the documented fallback in
`benchmark_table_source.py`:

```python
CAUSAL_RUN  = "snakeslam.causal.det"
RTVALID_RUN = "snakeslam.rtvalid.det"
# Prioritize "causal" over "rtvalid" run
```

`snakeslam.rt` matches no row.

**Mechanism, confirmed on raw trajectories.** For MIO01 / resultsDET:

| Artifact | Rows | Bounding-box diagonal | Path length |
|---|---|---|---|
| `trajectory.rt.csv` | 7854 | 11.319 m | 426.11 m |
| `trajectory.rt.valid.csv` | 5767 | 4.988 m | 85.39 m |
| `trajectory.causal.csv` | 5093 | 4.985 m | 80.43 m |

5093 / 7854 = 0.6484 — identical to the released `causal` success value for
MIO01/det. The camera stream therefore has ≈7855 frames, `trajectory.rt.csv`
emits one row per frame (success ≈ 0.9999), and the causal estimate validates
5093 of them. The `rt` path length is 5.3× the causal path over the same
workspace, i.e. it contains large excursions from poses the estimator did not
validate.

**Consequence for v1.** Under `snakeslam.rt`, 184 of 187 Snake-SLAM records passed
`C ≥ 0.99 and S ≥ 0.99`. Under `snakeslam.causal`, the maximum observed success is
0.9858 and the maximum completion is 0.9916, so **zero** records pass. The v1
coverage filter was not filtering Snake-SLAM at all.

## 4. Reconciliation of the 256 / 196 discrepancy — closes `REVIEW_REQUIRED_BEFORE_LOCK`

`SOURCE_AUDIT_SUMMARY_v1.txt` reported
`BASALT_SOURCE_ARTIFACT_MATCH = REQUIRES_REVIEW` and
`SNAKESLAM_SOURCE_COVERAGE_ARTIFACT_MATCH = REQUIRES_REVIEW` because an expected
candidate count of 256 (4 variants × 64 sequences) did not match the 196
directories actually present.

**Resolution.** The `DCK` variant was executed on four sequences only, for both
Basalt and Snake-SLAM. Per `SEQUENCE_MATRIX_v1.tsv`, the `DCK` column is 1 for
exactly `MGO03`, `MIPP06`, `MOO09`, `MOO13` and 0 for the other 60 sequences, in
both the Basalt and the Snake-SLAM blocks.

    4 (DCK) + 64 (DET) + 64 (ND1) + 64 (ND2) = 196          observed = 196  ✔
    256 − 196 = 60 structural matrix cells that were never executed

**Independent confirmation from a second file.** `ate.snakeslam.causal.json`
contains non-null entries under `snakeslam.causal.dck` for exactly `MGO03`,
`MIPP06`, `MOO09`, `MOO13` and `null` for the remaining 60 — a file produced by a
different stage of the pipeline than `SEQUENCE_MATRIX_v1.tsv`.

The 60 absent cells are **structural matrix cells, not released source runs**, and
must not be counted as missing data.

    BASALT_SOURCE_ARTIFACT_MATCH               = PASS (196 = 4 + 64x3)
    SNAKESLAM_SOURCE_COVERAGE_ARTIFACT_MATCH   = PASS (196 = 4 + 64x3)
    SOURCE_POPULATION_AUDIT_STATUS             = CLOSED
