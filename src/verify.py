#!/usr/bin/env python3
"""
Stage 3 — independent verification.

(a) Reconstructs the released MSD benchmark table (Table IV) selection and checks
    it against the published values for the rows that are legible in the paper.
    This is the external check that the analysed Snake-SLAM group is the one the
    released benchmark actually used.
(b) Structural checks on the built record table.

Exit code is non-zero if any check fails.
"""
import os
import sys
import numpy as np
import pandas as pd

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PKG, "outputs")

fail = []


def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}{('  ' + detail) if detail else ''}")
    if not ok:
        fail.append(name)


d = pd.read_csv(os.path.join(OUT, "records_primary.csv"))
bench = pd.read_csv(os.path.join(OUT, "Supplement_benchmark_selected_population.csv"))
provenance = pd.read_csv(
    os.path.join(OUT, "Supplement_evaluation_group_provenance.tsv"), sep="\t"
)

print("A. Published Table IV cross-check (MSD paper, Systems evaluation)")
# published values legible in the paper for MIO01-MIO07
PUB = {
    #        Basalt  OKVIS2  ORB     DM-VIO  Snake   -> ATE [cm]; None = x / inf
    "MIO01": dict(ate={"Basalt": 62.0, "OKVIS2": 50.4, "Snake-SLAM": 49.7}, succ={"Snake-SLAM": 65}),
    "MIO02": dict(ate={"Basalt": 117.7, "OKVIS2": 172.5, "ORB-SLAM3": 62.9, "Snake-SLAM": 92.2}, succ={"Snake-SLAM": 78}),
    "MIO03": dict(ate={"Basalt": 9.5, "OKVIS2": 6.4, "ORB-SLAM3": 12.0, "Snake-SLAM": 22.3}, succ={"Snake-SLAM": 92}),
    "MIO04": dict(ate={"Basalt": 20.6, "OKVIS2": 18.7, "ORB-SLAM3": 257.5, "Snake-SLAM": 77.6}, succ={"Snake-SLAM": 15}),
    "MIO05": dict(ate={"Basalt": 3.4, "OKVIS2": 3.9, "ORB-SLAM3": 26.6, "Snake-SLAM": 20.0}, succ={"Snake-SLAM": 89}),
    "MIO06": dict(ate={"Basalt": 4.9, "OKVIS2": 27.5, "ORB-SLAM3": 69.2, "Snake-SLAM": 20.7}, succ={"Snake-SLAM": 79}),
    "MIO07": dict(ate={"Basalt": 2.3, "OKVIS2": 3.1, "ORB-SLAM3": 10.8, "Snake-SLAM": 50.5}, succ={"Snake-SLAM": 84}),
}
nate = nsucc = 0
for seq, spec in PUB.items():
    sub = bench[bench.sequence == seq]
    for sysname, want in spec["ate"].items():
        got = sub[sub.system == sysname]
        ok = len(got) == 1 and abs(round(got.iloc[0].ate * 100, 1) - want) < 0.15
        nate += 1
        check(f"{seq} {sysname} ATE = {want} cm", ok,
              f"got {round(got.iloc[0].ate*100,1) if len(got) else 'missing'}")
    for sysname, want in spec["succ"].items():
        got = sub[sub.system == sysname]
        ok = len(got) == 1 and abs(round(got.iloc[0].success * 100) - want) < 1
        nsucc += 1
        check(f"{seq} {sysname} completed frames = {want}%", ok,
              f"got {round(got.iloc[0].success*100) if len(got) else 'missing'}")
print(f"  ({nate} ATE cells and {nsucc} completed-frame cells checked)")

print("\nB. Structural checks")
check("64 distinct sequences", d.sequence.nunique() == 64)
check("861 records with metrics", len(d) == 861, f"got {len(d)}")
check("no row missing ATE while having C and S",
      len(d[(d.ate.isna()) & d.completion.notna() & d.success.notna()]) == 0)
check("RTE present for every evaluable record",
      d.dropna(subset=["ate", "completion", "success"]).rte.notna().all())
check("Snake-SLAM fallback rows are sourced from rtvalid",
      set(d[d.source_group == "snakeslam.rtvalid"].system) == {"Snake-SLAM"})
check("no Snake-SLAM record reaches S >= 0.99",
      (d[d.system == "Snake-SLAM"].success.max() < 0.99),
      f"max S = {d[d.system=='Snake-SLAM'].success.max():.6f}")
check("Basalt/Snake DCK variant present on exactly 4 sequences",
      sorted(d[(d.variant == 'dck') & (d.system == 'Basalt')].sequence.tolist())
      == ["MGO03", "MIPP06", "MOO09", "MOO13"])
bcomp = bench.groupby("system").size().to_dict()
check("benchmark-selected: Basalt, OKVIS2, ORB-SLAM3 contribute all 64 sequences",
      all(bcomp.get(s) == 64 for s in ("Basalt", "OKVIS2", "ORB-SLAM3")), str(bcomp))
check("benchmark-selected: DM-VIO contributes 41 (sequences whose selected run "
      "produced resultScaled.txt)", bcomp.get("DM-VIO") == 41, f"got {bcomp.get('DM-VIO')}")
snake_missing = sorted(set(d.sequence.unique()) -
                       set(bench[bench.system == "Snake-SLAM"].sequence))
check("benchmark-selected: Snake-SLAM contributes 61; the 3 absent sequences are "
      "MGO08/MIO10/MIO11 (no causal and no rtvalid trajectory error)",
      bcomp.get("Snake-SLAM") == 61 and snake_missing == ["MGO08", "MIO10", "MIO11"],
      f"got {bcomp.get('Snake-SLAM')}, missing {snake_missing}")
check("benchmark-selected population size = 64*3 + 41 + 61 = 294",
      len(bench) == 294, f"got {len(bench)}")
check("Supplementary Table S5 contains fourteen evaluation groups",
      len(provenance) == 14, f"got {len(provenance)}")
check("Supplementary Table S5 contains six source archives",
      provenance.source_archive.nunique() == 6,
      f"got {provenance.source_archive.nunique()}")
analysed = provenance[provenance.status_in_this_study == "Analyzed"]
check("Supplementary Table S5 identifies the five analysed groups and 968 source records",
      len(analysed) == 5 and int(analysed.runs.sum()) == 968,
      f"groups={len(analysed)}, records={int(analysed.runs.sum())}")
check("Supplementary Table S5 identifies one released fallback group",
      int((provenance.status_in_this_study == "Fallback only").sum()) == 1)

print("\nC. Comparison-group sanity (not analysed)")
rt = pd.read_csv(os.path.join(OUT, "records_snakeslam_rt.csv"))
check("snakeslam.rt reports S >= 0.99 for the large majority",
      (rt.success >= 0.99).mean() > 0.95,
      f"{(rt.success>=0.99).sum()}/{len(rt)}")

print("\n" + ("ALL CHECKS PASSED" if not fail else f"{len(fail)} CHECK(S) FAILED: {fail}"))
sys.exit(1 if fail else 0)
