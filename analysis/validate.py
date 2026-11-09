#!/usr/bin/env python3
"""Check data/visits.csv before it is accepted.

Usage:
    python3 analysis/validate.py                          # check data/visits.csv
    python3 analysis/validate.py --previous old.csv       # also compare with the last committed version

Every row must be well formed. When --previous is given, rows that already existed may not be
changed or removed, unless the commit message (env COMMIT_MESSAGE) contains the word "correction".
Problems are printed as GitHub Actions annotations, so they show on the commit's run page.
Exit code 1 means at least one error. Uses only the Python standard library.
"""

import argparse
import csv
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = ROOT / "data" / "visits.csv"

COLUMNS = [
    "visit_id", "protocol_version", "site_id", "observed_at", "observer", "rating", "days_since_cleaned",
    "cleaned_this_visit", "bags_collected", "wind_from_deg", "wind_from_compass", "wind_speed_mph",
    "wind_window_hours", "onshore_mph", "alongshore_mph", "wind_class", "rain_48h", "river_current",
    "photo_count", "deviation", "deviation_reason", "notes", "face_deg",
]
COMPASS = {"N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"}
PROTOCOL_VERSIONS = {"1.0", "1.1", "1.2"}
SITES = {"BCD-01"}
ID_PATTERN = re.compile(r"^\d{8}-[a-z0-9]{4}$")

errors = 0
warnings = 0


def report(level, line, message, path):
    global errors, warnings
    if level == "error":
        errors += 1
    else:
        warnings += 1
    print(f"::{level} file={path},line={line}::{message}")


def number(value, lo=None, hi=None, integer=False, allow_blank=False):
    """Return (ok, parsed)."""
    value = (value or "").strip()
    if value == "":
        return (allow_blank, None)
    try:
        parsed = int(value) if integer else float(value)
    except ValueError:
        return (False, None)
    if lo is not None and parsed < lo:
        return (False, parsed)
    if hi is not None and parsed > hi:
        return (False, parsed)
    return (True, parsed)


def check_row(row, line, path, seen_ids):
    def err(msg):
        report("error", line, f"{row.get('visit_id') or 'row'}: {msg}", path)

    vid = (row.get("visit_id") or "").strip()
    if not ID_PATTERN.match(vid):
        err(f"visit_id '{vid}' should look like 20261109-ab12")
    elif vid in seen_ids:
        err(f"visit_id '{vid}' appears more than once (first on line {seen_ids[vid]})")
    else:
        seen_ids[vid] = line

    if row.get("protocol_version") not in PROTOCOL_VERSIONS:
        err(f"unknown protocol_version '{row.get('protocol_version')}'")
    if row.get("site_id") not in SITES:
        err(f"unknown site_id '{row.get('site_id')}'")

    try:
        when = datetime.fromisoformat(row.get("observed_at", ""))
        if when > datetime.now() + timedelta(days=1):
            err(f"observed_at {row['observed_at']} is in the future")
        if vid[:8].isdigit() and vid[:8] != when.strftime("%Y%m%d"):
            report("warning", line, f"{vid}: visit_id date doesn't match observed_at {row['observed_at']}", path)
    except ValueError:
        err(f"observed_at '{row.get('observed_at')}' should look like 2026-11-09T08:55")

    ok, _ = number(row.get("rating"), 1, 5, integer=True)
    if not ok:
        err(f"rating '{row.get('rating')}' must be a whole number from 1 to 5")

    ok, direction = number(row.get("wind_from_deg"), 0, 360, allow_blank=True)
    compass = (row.get("wind_from_compass") or "").strip()
    if not ok:
        err(f"wind_from_deg '{row.get('wind_from_deg')}' must be 0–360, or blank for calm")
    elif direction is None and compass != "CALM":
        err("wind_from_deg is blank, so wind_from_compass must be CALM")
    elif direction is not None and compass not in COMPASS:
        err(f"wind_from_compass '{compass}' is not a 16-point compass label")

    ok, _ = number(row.get("wind_speed_mph"), 0, 80)
    if not ok:
        err(f"wind_speed_mph '{row.get('wind_speed_mph')}' must be 0–80")
    ok, _ = number(row.get("wind_window_hours"), 1, 72, allow_blank=True)
    if not ok:
        err(f"wind_window_hours '{row.get('wind_window_hours')}' must be 1–72")

    if row.get("rain_48h") not in {"none", "light", "heavy"}:
        err(f"rain_48h '{row.get('rain_48h')}' must be none, light or heavy")
    if row.get("river_current") not in {"still", "moving", "fast"}:
        err(f"river_current '{row.get('river_current')}' must be still, moving or fast")

    for field in ("cleaned_this_visit", "deviation"):
        if (row.get(field) or "").lower() not in {"true", "false"}:
            err(f"{field} '{row.get(field)}' must be true or false")
    if (row.get("deviation") or "").lower() == "true" and not (row.get("deviation_reason") or "").strip():
        err("deviation is true but deviation_reason is empty")

    for field, hi in (("days_since_cleaned", 3650), ("bags_collected", 500), ("photo_count", 100)):
        ok, _ = number(row.get(field), 0, hi, allow_blank=(field == "days_since_cleaned"))
        if not ok:
            err(f"{field} '{row.get(field)}' must be a number from 0 to {hi}")
    ok, _ = number(row.get("face_deg"), 0, 360)
    if not ok:
        err(f"face_deg '{row.get('face_deg')}' must be 0–360")


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv", nargs="?", default=str(DEFAULT_CSV))
    parser.add_argument("--previous", help="the last committed visits.csv, to detect edits to existing rows")
    args = parser.parse_args()

    path = Path(args.csv)
    shown = os.path.relpath(path, ROOT) if path.is_absolute() else str(path)
    header, rows = read(path)

    missing = [c for c in COLUMNS if c not in header]
    if missing:
        report("error", 1, f"missing columns: {', '.join(missing)}", shown)
    extra = [c for c in header if c not in COLUMNS]
    if extra:
        report("warning", 1, f"unexpected columns will be ignored: {', '.join(extra)}", shown)

    seen = {}
    for i, row in enumerate(rows, start=2):
        check_row(row, i, shown, seen)

    if args.previous and Path(args.previous).exists() and Path(args.previous).stat().st_size:
        _, old_rows = read(args.previous)
        current = {r.get("visit_id"): (i, r) for i, r in enumerate(rows, start=2)}
        allowed = "correction" in os.environ.get("COMMIT_MESSAGE", "").lower()
        level = "warning" if allowed else "error"
        hint = "" if allowed else " Committed rows can't change. If this is a deliberate fix, put the word 'correction' in the commit message and explain it in the row's notes."
        for old in old_rows:
            vid = old.get("visit_id")
            if vid not in current:
                report(level, 1, f"{vid}: this committed visit was removed.{hint}", shown)
                continue
            line, new = current[vid]
            changed = [c for c in COLUMNS if (old.get(c) or "") != (new.get(c) or "")]
            if changed:
                report(level, line, f"{vid}: committed visit changed ({', '.join(changed)}).{hint}", shown)

    print(f"Checked {len(rows)} visits: {errors} error(s), {warnings} warning(s).")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
