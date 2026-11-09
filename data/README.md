# Data

| File | Contents |
|---|---|
| `visits.csv` | One row per site visit, exported from the field logger (`app/index.html`). |
| `photos/` | Visit photos, named `YYYY-MM-DD_<visit_id>_<n>.jpg`. |

The data in this folder is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). You may reuse it with attribution.

## Adding data

1. In the field logger, tap **Export CSV**.
2. Replace `data/visits.csv` with the exported file. The export always contains every visit stored in the logger, sorted by time.
3. Rename that visit's photos to the pattern above and add them to `photos/`.
4. Commit with a message like `Add visit 20261109-k3f2`.

Never edit a recorded rating after the fact. If a value was entered wrong, correct it and explain the change in that row's `notes` field and in the commit message.

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
| `wind_from_deg` | number | Main direction the wind came **from**, degrees clockwise from north (0 = N, 90 = E). |
| `wind_from_compass` | text | The same direction as a 16-point compass label. |
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
