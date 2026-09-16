# Historical manuscript changes, v1 → corrected v3 analysis

Base file `v1_original.docx`
sha256 `de2bb3731f4959f7ae46534ed824b340d5de7ccaae46a7c72f3c64c2484a5a51` — preserved unchanged.

**Not touched:** Equations 1–9 (all nine OMML objects are byte-identical to v1),
reference list, section structure, styles, headers, footers. Paragraph count is
unchanged (323 → 323) and the document validates against the original.

## Numbers

Every figure below comes from `outputs/`; none was typed by hand.

| Location | v1 | corrected v3 analysis |
|---|---|---|
| Abstract, Table 2, §4.1, §5.1, §6 — high-coverage subset | 796 | **612** |
| ATE ≥ 1 m | 95 (11.9%) | **66 (10.8%)** |
| ATE ≥ 10 m | 39 (4.9%) | **32 (5.2%)** |
| bootstrap CI, 1 m | 8.2–16.1% | **6.7–15.3%** |
| bootstrap CI, 10 m | 2.8–7.3% | **2.8–8.0%** |
| median / P90 / P95 ATE | 0.222 / 1.10 / 8.79 m | **0.167 / 1.12 / 19.00 m** |
| τ = 0.95 | 831; 14.1% / 6.6% | **675; 13.0% / 7.1%** |
| τ = 0.999 | 724; 10.1% / 3.9% | **543; 8.1% / 3.9%** |
| exact C = S = 1.0 | 477; 11.5% / 5.2% | **387; 9.0% / 4.9%** |
| completion only | 812; 13.2% / 5.8% | **631; 12.4% / 6.3%** |
| equal-sequence weighting | 11.51% / 4.72% | **10.20% / 4.93%** |
| equal-sequence bootstrap CIs | 7.78–15.61% / 2.62–7.11% | **6.29–14.59% / 2.61–7.68%** |
| leave-one-system-out | 600–755 records; 9.67–14.67% / 3.61–6.17% | **416–571 records (four informative removals); 7.71–14.18% / 3.52–7.21%** |
| benchmark-selected rows | 211 / 130; 10.4%, 4.7%, 6.9%, 3.1% | **unchanged** (v1 already used the causal group here) |
| Table 4, repeated-run | — | **unchanged** |

## Text

- **§3.1** — new opening paragraph: fourteen evaluation groups derived from six source
  archives, the five analysed, the Snake-SLAM causal group with its released
  rtvalid fallback, and why post-processed, bundle-adjusted and offline groups are
  excluded. The sample is *not* described as "the causal branch of the released
  benchmark table"; that branch selects one run per sequence by an outcome-dependent
  rule, whereas this population keeps all runs and variants.
- **§3.1** — the 107 excluded records are split into their three causes
  (80 / 18 / 9) instead of being presented as one category.
- **Table 1 note** — Snake-SLAM's 187 stated as 173 causal + 14 released fallback.
- **§4.1** — per-system composition of the eligible subset added, including that
  Snake-SLAM contributes no record because its causal output does not reach
  C ≥ 0.99 and S ≥ 0.99 on any of the 64 sequences.
- **§4.2 and Table 3 note** — leave-one-system-out reported over the four
  informative removals, with an explicit statement that removing Snake-SLAM leaves
  the denominator (612) and both proportions unchanged.
- **§4.3** — max-to-min ratio counts added (ORB-SLAM3: 21 of 59 triplets ≥ 2×,
  6 ≥ 10×; OKVIS2: 1 and 1), so threshold crossing is not the only spread summary.
- **§5.1** — one sentence separating what is analytic (coverage carries no accuracy
  information) from what is measured (the size of the remaining tail).
- **§5.3** — reporting recommendation extended: the evaluation group belongs in the
  report, because the same executions can yield several groups.
- **§5.4** — limitation 1 extended to state that results are conditional on the
  chosen evaluation group; limitation 2 rewritten to give the three exclusion
  categories and to state explicitly that the direction of any resulting difference
  is **not** determined, since the excluded records have no coverage values.
- **Figure captions 1–3** rewritten to match the regenerated figures.

## Deliberately not done

- **Literature-screening counts are not in Related Work.** The evidence matrix
  (166 combined unique records → 23 shortlisted → 37 in the matrix) was used to keep
  the gap claim bounded and to prevent unsupported novelty claims. The manuscript is
  not a systematic review, so Related Work stays concept-centred and reports no
  screening arithmetic.
- **Equations 4 and 7 are unchanged.** The earlier report that their delimiters were
  broken came from `pdftotext`, which renders the norm glyph `∥` as `)`. The OMML is
  correct. Nothing was edited.
