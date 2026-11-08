# LadyBird-DebrisDetector

**Predicting where floating trash collects on Lady Bird Lake from wind and weather, so cleanups go where the trash is.**

Trash on Lady Bird Lake in Austin, Texas, gathers in shoreline pockets, and the amount in any one pocket changes from day to day. LadyBird-DebrisDetector is a citizen-science field study testing a simple idea: **wind decides where floating trash ends up.** If that holds, volunteers can check the wind each morning and go straight to the pockets that are filling.

The study starts with a single site and will expand once the method is proven.


## Status

| | |
|---|---|
| Phase | Pilot, one site |
| Protocol | [v1.0](docs/PROTOCOL.md), registered 2026-11-08 before the first observation |
| Site | Blunn Creek Delta (BCD-01), south shore of Lady Bird Lake, west of I-35 |
| Data collection | November–December 2026 |
| Results | Pending |

## The hypothesis

The Blunn Creek Delta pocket opens to the northeast. Wind from that direction should push floating trash in; wind from the southwest should pull it out.

- **H₁:** Trash rating increases with the onshore wind component over the previous 24 hours.
- **H₀:** Trash rating has no relationship to onshore wind.
- **H₂:** Rain in the previous 48 hours adds trash independently of wind, because the site is at a creek mouth.
- **H₃:** During high river flow from dam releases, the current overrides the wind.

The full design, including variables, controls, threats to validity and the decision criteria, is in the **[study protocol](docs/PROTOCOL.md)**.

## How it works

```
 Camp Mabry wind ──► onshore component ──┐
 (NOAA, hourly)      (mph into pocket)    ├──► compare ──► does wind predict trash?
                                          │
 Site visit ───────► trash rating 1–5 ────┘
 (photos first)      + rain, river flow, days since cleaned
```

For wind from direction *d* at speed *v*, the push straight into a pocket facing angle *f* is:

```
onshore = v × cos(d − f)
```

At this site *f* ≈ 50°. A north wind at 12 mph puts about 8 mph into the pocket; a northeast wind at 12 mph puts in nearly all 12.

## Repository layout

```
LadyBird-DebrisDetector/
├── README.md
├── docs/
│   ├── PROTOCOL.md      Study design, registered before data collection
│   └── FIELD_GUIDE.md   Step-by-step visit instructions and trash scale
├── app/
│   └── index.html       Field logger: open in any browser, works on a phone
├── data/
│   ├── README.md        Data dictionary
│   ├── visits.csv       One row per visit
│   └── photos/          Visit photos
└── analysis/
    └── analyze.py       Runs the pre-registered analysis (Python standard library only)
```

## Quick start

### Log a visit

Open `app/index.html` in a browser. On a phone, host the repo with GitHub Pages and open `https://a-aza1.github.io/LadyBird-DebrisDetector/app/`.

The logger walks through the protocol in order: observe and rate first, then look up conditions, then record cleanup and any deviations. Paste the Camp Mabry wind table and it calculates average speed and direction for you.

Visits are stored in your browser. After each visit, tap **Export CSV** and commit the file to `data/visits.csv`.

### Run the analysis

```bash
python3 analysis/analyze.py
python3 analysis/analyze.py --out analysis/results.md   # also save the report
```

The script needs Python 3.8 or later and no extra packages. It reports mean trash rating by wind class, a Spearman correlation with a permutation p-value, breakdowns by rain and river flow, wind-shift pairs, and a check against each pre-registered decision criterion.

## Contributing

Observations from other Lady Bird Lake pockets are welcome once the pilot is complete. To keep the data comparable:

1. Read the [protocol](docs/PROTOCOL.md) and [field guide](docs/FIELD_GUIDE.md).
2. Open an issue proposing your site with its coordinates, so it can be assigned a site ID and facing angle.
3. Follow the same visit procedure and record deviations honestly.

Corrections to the analysis or the logger are welcome as pull requests.

## Limitations

- Wind comes from Camp Mabry, about 3 miles from the site. Local trees and buildings can change it.
- Ratings are judgment calls. The written scale and archived photos are there so others can check them.
- The pilot covers late fall and early winter only, and about 20 visits. Treat results as preliminary.
- This is an observational study. Wind can't be controlled; cold fronts provide the closest thing to a controlled test.

## Data sources

- Wind and precipitation: NOAA National Weather Service, Camp Mabry ASOS (KATT)
- River flow: U.S. Geological Survey, gauge 08158000, Colorado River at Austin

## License

Code is released under the [MIT License](LICENSE). Data in `data/` is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). If you use the data or method, please cite this repository; see [`CITATION.cff`](CITATION.cff).
