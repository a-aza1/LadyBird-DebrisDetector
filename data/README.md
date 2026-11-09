# Data

| File | Contents |
|---|---|
| `visits.csv` | One row per site visit, exported from the field logger (`app/index.html`). |
| `photos/` | Visit photos, named `YYYY-MM-DD_<visit_id>_<n>.jpg`. |

The data in this folder is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). You may reuse it with attribution.

## Adding data

`data/visits.csv` is the source of truth. The field logger reads it from the repo and plots every committed visit. A new visit is held in the browser, marked **NEW**, until it is committed.

1. In the field logger, tap **Export CSV**. The export is the repo file plus any new visits, sorted by time.
2. Replace `data/visits.csv` with the exported file. When the logger next loads and finds those visits in the repo file, it drops its browser copies.
3. Rename that visit's photos to the pattern above and add them to `photos/`.
4. Commit with a message like `Add visit 20261109-k3f2`.

Never edit a recorded rating after the fact. If a value was entered wrong, correct it, explain the change in that row's `notes` field, and include the word **correction** in the commit message. The automated check rejects any change to a committed row unless the commit message says so.

## Automated checks

Every push runs `.github/workflows/pipeline.yml`, which:

1. **Validates** `visits.csv` with `analysis/validate.py`: ratings 1–5, valid dates, unique visit IDs, allowed values for rain and current, a reason for every deviation, and no silent edits to committed rows. A failed check shows a red X on the commit, and the site is not republished until it is fixed.
2. **Archives conditions** to `data/weather/` (also once a day).
3. **Re-runs the analysis** and commits `analysis/results.md`.
4. **Publishes** the site to GitHub Pages.

## Weather archive

| File | Source | Columns |
|---|---|---|
| `weather/katt_hourly.csv` | NOAA/NWS Camp Mabry (KATT) observations, via the [Iowa Environmental Mesonet](https://mesonet.agron.iastate.edu/request/download.phtml) ASOS archive | `valid_utc`, `valid_local` (America/Chicago), `wind_from_deg` (blank when calm), `wind_speed_mph`, `wind_gust_mph`, `precip_1h_in` (0.001 = trace) |
| `weather/usgs_08158000_flow.csv` | USGS Water Services, gauge 08158000, discharge (parameter 00060) | `valid_utc`, `valid_local`, `discharge_cfs`, `qualifiers` (`P` = provisional) |

Rows are keyed by timestamp. Each daily run re-fetches the last 7 days, so a missed run fills itself in, and revised values (USGS data starts provisional) replace earlier ones. To backfill a longer period, open the Actions tab, choose **Data pipeline → Run workflow**, and enter a start date.

## Data dictionary

| Column | Type | Description |
|---|---|---|
| `visit_id` | text | Unique ID: date plus four random characters, e.g. `20261109-k3f2`. |
| `protocol_version` | text | Protocol version in force at the visit, e.g. `1.0`. |
| `site_id` | text | Site code. `BCD-01` is the Blunn Creek Delta pocket. |
| `observed_at` | datetime | Local time (America/Chicago) of the observation, `YYYY-MM-DDTHH:MM`. |
| `observer` | text | Observer's initials. |
| `rating` | integer 1–5 | Trash rating on the [field guide scale](../docs/FIELD_GUIDE.md#trash-scale). **Primary outcome.** |
| `days_since_cleaned` | number or blank | Days since the pocket was last cleaned. Blank means unknown. |
| `cleaned_this_visit` | true/false | Whether the observer cleaned on this visit. |
| `bags_collected` | integer | Trash bags filled. Secondary outcome. |
| `wind_from_deg` | number or blank | Main direction the wind came **from**, degrees clockwise from north (0 = N, 90 = E). **Blank** means calm, with no main direction. |
| `wind_from_compass` | text | The same direction as a 16-point compass label, or `CALM` when the direction is blank. |
| `wind_speed_mph` | number | Average steady wind speed over the window, gusts excluded, calm counted as 0. |
| `wind_window_hours` | integer | Hours of Camp Mabry observations averaged: 12 or 24. |
| `onshore_mph` | number | Wind component pushing into the pocket. Positive = into the pocket. **Primary predictor.** |
| `alongshore_mph` | number | Wind component along the shore. Positive = toward I-35 (down-lake). |
| `wind_class` | text | `loading`, `clearing`, `alongshore` or `calm`, per protocol section 4. |
| `rain_48h` | text | Rain in the previous 48 hours: `none`, `light` or `heavy`. |
| `river_current` | text | Flow at USGS 08158000: `still`, `moving` or `fast` (dam release). |
| `photo_count` | integer | Number of photos taken. |
| `deviation` | true/false | Whether the visit departed from the protocol. |
| `deviation_reason` | text | What was different, if `deviation` is true. |
| `notes` | text | Free-text observations. |
| `face_deg` | number | Facing angle of the pocket used for this visit's calculations. |

`onshore_mph`, `alongshore_mph` and `wind_class` are derived values. The analysis script recalculates them from `wind_from_deg`, `wind_speed_mph` and `face_deg`, so the raw fields are the source of truth.

## Sources

- Wind: NOAA/NWS hourly observations, Camp Mabry ASOS (KATT), https://forecast.weather.gov/data/obhistory/KATT.html
- River flow: USGS 08158000, Colorado River at Austin, https://waterdata.usgs.gov/monitoring-location/USGS-08158000/
