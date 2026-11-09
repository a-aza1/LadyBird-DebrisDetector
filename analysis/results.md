# LadyBird-DebrisDetector analysis report

Based on 1 visits, 2026-11-08 to 2026-11-08.

## Primary analysis (H₁)

### All visits

Visits analysed: **1**

| Wind class | Visits | Mean rating |
|---|---:|---:|
| loading | 1 | 3.00 |
| clearing | 0 | – |
| alongshore | 0 | – |
| calm | 0 | – |

Spearman ρ (onshore wind vs rating): **–**, permutation p = –

## Sensitivity: excluding deviations

### Visits without deviations (1 excluded)

Visits analysed: **0**

| Wind class | Visits | Mean rating |
|---|---:|---:|
| loading | 0 | – |
| clearing | 0 | – |
| alongshore | 0 | – |
| calm | 0 | – |

Spearman ρ (onshore wind vs rating): **–**, permutation p = –

## Rain (H₂)

| Rain in prior 48 h | Visits | Mean rating |
|---|---:|---:|
| none | 0 | – |
| light | 1 | 3.00 |
| heavy | 0 | – |

## River current (H₃)

| Current | Visits | Spearman ρ |
|---|---:|---:|
| still or moving | 1 | – |
| fast / release | 0 | – |

## Wind-shift pairs (cold-front proxy)

No south-to-north wind shifts between consecutive visits yet.

## Wind cross-check against the archive

No archived wind data yet. The daily GitHub Action fills `data/weather/katt_hourly.csv`.

## Decision criteria

| Criterion | Met | Value |
|---|:---:|---|
| Sample size ≥ 20 visits | no | 1 |
| ≥ 5 loading and ≥ 5 clearing visits | no | 1 loading, 0 clearing |
| Spearman ρ ≥ 0.4 | no | – |
| Loading mean ≥ clearing mean + 1.5 | no | – |
| Rating rose after ≥ 2 wind shifts | no | 0 |

## Verdict

**Insufficient data.** Keep collecting until the sample-size targets are met.

