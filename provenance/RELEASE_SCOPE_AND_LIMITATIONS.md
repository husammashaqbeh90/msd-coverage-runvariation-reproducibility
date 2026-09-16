# Release scope and interpretation limits

This package is complete for the reproducibility scope of the accompanying
secondary analysis. The points below are limits on interpretation, not pending
computational tasks or unresolved validation failures.

## Scope of the released analysis

- The analysis uses one released online/causal evaluation group for each of the
  five system families, with the documented `snakeslam.rtvalid` fallback when a
  causal Snake-SLAM result is unavailable.
- No VIO or SLAM system was newly executed. The package reads only the released
  metric JSON files copied into `inputs/batch/`.
- The primary analysis is conditional on records that contain ATE, temporal
  completion, and pose-count success. Its population is 861 of 968 source
  records; 612 satisfy the joint high-coverage criterion.
- The repeated-run analysis covers the complete released triplets for ORB-SLAM3
  and OKVIS2. It does not estimate a general run-level variance distribution,
  identify a cause of variation, or compare deterministic with
  non-deterministic execution.

## Missing-metric records

The 107 source records excluded from the primary evaluable population were not
imputed: 98 are DM-VIO records without a usable scaled trajectory artifact and
9 are Snake-SLAM records with coverage but no trajectory error. The released
artifacts do not establish whether the excluded records would have met the joint
coverage condition. This bound is reported as a manuscript limitation rather
than repaired with an assumed value.

## Submission metadata outside this archive

The permanent public repository URL and archival DOI must be recorded in the
manuscript after depositing this exact archive. These identifiers are not data
or analysis inputs and are intentionally not invented in the package.
