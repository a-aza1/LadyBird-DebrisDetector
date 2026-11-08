# Study Protocol: Wind-Driven Trash Accumulation at the Blunn Creek Delta

| | |
|---|---|
| **Protocol version** | 1.0 |
| **Registered** | 2026-11-08, before the first observation |
| **Study site** | Blunn Creek Delta, south shore of Lady Bird Lake, Austin, Texas |
| **Site extent** | 30.25357, −97.74158 to 30.25266, −97.74071 (about 130 m of shoreline) |
| **Study type** | Observational field study (natural experiment) |
| **Planned duration** | Pilot phase: about 4 weeks, starting November 2026 |

This document records the hypotheses, variables and analysis plan **before** any data is collected. Changes made after data collection begins are listed in the [amendment log](#amendment-log) with a date and reason, so readers can tell planned analyses from ones added later.

---

## 1. Background

Floating trash on Lady Bird Lake collects in shoreline pockets, and the amount in a given pocket changes from day to day. Litter reaches the lake mainly through storm drains and creeks after rain. Once on the water, floating debris (bottles, foam, bags) sits partly above the surface and drifts with the wind at a small fraction of the wind speed, typically 1–4%. Because the lake is only a few hundred feet wide at the study site, a few hours of steady wind is enough to move loose debris across it.

Lady Bird Lake is a reservoir between Tom Miller Dam and Longhorn Dam. On most days the current is weak, which suggests wind may decide where floating trash ends up, except during large dam releases.

## 2. Research question

Does wind direction and strength determine how much floating trash collects in the Blunn Creek Delta pocket?

## 3. Hypotheses

| | Statement |
|---|---|
| **H₁ (primary)** | Trash rating increases with the onshore wind component averaged over the previous 24 hours. |
| **H₀ (null)** | Trash rating has no relationship with the onshore wind component. |
| **H₂ (secondary)** | Rain in the previous 48 hours raises the trash rating independently of wind, because the site is at a creek mouth. |
| **H₃ (secondary)** | During high river flow (dam releases), the relationship between wind and trash rating weakens. |

## 4. Site geometry

The shoreline segment runs on a bearing of about 140° (northwest to southeast). Open water lies to the northeast, so the pocket **opens toward about 50°**. Wind *from* 50° blows straight into the pocket.

For a wind from direction *d* (degrees, the direction the wind comes **from**) at speed *v* (mph):

```
onshore component  = v × cos(d − 50°)       positive = pushes into the pocket
alongshore component = v × cos((d + 180°) − 140°)   positive = pushes down-lake, toward I-35
```

| Wind class | Rule | Expected effect |
|---|---|---|
| **Loading** | onshore ≥ 4 mph | Trash pushed into the pocket |
| **Clearing** | onshore ≤ −4 mph | Trash pulled away from the pocket |
| **Along shore** | between −4 and 4 mph, speed ≥ 3 mph | Trash slides past along the shore |
| **Calm** | speed < 3 mph | Little movement |

The 50° facing angle is an estimate from coordinates. If field observation shows it is wrong, the corrected value is recorded as an amendment, and every visit stores the angle in use at the time (`face_deg`).

## 5. Variables

### Independent variable (predictor)
- **Onshore wind component (mph)**, computed from the hourly observations at the Camp Mabry ASOS station (KATT) over the 24 hours before the visit. A 12-hour window is used instead when the wind direction shifted substantially during the day (for example, a frontal passage). The window used is recorded per visit.

### Dependent variables (outcomes)
- **Primary:** trash rating, 1–5, on the scale defined in the [Field Guide](FIELD_GUIDE.md#trash-scale).
- **Secondary:** number of trash bags collected.

### Controlled variables (held constant by procedure)
| Variable | How it is held constant |
|---|---|
| Location | Same 130 m segment every visit |
| Photo point | Same fixed standing spot and framing |
| Time of day | Visits between 8:30 and 9:30 a.m. local time |
| Rating method | Same written 1–5 scale |
| Observer | Single observer for the pilot phase |
| Order of steps | Rating and photos happen **before** checking any wind data, and before any cleanup |
| Wind data source | Camp Mabry (KATT) hourly observations |

### Covariates (measured, not controlled)
- Rain in the previous 48 hours: none, light, heavy
- River current below Longhorn Dam (USGS gauge 08158000): still, moving, fast/release
- Days since the pocket was last cleaned
- Weekday or weekend

## 6. Procedure

1. Arrive at the photo point between 8:30 and 9:30 a.m.
2. Take one wide photo of the pocket and one close-up of the densest trash.
3. Assign the trash rating using the written scale. **Do not look at wind data first.**
4. Record days since last cleaning and whether you will clean today.
5. Look up wind (Camp Mabry, past 24 hours), rain (past 48 hours) and river flow, and enter them.
6. Clean if planned, then record bags collected.
7. Record any deviation from this procedure (section 8).

The full step-by-step instructions are in the [Field Guide](FIELD_GUIDE.md).

## 7. Threats to validity

| Threat | Description | Mitigation |
|---|---|---|
| Observer bias | Knowing the wind could influence the rating. | Rate before looking up wind. Photos allow independent re-rating. |
| Cleanup carryover | Cleaning resets the pocket, so the next rating reflects elapsed time as well as wind. | Record days since last cleaning; include it as a covariate. |
| Unobserved cleaning | City crews or other volunteers may clear the pocket. | Note visible signs of other cleanup as a deviation. |
| Measurement distance | Camp Mabry is about 3 miles from the site; local trees and buildings can alter wind. | Accept as a limitation; a future phase may add an on-site wind reading. |
| Subjective scale | Ratings are judgment calls. | Written scale with piece and bag counts; photos archived for review. |
| Seasonality | A November–December pilot covers fall and winter wind patterns only. | Results are reported as specific to this season. |
| Small sample | A pilot of about 20 visits has limited statistical power. | Results are treated as preliminary and used to plan a longer study. |

## 8. Deviations

Any departure from section 6 is recorded on that visit as a deviation, with a one-line reason. Examples: visiting outside the time window, a different observer, a different photo point, partial cleaning, rating after seeing wind data, or visible signs that someone else cleaned the pocket.

Visits with deviations are **kept** in the dataset. The primary analysis is run twice, with and without them, and both results are reported.

## 9. Analysis plan

Run `analysis/analyze.py` on `data/visits.csv`. It performs the following:

1. **Descriptive:** count of visits and mean trash rating for each wind class.
2. **Primary test (H₁):** Spearman rank correlation between onshore wind component and trash rating. Spearman is used because the rating is ordinal.
3. **Secondary (H₂):** mean rating by rain category.
4. **Secondary (H₃):** primary correlation repeated for visits with still or moving current, and separately for fast/release.
5. **Frontal pairs:** for each cold front with a visit within 48 hours before and after, the change in rating.
6. **Sensitivity:** steps 1 and 2 repeated excluding visits with deviations.

### Sample size target
At least **20 visits**, including at least **5 loading** and **5 clearing** visits.

### Decision criteria
H₁ is considered **supported** in the pilot if all of the following hold:
- Spearman ρ ≥ 0.4 between onshore wind and rating
- Loading visits average at least **1.5 levels higher** than clearing visits
- Ratings rise after at least **two** separate cold-front passages

If none of these hold, the pilot finds no evidence that wind drives accumulation at this site. Mixed results are reported as inconclusive, with the specific criteria that were and were not met.

## 10. Data and materials

| Item | Location |
|---|---|
| Visit records | `data/visits.csv` |
| Photos | `data/photos/`, named `YYYY-MM-DD_<visit_id>_<n>.jpg` |
| Data dictionary | [`data/README.md`](../data/README.md) |
| Field logger | `app/index.html` |
| Analysis | `analysis/analyze.py` |

Wind data: National Weather Service observations at Camp Mabry (KATT), https://forecast.weather.gov/data/obhistory/KATT.html. Historical records are also available from the Iowa Environmental Mesonet ASOS archive.

River flow: USGS 08158000, Colorado River at Austin, https://waterdata.usgs.gov/monitoring-location/USGS-08158000/

## Amendment log

| Date | Version | Change | Reason |
|---|---|---|---|
| 2026-11-08 | 1.0 | Protocol registered | — |
