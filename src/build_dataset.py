#!/usr/bin/env python3
"""
Stage 1 — build the flat record table directly from the released metric JSONs.

No intermediate table from any earlier package version is used. Every value in
the output originates from inputs/batch/{ate,rte,success,completion}.<group>.json.

Metric-file convention (verified against xrtslam-metrics batch.py line 391,
`np.array([s["rmse"], s["std"]])`):
    ate/rte  -> [rmse, std] pair, or null
    success/completion -> scalar, or null
Element 0 (the RMSE) is the analysed value.

Snake-SLAM variant rule
-----------------------
The released MSD benchmark table (benchmark_table_source.py, CAUSAL=True branch)
uses `snakeslam.causal` and falls back to `snakeslam.rtvalid` where the causal
result is unavailable. The primary population retains all four determinism
variants (dck/det/nd1/nd2) rather than the single deterministic run the table
selects, so the fallback is applied per (variant, sequence):

    causal[v][s] if available else rtvalid[v][s]

A causal-only table is also emitted so the effect of the fallback is auditable.
"""
import json
import os
import sys
import csv

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
BATCH = os.path.join(PKG, "inputs", "batch")
OUT = os.path.join(PKG, "outputs")

SEQUENCES = ["MIO01","MIO02","MIO03","MIO04","MIO05","MIO06","MIO07","MIO08","MIO09","MIO10","MIO11","MIO12","MIO13","MIO14","MIO15","MIO16","MIPB01","MIPB02","MIPB03","MIPB04","MIPB05","MIPB06","MIPB07","MIPB08","MIPP01","MIPP02","MIPP03","MIPP04","MIPP05","MIPP06","MIPT01","MIPT02","MIPT03","MGO01","MGO02","MGO03","MGO04","MGO05","MGO06","MGO07","MGO08","MGO09","MGO10","MGO11","MGO12","MGO13","MGO14","MGO15","MOO01","MOO02","MOO03","MOO04","MOO05","MOO06","MOO07","MOO08","MOO09","MOO10","MOO11","MOO12","MOO13","MOO14","MOO15","MOO16"]  # fmt: skip
assert len(set(SEQUENCES)) == 64

# analysed group -> (system label, released source-run count)
ANALYSED = {
    "basalt":            ("Basalt",     196),
    "okvis2.vio":        ("OKVIS2",     192),
    "orbslam3.rt":       ("ORB-SLAM3",  192),
    "dmvio.scaled":      ("DM-VIO",     192),
    "snakeslam.causal":  ("Snake-SLAM",  196),   # + rtvalid fallback
}
SNAKE_FALLBACK = "snakeslam.rtvalid"


def load(metric, group):
    p = os.path.join(BATCH, f"{metric}.{group}.json")
    with open(p, encoding="utf-8") as f:
        return json.load(f)[metric]


def scalar(v):
    """ate/rte -> element 0 (RMSE); success/completion -> the scalar itself."""
    if v is None:
        return None
    if isinstance(v, list):
        return v[0]
    return v


def group_records(group, system, fallback_group=None):
    met = {m: load(m, group) for m in ("ate", "rte", "success", "completion")}
    fb = None
    if fallback_group:
        fb = {m: load(m, fallback_group) for m in ("ate", "rte", "success", "completion")}

    runs = sorted(met["ate"].keys())
    rows = []
    for run in runs:
        variant = run.split(".")[-1]
        fb_run = f"{fallback_group}.{variant}" if fallback_group else None
        for seq in SEQUENCES:
            vals, src = {}, group
            for m in ("ate", "rte", "success", "completion"):
                vals[m] = scalar(met[m][run].get(seq))
            # released fallback: causal unavailable -> rtvalid
            if fb is not None and vals["ate"] is None and vals["completion"] is None \
               and vals["success"] is None:
                fbv = {m: scalar(fb[m][fb_run].get(seq)) for m in
                       ("ate", "rte", "success", "completion")}
                if any(v is not None for v in fbv.values()):
                    vals, src = fbv, fallback_group
            if all(v is None for v in vals.values()):
                continue          # matrix cell never executed
            rows.append(dict(system=system, group=group, source_group=src,
                             run_name=run, variant=variant, sequence=seq,
                             ate=vals["ate"], rte=vals["rte"],
                             success=vals["success"], completion=vals["completion"]))
    return rows


def write(path, rows):
    cols = ["system", "group", "source_group", "run_name", "variant", "sequence",
            "ate", "rte", "success", "completion"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    os.makedirs(OUT, exist_ok=True)

    primary, causal_only = [], []
    for g, (sysname, _) in ANALYSED.items():
        fb = SNAKE_FALLBACK if g == "snakeslam.causal" else None
        primary += group_records(g, sysname, fallback_group=fb)
        causal_only += group_records(g, sysname, fallback_group=None)

    write(os.path.join(OUT, "records_primary.csv"), primary)
    write(os.path.join(OUT, "records_causal_only.csv"), causal_only)

    # the two comparison populations (not analysed; built for the audit)
    for g, sysname in (("snakeslam.rt", "Snake-SLAM"), ("dmvio.rt", "DM-VIO")):
        write(os.path.join(OUT, f"records_{g.replace('.','_')}.csv"),
              group_records(g, sysname))

    print(f"records_primary.csv      : {len(primary)} rows")
    print(f"records_causal_only.csv  : {len(causal_only)} rows")
    fb_rows = sum(1 for r in primary if r["source_group"] == SNAKE_FALLBACK)
    print(f"Snake-SLAM rows taken from rtvalid fallback : {fb_rows}")


if __name__ == "__main__":
    main()
