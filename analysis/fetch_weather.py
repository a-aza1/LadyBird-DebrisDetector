#!/usr/bin/env python3
"""Archive the raw conditions data the study depends on.

Downloads and merges into data/weather/:
  katt_hourly.csv           Camp Mabry (KATT) hourly wind and precipitation, from the Iowa Environmental
                            Mesonet ASOS archive (a copy of the NOAA/NWS observations)
  usgs_08158000_flow.csv    Colorado River at Austin discharge, from the USGS Water Services
                            instantaneous-values service

Usage:
    python3 analysis/fetch_weather.py              # last 7 days (the daily GitHub Action runs this)
    python3 analysis/fetch_weather.py --since 2026-11-01

Re-running is safe: rows are keyed by timestamp, so existing rows are updated, never duplicated.
Each source is fetched independently; if one fails the other is still saved.
Exit code 1 only if every source failed. Uses only the Python standard library.
"""

import argparse
import csv
import io
import json
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "weather"
LOCAL = ZoneInfo("America/Chicago")
USER_AGENT = "LadyBird-DebrisDetector weather archiver (citizen-science study)"
KNOTS_TO_MPH = 1.150779

IEM_URL = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"
USGS_URL = "https://waterservices.usgs.gov/nwis/iv/"

KATT_FIELDS = ["valid_utc", "valid_local", "wind_from_deg", "wind_speed_mph", "wind_gust_mph", "precip_1h_in"]
FLOW_FIELDS = ["valid_utc", "valid_local", "discharge_cfs", "qualifiers"]


def get(url, params, timeout=60):
    full = url + "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(full, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def to_local(dt_utc):
    return dt_utc.astimezone(LOCAL).strftime("%Y-%m-%dT%H:%M")


# ---------- Camp Mabry via Iowa Environmental Mesonet ----------

def iem_params(station, start, end):
    return {
        "station": station,
        "data": ["drct", "sknt", "gust", "p01i"],
        "year1": start.year, "month1": start.month, "day1": start.day,
        "year2": end.year, "month2": end.month, "day2": end.day,
        "tz": "Etc/UTC",
        "format": "onlycomma",
        "latlon": "no",
        "elev": "no",
        "missing": "M",
        "trace": "T",
        "direct": "no",
        "report_type": [3, 4],  # routine hourly and special observations, as on the NWS 3-day page
    }


def parse_iem(text):
    """Parse IEM ASOS output into rows. Finds the header line, so leading metadata is tolerated."""
    lines = [ln for ln in text.splitlines() if ln.strip() and not ln.startswith("#")]
    start = next((i for i, ln in enumerate(lines) if ln.lower().startswith("station")), None)
    if start is None:
        return []
    sep = "\t" if "\t" in lines[start] else ","
    reader = csv.DictReader(io.StringIO("\n".join(lines[start:])), delimiter=sep)
    rows = []
    for r in reader:
        r = {k.strip(): (v or "").strip() for k, v in r.items() if k}
        try:
            valid = datetime.strptime(r["valid"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        except (KeyError, ValueError):
            continue

        def num(key):
            v = r.get(key, "M")
            if v in ("", "M"):
                return None
            if v == "T":  # trace of precipitation
                return 0.001
            try:
                return float(v)
            except ValueError:
                return None

        knots, drct, gust, precip = num("sknt"), num("drct"), num("gust"), num("p01i")
        mph = None if knots is None else round(knots * KNOTS_TO_MPH, 1)
        # Calm is reported as 0 knots; it has no direction, so the direction is left blank.
        direction = None if (mph is None or mph == 0 or drct is None) else drct
        rows.append({
            "valid_utc": valid.strftime("%Y-%m-%dT%H:%MZ"),
            "valid_local": to_local(valid),
            "wind_from_deg": "" if direction is None else f"{direction:g}",
            "wind_speed_mph": "" if mph is None else f"{mph:g}",
            "wind_gust_mph": "" if gust is None else f"{round(gust * KNOTS_TO_MPH, 1):g}",
            "precip_1h_in": "" if precip is None else f"{precip:g}",
        })
    return rows


def fetch_katt(start, end):
    for station in ("ATT", "KATT"):  # IEM uses 3-letter IDs for US ASOS sites; try the 4-letter form too
        rows = parse_iem(get(IEM_URL, iem_params(station, start, end + timedelta(days=1))))
        if rows:
            return rows
    raise RuntimeError("no Camp Mabry observations returned")


# ---------- River flow via USGS ----------

def parse_usgs(text):
    data = json.loads(text)
    rows = []
    for series in data.get("value", {}).get("timeSeries", []):
        for block in series.get("values", []):
            for v in block.get("value", []):
                try:
                    when = datetime.fromisoformat(v["dateTime"]).astimezone(timezone.utc)
                except (KeyError, ValueError):
                    continue
                value = v.get("value")
                if value in (None, "", "-999999"):
                    continue
                rows.append({
                    "valid_utc": when.strftime("%Y-%m-%dT%H:%MZ"),
                    "valid_local": to_local(when),
                    "discharge_cfs": value,
                    "qualifiers": " ".join(v.get("qualifiers", [])),
                })
    return rows


def fetch_flow(start, end):
    text = get(USGS_URL, {
        "format": "json", "sites": "08158000", "parameterCd": "00060", "siteStatus": "all",
        "startDT": start.isoformat(), "endDT": (end + timedelta(days=1)).isoformat(),
    })
    rows = parse_usgs(text)
    if not rows:
        raise RuntimeError("no river-flow values returned")
    return rows


# ---------- merge ----------

def merge(path, fields, new_rows):
    existing = {}
    if path.exists():
        with open(path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                existing[r["valid_utc"]] = r
    before = dict(existing)
    for r in new_rows:
        existing[r["valid_utc"]] = r
    added = sum(1 for k in existing if k not in before)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for k in sorted(existing):
            w.writerow(existing[k])
    return added, len(existing)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--since", type=date.fromisoformat, help="first day to fetch (default: 7 days ago)")
    args = parser.parse_args()
    end = datetime.now(LOCAL).date()
    start = args.since or end - timedelta(days=7)

    failures = 0
    for name, fetch, path, fields in (
        ("Camp Mabry wind and rain", fetch_katt, OUT / "katt_hourly.csv", KATT_FIELDS),
        ("USGS 08158000 river flow", fetch_flow, OUT / "usgs_08158000_flow.csv", FLOW_FIELDS),
    ):
        try:
            added, total = merge(path, fields, fetch(start, end))
            print(f"{name}: {added} new rows, {total} total in {path.relative_to(ROOT)}")
        except Exception as err:  # keep going so one outage doesn't block the other source
            failures += 1
            print(f"::warning::{name} could not be fetched ({err}). The archive keeps its earlier rows; the next run will fill the gap.")
    sys.exit(1 if failures == 2 else 0)


if __name__ == "__main__":
    main()
