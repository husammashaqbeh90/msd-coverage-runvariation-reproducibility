#!/usr/bin/env python3
"""
Stage 2 — all reported quantities, computed from outputs/records_primary.csv.

Deterministic: bootstrap seed fixed, replicate count fixed. Re-running from a
fresh extraction reproduces every number bit-for-bit.
"""
import json
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
OUT = os.path.join(PKG, "outputs")
BATCH = os.path.join(PKG, "inputs", "batch")

SEED = 20260821
NBOOT = 30000
THRESHOLDS = (1.0, 10.0)

# released source-run directory counts (provenance/EVALUATION_GROUP_PROVENANCE.md)
RELEASED = {"Basalt": 196, "OKVIS2": 192, "ORB-SLAM3": 192, "DM-VIO": 192, "Snake-SLAM": 196}
SYS_ORDER = ["Basalt", "OKVIS2", "ORB-SLAM3", "DM-VIO", "Snake-SLAM"]

rep = {}


def hdr(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def prop(sub, a):
    n = len(sub)
    k = int((sub.ate >= a).sum())
    return k, n, (100.0 * k / n if n else float("nan"))


def cluster_bootstrap(sub, a, seqs, nboot=NBOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    by = {s: g.ate.to_numpy() for s, g in sub.groupby("sequence")}
    keys = list(seqs)
    arr = np.empty(nboot)
    for b in range(nboot):
        idx = rng.integers(0, len(keys), len(keys))
        num = den = 0
        for i in idx:
            v = by.get(keys[i])
            if v is None:
                continue
            num += int((v >= a).sum())
            den += v.size
        arr[b] = 100.0 * num / den if den else np.nan
    arr = arr[np.isfinite(arr)]
    return float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))


# ------------------------------------------------------------------ load
d = pd.read_csv(os.path.join(OUT, "records_primary.csv"))
ev = d.dropna(subset=["ate", "completion", "success"]).copy()
SEQS = sorted(d.sequence.unique())
assert len(SEQS) == 64

# ------------------------------------------------------------------ Table 1
hdr("TABLE 1  Analysis population")
rows = []
for s in SYS_ORDER:
    n = int((ev.system == s).sum())
    rows.append([s, RELEASED[s], n, RELEASED[s] - n])
rows.append(["Total", sum(RELEASED.values()), int(len(ev)),
             sum(RELEASED.values()) - int(len(ev))])
t1 = pd.DataFrame(rows, columns=["System", "Released source records",
                                 "Evaluable records", "Records not included"])
print(t1.to_string(index=False))
t1.to_csv(os.path.join(OUT, "Table1_population.csv"), index=False)
rep["evaluable"] = int(len(ev))
rep["rte_available_among_evaluable"] = int(ev.rte.notna().sum())
print(f"\nRTE available among evaluable: {rep['rte_available_among_evaluable']}/{len(ev)}")
nfb = int((ev.source_group == "snakeslam.rtvalid").sum())
print(f"Snake-SLAM records supplied by the released rtvalid fallback: {nfb}")
rep["snakeslam_fallback_records"] = nfb

# ------------------------------------------------------------------ Table 2
hdr("TABLE 2  Trajectory error at high output coverage (C >= 0.99, S >= 0.99)")
hc = ev[(ev.completion >= 0.99) & (ev.success >= 0.99)]
t2 = [["Evaluable records before coverage restriction", len(ev)],
      ["Records with C >= 0.99 and S >= 0.99", len(hc)],
      ["Median ATE (m)", hc.ate.median()],
      ["P90 ATE (m)", np.percentile(hc.ate, 90)],
      ["P95 ATE (m)", np.percentile(hc.ate, 95)]]
for a in THRESHOLDS:
    k, n, p = prop(hc, a)
    lo, hi = cluster_bootstrap(hc, a, SEQS)
    t2 += [[f"ATE >= {a:g} m count", k], [f"ATE >= {a:g} m percent", p],
           [f"ATE >= {a:g} m bootstrap 95% low", lo],
           [f"ATE >= {a:g} m bootstrap 95% high", hi]]
    rep[f"ate_ge_{a:g}m_n"] = k
    rep[f"ate_ge_{a:g}m_pct"] = p
    rep[f"ate_ge_{a:g}m_ci"] = [lo, hi]
t2 = pd.DataFrame(t2, columns=["Measure", "Result"])
print(t2.to_string(index=False))
t2.to_csv(os.path.join(OUT, "Table2_primary_high_coverage.csv"), index=False)
rep["primary_high_coverage"] = int(len(hc))
rep["median_ate"] = float(hc.ate.median())
rep["p90_ate"] = float(np.percentile(hc.ate, 90))
rep["p95_ate"] = float(np.percentile(hc.ate, 95))

print("\nComposition of the eligible subset:")
comp = []
for s in SYS_ORDER:
    g = hc[hc.system == s]
    comp.append([s, len(g), int((g.ate >= 1).sum()), int((g.ate >= 10).sum()),
                 g.ate.median() if len(g) else np.nan])
comp = pd.DataFrame(comp, columns=["System", "n", "ATE>=1m", "ATE>=10m", "median ATE"])
print(comp.to_string(index=False))
comp.to_csv(os.path.join(OUT, "Supplement_system_stratification.csv"), index=False)

# ------------------------------------------------------------------ benchmark-selected
def select_run(sub_runs, seq, metrics):
    """Faithful port of select_run in benchmark_table_source.py (lines 59-87)."""
    def g(metric, run):
        v = metrics[metric].get((run, seq))
        return v
    succ = {r: g("success", r) for r in sub_runs}
    real = {r: v for r, v in succ.items() if v is not None}
    if not real:
        return sub_runs[0]
    mx = max(real.values())
    cand = [r for r in sub_runs if succ[r] == mx]
    if len(cand) == 1:
        return cand[0]
    ates = {r: (g("ate", r) if g("ate", r) is not None else np.inf) for r in cand}
    mn = min(ates.values())
    cand2 = [r for r in cand if ates[r] == mn]
    if len(cand2) == 1:
        return cand2[0]
    rtes = {r: (g("rte", r) if g("rte", r) is not None else np.inf) for r in cand2}
    mn2 = min(rtes.values())
    cand3 = [r for r in cand2 if rtes[r] == mn2]
    return cand3[0]


lut = {m: {(r.run_name, r.sequence): getattr(r, m) if pd.notna(getattr(r, m)) else None
           for r in d.itertuples()} for m in ("ate", "rte", "success", "completion")}

bench = []
for seq in SEQS:
    picks = [("Basalt", "basalt.det")]
    for sysname, runs in (("OKVIS2", [f"okvis2.vio.{i}" for i in (1, 2, 3)]),
                          ("ORB-SLAM3", [f"orbslam3.rt.{i}" for i in (1, 2, 3)]),
                          ("DM-VIO", [f"dmvio.scaled.{i}" for i in (1, 2, 3)])):
        picks.append((sysname, select_run(runs, seq, lut)))
    # Snake-SLAM: causal.det, else rtvalid.det (benchmark_table_source.py 156-178)
    snake = "snakeslam.causal.det"
    if lut["completion"].get((snake, seq)) is None:
        snake = "snakeslam.rtvalid.det"
    picks.append(("Snake-SLAM", snake))
    for sysname, run in picks:
        row = d[(d.run_name == run) & (d.sequence == seq)]
        if len(row):
            bench.append(row.iloc[0])
bench = pd.DataFrame(bench)
bench_ev = bench.dropna(subset=["ate", "completion", "success"])
bench.to_csv(os.path.join(OUT, "Supplement_benchmark_selected_population.csv"), index=False)

# ------------------------------------------------------------------ Table 3
hdr("TABLE 3  Sensitivity")
sens = []


def add(label, sub, basis=None):
    k1, n, p1 = prop(sub, 1)
    k10, _, p10 = prop(sub, 10)
    nsk = int((sub.system == "Snake-SLAM").sum())
    sens.append([label, basis or f"{n} records", round(p1, 4), round(p10, 4), k1, k10, nsk])
    print(f"  {label:38s} {('n=%d' % n):>12s}  >=1m {k1:3d} ({p1:6.3f}%)  "
          f">=10m {k10:3d} ({p10:6.3f}%)  [Snake n={nsk}]")


for t in (0.95, 0.99, 0.999):
    lbl = "Primary: joint coverage, tau = 0.99" if t == 0.99 else f"Joint coverage, tau = {t}"
    add(lbl, ev[(ev.completion >= t) & (ev.success >= t)])
add("Exact C = S = 1.0", ev[(ev.completion == 1.0) & (ev.success == 1.0)])
add("Completion only, C >= 0.99", ev[ev.completion >= 0.99])

eqw = {}
for a in THRESHOLDS:
    per = hc.groupby("sequence").apply(lambda g: (g.ate >= a).mean(), include_groups=False)
    eqw[a] = 100.0 * per.mean()
sens.append(["Equal sequence weighting", "64 sequences", round(eqw[1], 4),
             round(eqw[10], 4), "", "", ""])
print(f"  {'Equal sequence weighting':38s} {'64 seq':>12s}  >=1m {eqw[1]:6.3f}%   "
      f">=10m {eqw[10]:6.3f}%")
rep["equal_sequence_weighted"] = {"ge1m": eqw[1], "ge10m": eqw[10]}


def eqw_bootstrap(sub, a, seqs, nboot=NBOOT, seed=SEED):
    """Sequence-cluster bootstrap of the equal-sequence-weighted proportion."""
    rng = np.random.default_rng(seed)
    per = {s: float((g.ate >= a).mean()) for s, g in sub.groupby("sequence")}
    keys = [s for s in seqs if s in per]
    vals = np.array([per[s] for s in keys])
    out = np.empty(nboot)
    for b in range(nboot):
        out[b] = 100.0 * vals[rng.integers(0, vals.size, vals.size)].mean()
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


for a in THRESHOLDS:
    lo, hi = eqw_bootstrap(hc, a, SEQS)
    rep[f"eqw_ci_{a:g}"] = [lo, hi]
    print(f"  equal-sequence-weighted bootstrap 95% CI, ATE>={a:g}m : [{lo:.4f}, {hi:.4f}]")

bhc = bench_ev[(bench_ev.completion >= 0.99) & (bench_ev.success >= 0.99)]
bex = bench_ev[(bench_ev.completion == 1.0) & (bench_ev.success == 1.0)]
print(f"  benchmark-selected evaluable records: {len(bench_ev)}")
add("Benchmark-selected, C,S >= 0.99", bhc)
add("Benchmark-selected, C = S = 1.0", bex)
rep["benchmark_selected_evaluable"] = int(len(bench_ev))
rep["benchmark_selected_high_coverage"] = int(len(bhc))

# leave-one-system-out. A system that contributes no record to the high-coverage
# subset cannot change the estimate or its denominator, so the reported range is
# taken over the informative removals only and the non-contributing systems are
# named explicitly instead of being folded into the range.
contrib = {s: int((hc.system == s).sum()) for s in SYS_ORDER}
informative = [s for s in SYS_ORDER if contrib[s] > 0]
inert = [s for s in SYS_ORDER if contrib[s] == 0]

l1, l10, bases, loo = [], [], [], []
for s in SYS_ORDER:
    sub = hc[hc.system != s]
    _, n, p1 = prop(sub, 1)
    _, _, p10 = prop(sub, 10)
    loo.append([f"drop {s}", contrib[s], n, round(p1, 4), round(p10, 4),
                "informative" if contrib[s] else "no effect (contributes 0 records)"])
    if contrib[s]:
        l1.append(p1); l10.append(p10); bases.append(n)
    print(f"     drop {s:11s} contributes {contrib[s]:4d}  n={n:4d}  "
          f">=1m {p1:6.3f}%  >=10m {p10:6.3f}%"
          f"{'' if contrib[s] else '   <- leaves the subset unchanged'}")

sens.append([f"Leave-one-system-out ({len(informative)} informative removals)",
             f"{min(bases)}-{max(bases)} records",
             f"{min(l1):.2f}-{max(l1):.2f}", f"{min(l10):.2f}-{max(l10):.2f}", "", "", ""])
if inert:
    _, n0, p1_0 = prop(hc, 1)
    _, _, p10_0 = prop(hc, 10)
    sens.append([f"  note: removing {', '.join(inert)} leaves the subset unchanged",
                 f"{n0} records", round(p1_0, 4), round(p10_0, 4), "", "", ""])
pd.DataFrame(loo, columns=["Analysis", "Records contributed to subset", "n after removal",
                           "ATE>=1m (%)", "ATE>=10m (%)", "Status"]).to_csv(
    os.path.join(OUT, "Supplement_leave_one_system_out.csv"), index=False)
rep["loo_informative_range"] = {"ge1m": [min(l1), max(l1)], "ge10m": [min(l10), max(l10)],
                                "basis": [min(bases), max(bases)],
                                "non_contributing": inert}

t3 = pd.DataFrame(sens, columns=["Analysis", "Eligible basis", "ATE>=1m (%)",
                                 "ATE>=10m (%)", "n>=1m", "n>=10m", "Snake-SLAM n"])
t3.to_csv(os.path.join(OUT, "Table3_sensitivity.csv"), index=False)

# ------------------------------------------------------------------ Table 4
hdr("TABLE 4  Run-to-run variation (ORB-SLAM3 real-time, OKVIS2 causal VIO)")
t4, trip_detail = [], []
for pref, lab in (("orbslam3.rt", "ORB-SLAM3"), ("okvis2.vio", "OKVIS2")):
    s = ev[ev.run_name.str.startswith(pref)]
    recs = []
    for seq, g in s.groupby("sequence"):
        if len(g) != 3:
            continue
        if not ((g.completion >= 0.99) & (g.success >= 0.99)).all():
            continue
        g = g.sort_values("run_name")
        a = g.ate.to_numpy(); r = g.rte.to_numpy()
        recs.append(dict(system=lab, sequence=seq,
                         ate_run1=a[0], ate_run2=a[1], ate_run3=a[2],
                         ate_min=a.min(), ate_max=a.max(),
                         ate_ratio=a.max() / a.min(), rte_ratio=r.max() / r.min(),
                         cross1=bool(a.min() < 1 <= a.max()),
                         cross10=bool(a.min() < 10 <= a.max()),
                         ratio_ge2=bool(a.max() / a.min() >= 2),
                         ratio_ge10=bool(a.max() / a.min() >= 10)))
    df = pd.DataFrame(recs)
    trip_detail.append(df)
    t4.append([lab, 64, len(df), df.ate_ratio.median(), np.percentile(df.ate_ratio, 90),
               df.rte_ratio.median(), np.percentile(df.rte_ratio, 90),
               int(df.cross1.sum()), 100 * df.cross1.mean(),
               int(df.cross10.sum()), 100 * df.cross10.mean(),
               int(df.ratio_ge2.sum()), int(df.ratio_ge10.sum())])
t4 = pd.DataFrame(t4, columns=["System", "Sequences with 3 released runs",
                               "All 3 runs high coverage", "Median ATE max/min",
                               "P90 ATE max/min", "Median RTE max/min", "P90 RTE max/min",
                               "Crossed 1m n", "Crossed 1m percent",
                               "Crossed 10m n", "Crossed 10m percent",
                               "Ratio >= 2x n", "Ratio >= 10x n"])
print(t4.to_string(index=False))
t4.to_csv(os.path.join(OUT, "Table4_repeated_run.csv"), index=False)
pd.concat(trip_detail).to_csv(os.path.join(OUT, "Supplement_repeated_triplet_details.csv"),
                              index=False)
rep["orb_triplets"] = int(t4.loc[0, "All 3 runs high coverage"])
rep["okvis_triplets"] = int(t4.loc[1, "All 3 runs high coverage"])

# exact-coverage repeated-run subset
hdr("Repeated-run, exact C = S = 1.0 in all three executions")
for pref, lab in (("orbslam3.rt", "ORB-SLAM3"), ("okvis2.vio", "OKVIS2")):
    s = ev[ev.run_name.str.startswith(pref)]
    n = c1 = c10 = 0
    for seq, g in s.groupby("sequence"):
        if len(g) != 3 or not ((g.completion == 1.0) & (g.success == 1.0)).all():
            continue
        a = g.ate.to_numpy(); n += 1
        c1 += a.min() < 1 <= a.max(); c10 += a.min() < 10 <= a.max()
    print(f"  {lab:11s} triplets={n:3d}  crossed 1m={c1}  crossed 10m={c10}")
    rep[f"exact_triplets_{lab}"] = [n, int(c1), int(c10)]

json.dump(rep, open(os.path.join(OUT, "analysis_report.json"), "w"), indent=2)
print("\nwrote outputs/*.csv and outputs/analysis_report.json")
