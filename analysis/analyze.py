#!/usr/bin/env python3
"""LadyBird-DebrisDetector analysis: runs the pre-registered analysis plan in docs/PROTOCOL.md (section 9).

Usage:
    python3 analysis/analyze.py                 # reads data/visits.csv, prints a report
    python3 analysis/analyze.py path/to.csv     # reads another file
    python3 analysis/analyze.py --out analysis/results.md

Uses only the Python standard library (3.8+), so it runs anywhere without installs.
Wind components are recomputed from each visit's raw direction, speed and facing angle,
so the results do not depend on the logger's stored values.
"""

import argparse
import csv
import math
import random
import statistics
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = ROOT / "data" / "visits.csv"
ARCHIVE = ROOT / "data" / "weather" / "katt_hourly.csv"

# Decision criteria from PROTOCOL.md section 9
MIN_VISITS = 20
MIN_PER_CLASS = 5
RHO_THRESHOLD = 0.4
CLASS_GAP = 1.5
MIN_FRONTS = 2
PERMUTATIONS = 10_000
CLASSES = ["loading", "clearing", "alongshore", "calm"]


def onshore(from_deg, mph, face):
    if from_deg is None:  # calm: no prevailing direction, so no push into the pocket
        return 0.0
    return mph * math.cos(math.radians(from_deg - face))


def alongshore(from_deg, mph, face):
    shore = (face + 90) % 360
    return mph * math.cos(math.radians((from_deg + 180) - shore))


def wind_class(from_deg, mph, face):
    if from_deg is None or mph < 3:
        return "calm"
    on = onshore(from_deg, mph, face)
    if on >= 4:
        return "loading"
    if on <= -4:
        return "clearing"
    return "alongshore"


def to_bool(value):
    return str(value).strip().lower() in {"true", "1", "yes"}


def load(path):
    visits = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                v = {
                    "visit_id": row["visit_id"],
                    "observed_at": datetime.fromisoformat(row["observed_at"]),
                    "rating": int(row["rating"]),
                    # blank direction = calm, recorded without a direction (protocol 1.1)
                    "wind_from_deg": float(row["wind_from_deg"]) if row["wind_from_deg"].strip() else None,
                    "wind_speed_mph": float(row["wind_speed_mph"] or 0),
                    "face_deg": float(row.get("face_deg") or 50),
                    "rain_48h": (row.get("rain_48h") or "").strip() or "unknown",
                    "river_current": (row.get("river_current") or "").strip() or "unknown",
                    "deviation": to_bool(row.get("deviation", "")),
                    "days_since_cleaned": (
                        float(row["days_since_cleaned"]) if row.get("days_since_cleaned") else None
                    ),
                    "window": int(float(row["wind_window_hours"])) if row.get("wind_window_hours") else None,
                }
            except (KeyError, ValueError) as err:
                print(f"Skipping row {row.get('visit_id', '?')}: {err}", file=sys.stderr)
                continue
            if not 1 <= v["rating"] <= 5:
                print(f"Skipping row {v['visit_id']}: rating out of range", file=sys.stderr)
                continue
            v["onshore"] = onshore(v["wind_from_deg"], v["wind_speed_mph"], v["face_deg"])
            v["class"] = wind_class(v["wind_from_deg"], v["wind_speed_mph"], v["face_deg"])
            visits.append(v)
    visits.sort(key=lambda v: v["observed_at"])
    return visits


def ranks(values):
    """Average ranks, 1-based, with ties sharing the mean rank."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    result = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        mean_rank = (i + j) / 2 + 1
        for k in range(i, j + 1):
            result[order[k]] = mean_rank
        i = j + 1
    return result


def pearson(x, y):
    mx, my = statistics.fmean(x), statistics.fmean(y)
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def spearman(x, y, permutations=PERMUTATIONS, seed=20261108):
    """Spearman rho and a two-sided permutation p-value."""
    if len(x) < 3:
        return None, None
    rx, ry = ranks(x), ranks(y)
    rho = pearson(rx, ry)
    if rho is None:
        return None, None
    rng = random.Random(seed)
    shuffled = ry[:]
    extreme = 0
    for _ in range(permutations):
        rng.shuffle(shuffled)
        r = pearson(rx, shuffled)
        if r is not None and abs(r) >= abs(rho) - 1e-12:
            extreme += 1
    return rho, (extreme + 1) / (permutations + 1)


def class_means(visits):
    out = {}
    for c in CLASSES:
        ratings = [v["rating"] for v in visits if v["class"] == c]
        out[c] = (len(ratings), statistics.fmean(ratings) if ratings else None)
    return out


def frontal_pairs(visits, max_gap_days=3):
    """Consecutive visits where the wind swung from southerly to northerly within max_gap_days.

    Southerly: wind from 90-270 degrees. Northerly: wind from 270-360 or 0-90 degrees.
    This is a heuristic stand-in for a cold-front passage; confirm each pair against
    the weather record and note confirmed fronts in the visit notes.
    """
    pairs = []
    for a, b in zip(visits, visits[1:]):
        if a["wind_from_deg"] is None or b["wind_from_deg"] is None:
            continue  # a calm visit has no direction to compare
        gap = (b["observed_at"] - a["observed_at"]).total_seconds() / 86400
        southerly = 90 < a["wind_from_deg"] < 270
        northerly = b["wind_from_deg"] >= 270 or b["wind_from_deg"] <= 90
        if 0 < gap <= max_gap_days and southerly and northerly:
            pairs.append((a, b, b["rating"] - a["rating"]))
    return pairs


def fmt(x, digits=2):
    return "–" if x is None else f"{x:.{digits}f}"


def analyse(visits, label):
    lines = [f"### {label}", ""]
    n = len(visits)
    lines.append(f"Visits analysed: **{n}**")
    lines.append("")

    means = class_means(visits)
    lines += ["| Wind class | Visits | Mean rating |", "|---|---:|---:|"]
    for c in CLASSES:
        count, mean = means[c]
        lines.append(f"| {c} | {count} | {fmt(mean)} |")
    lines.append("")

    rho, p = spearman([v["onshore"] for v in visits], [v["rating"] for v in visits])
    lines.append(f"Spearman ρ (onshore wind vs rating): **{fmt(rho)}**, permutation p = {fmt(p, 4)}")
    lines.append("")
    return {"n": n, "means": means, "rho": rho, "p": p, "lines": lines}


def load_archive(path=None):
    """Hourly Camp Mabry observations saved by analysis/fetch_weather.py, keyed by local time."""
    path = path or ARCHIVE
    if not path.exists():
        return []
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                rows.append((
                    datetime.fromisoformat(r["valid_local"]),
                    float(r["wind_from_deg"]) if r["wind_from_deg"] else None,
                    float(r["wind_speed_mph"]) if r["wind_speed_mph"] else None,
                ))
            except (KeyError, ValueError):
                continue
    return rows


def archived_wind(archive, end, hours):
    """Mean speed (calm = 0) and speed-weighted mean direction over the window, as the logger computes it."""
    start = end - timedelta(hours=hours)
    obs = [(d, s) for t, d, s in archive if start < t <= end and s is not None]
    covered_hours = len({t.replace(minute=0) for t, _, s in archive if start < t <= end and s is not None})
    if covered_hours < hours * 0.5:
        return None
    speed = statistics.fmean(s for _, s in obs)
    x = sum(math.sin(math.radians(d)) * s for d, s in obs if d is not None)
    y = sum(math.cos(math.radians(d)) * s for d, s in obs if d is not None)
    direction = (math.degrees(math.atan2(x, y)) + 360) % 360 if (x or y) else None
    return direction, speed


def wind_cross_check(visits):
    """Compare the wind entered at each visit with the archived hourly record (protocol 1.2).

    The primary analysis keeps using the entered values, as pre-registered; this section shows
    whether they agree with the raw observations, so a reader can judge the inputs.
    """
    out = ["## Wind cross-check against the archive", ""]
    archive = load_archive()
    if not archive:
        out += ["No archived wind data yet. The daily GitHub Action fills `data/weather/katt_hourly.csv`.", ""]
        return out
    rows, agree, diffs = [], 0, []
    for v in visits:
        hours = v.get("window") or 24
        got = archived_wind(archive, v["observed_at"], hours)
        if got is None:
            rows.append(f"| {v['visit_id']} | {v['class']} | – | {v['onshore']:.1f} | – | not enough archived hours |")
            continue
        direction, speed = got
        a_on = onshore(direction, speed, v["face_deg"])
        a_class = wind_class(direction, speed, v["face_deg"])
        agree += a_class == v["class"]
        diffs.append(abs(a_on - v["onshore"]))
        rows.append(f"| {v['visit_id']} | {v['class']} | {a_class} | {v['onshore']:.1f} | {a_on:.1f} | {hours} h |")
    checked = len(diffs)
    if checked:
        out.append(f"Wind class matched the archive on **{agree} of {checked}** visits; "
                   f"onshore wind differed by {statistics.fmean(diffs):.1f} mph on average.")
        out.append("")
    out += ["| Visit | Entered class | Archive class | Entered onshore mph | Archive onshore mph | Window |",
            "|---|---|---|---:|---:|---|"] + rows + [""]
    return out


def report(visits):
    out = ["# LadyBird-DebrisDetector analysis report", ""]
    if visits:
        out.append(f"Based on {len(visits)} visits, {visits[0]['observed_at']:%Y-%m-%d} to {visits[-1]['observed_at']:%Y-%m-%d}.")
    out.append("")
    if not visits:
        out.append("No usable visits yet. Add rows to `data/visits.csv`.")
        return "\n".join(out)

    out += ["## Primary analysis (H₁)", ""]
    main = analyse(visits, "All visits")
    out += main["lines"]

    out += ["## Sensitivity: excluding deviations", ""]
    clean = [v for v in visits if not v["deviation"]]
    out += analyse(clean, f"Visits without deviations ({len(visits) - len(clean)} excluded)")["lines"]

    out += ["## Rain (H₂)", "", "| Rain in prior 48 h | Visits | Mean rating |", "|---|---:|---:|"]
    for cat in ["none", "light", "heavy"]:
        r = [v["rating"] for v in visits if v["rain_48h"] == cat]
        out.append(f"| {cat} | {len(r)} | {fmt(statistics.fmean(r) if r else None)} |")
    out.append("")

    out += ["## River current (H₃)", "", "| Current | Visits | Spearman ρ |", "|---|---:|---:|"]
    for label, cats in [("still or moving", {"still", "moving"}), ("fast / release", {"fast"})]:
        sub = [v for v in visits if v["river_current"] in cats]
        rho, _ = spearman([v["onshore"] for v in sub], [v["rating"] for v in sub], permutations=1000)
        out.append(f"| {label} | {len(sub)} | {fmt(rho)} |")
    out.append("")

    pairs = frontal_pairs(visits)
    out += ["## Wind-shift pairs (cold-front proxy)", ""]
    if pairs:
        out += ["| Before | After | Wind before | Wind after | Rating change |", "|---|---|---|---|---:|"]
        for a, b, d in pairs:
            out.append(
                f"| {a['observed_at']:%Y-%m-%d} | {b['observed_at']:%Y-%m-%d} | "
                f"{a['wind_from_deg']:.0f}° {a['wind_speed_mph']:.0f} mph | "
                f"{b['wind_from_deg']:.0f}° {b['wind_speed_mph']:.0f} mph | {d:+d} |"
            )
    else:
        out.append("No south-to-north wind shifts between consecutive visits yet.")
    out.append("")

    out += wind_cross_check(visits)

    # Decision criteria
    loading_n, loading_mean = main["means"]["loading"]
    clearing_n, clearing_mean = main["means"]["clearing"]
    gap = loading_mean - clearing_mean if loading_mean is not None and clearing_mean is not None else None
    rising_fronts = sum(1 for _, _, d in pairs if d > 0)
    checks = [
        ("Sample size ≥ 20 visits", main["n"] >= MIN_VISITS, f"{main['n']}"),
        ("≥ 5 loading and ≥ 5 clearing visits", loading_n >= MIN_PER_CLASS and clearing_n >= MIN_PER_CLASS,
         f"{loading_n} loading, {clearing_n} clearing"),
        ("Spearman ρ ≥ 0.4", main["rho"] is not None and main["rho"] >= RHO_THRESHOLD, fmt(main["rho"])),
        ("Loading mean ≥ clearing mean + 1.5", gap is not None and gap >= CLASS_GAP, fmt(gap)),
        ("Rating rose after ≥ 2 wind shifts", rising_fronts >= MIN_FRONTS, f"{rising_fronts}"),
    ]
    out += ["## Decision criteria", "", "| Criterion | Met | Value |", "|---|:---:|---|"]
    for name, ok, value in checks:
        out.append(f"| {name} | {'yes' if ok else 'no'} | {value} |")
    out.append("")

    sample_ok = checks[0][1] and checks[1][1]
    evidence = [c[1] for c in checks[2:]]
    if not sample_ok:
        verdict = "**Insufficient data.** Keep collecting until the sample-size targets are met."
    elif all(evidence):
        verdict = "**H₁ supported** for this site and season."
    elif not any(evidence):
        verdict = "**No evidence** that wind drives accumulation at this site."
    else:
        verdict = "**Inconclusive.** Some criteria were met and others were not; see the table above."
    out += ["## Verdict", "", verdict, ""]
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv", nargs="?", default=str(DEFAULT_CSV), help="path to visits.csv")
    parser.add_argument("--out", help="also write the report to this Markdown file")
    args = parser.parse_args()

    path = Path(args.csv)
    if not path.exists():
        sys.exit(f"Can't find {path}. Export visits from the field logger and save them there.")
    text = report(load(path))
    print(text)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
        print(f"\nReport written to {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
