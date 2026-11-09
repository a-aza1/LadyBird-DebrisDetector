# Field Guide

Step-by-step instructions for a site visit under [Protocol v1.0](PROTOCOL.md). One visit takes about 10 minutes plus cleanup.

## Before you go

- **Schedule:** about 4 visits a week, between 8:30 and 9:30 a.m. Days of the week can vary; avoid gaps of more than 3 days.
- **Watch for cold fronts.** When the forecast shows a front, plan visits the morning before and the morning after. These pairs are the most informative data in the study.
- **Bring:** phone, gloves, trash bags, a grabber.

## At the site

### 1. Photograph the pocket

Stand at the fixed photo point and take:
- one **wide** shot of the whole pocket, framed the same way each visit;
- one **close-up** of the densest trash.

Keep people and campsites out of frame. Point the camera at the water and shoreline.

### 2. Rate the trash

Judge the whole pocket, about 130 m of shoreline, using the scale below. **Do not look at any wind data before rating.** Knowing the wind could bias the rating.

### 3. Record cleanup history

Enter how many days since the pocket was last cleaned, by you or by anyone you saw. Leave it blank if you don't know.

### 4. Look up the conditions

- **Wind:** open the [Camp Mabry 3-day history](https://forecast.weather.gov/data/obhistory/KATT.html), copy the table, and paste it into the logger. It averages the steady speeds (gusts ignored, calm counted as 0) and finds the main direction. Use the 24-hour window unless the wind shifted a lot during the day, then use 12 hours.
- **Rain:** check the precipitation columns on the same table for the last 48 hours. All blank or zero is *None*; a few small amounts is *Light*; around half an inch or more is *Heavy*.
- **River:** open [USGS 08158000](https://waterdata.usgs.gov/monitoring-location/USGS-08158000/). Flat and in the hundreds of cfs is *Still*; a noticeable rise is *Moving*; a jump into the thousands is *Fast / release*.

### 5. Clean up

Clean if you plan to, then record the number of bags.

### 6. Record deviations

If anything differed from this guide, tick **Something differed from the protocol** and say what in one line. Examples:
- visited outside 8:30–9:30 a.m.;
- checked the wind before rating;
- used a different photo point;
- someone else rated the pocket;
- saw signs that a city crew or other volunteers had cleaned it.

A recorded deviation is fine. An unrecorded one makes the data unreliable.

### 7. Save and export

Save the visit, then **Export CSV** and upload it to `data/visits.csv` in the repo. The logger reads that file, so a visit stays marked **NEW** until it is committed. Rename the photos to `YYYY-MM-DD_<visit_id>_1.jpg`, `_2.jpg` and add them to `data/photos/`.

## Trash scale

| Level | Name | What you see | Pieces | Bags |
|:---:|---|---|---|---|
| 1 | Clean | Open water along the edge. Maybe a stray bottle or wrapper. | 0–5 | under ¼ |
| 2 | Light | Scattered items you notice when you look, spread out, no clumps. | 5–20 | ¼–½ |
| 3 | Noticeable | Small clusters at the waterline. A passerby on the trail would see it. | 20–50 | about 1 |
| 4 | Heavy | Clumps and small rafts along much of the pocket. Hard to count. | 50+ | 1–3 |
| 5 | Solid raft | A continuous mat of trash. In places you can't see the water surface. | too many | 3+ |

When you're torn between two levels, use the bag count to decide.

## Reading the wind

The Camp Mabry table shows wind as, for example, `SSE 8 G 20`:
- `SSE` is the direction the wind is coming **from**;
- `8` is the steady speed in mph;
- `G 20` is a gust, which the study ignores;
- `Calm` means no wind and counts as 0.

Calm readings are common overnight and early in the morning. They count as 0 mph in the average and are left out when working out direction, so a few windy hours still set the direction. If the whole window is calm, choose **Calm** on the compass. The logger does this for you when you paste an all-calm table. The visit is then recorded with no direction rather than a made-up one. If the lake was visibly choppy while the station read calm, say so in the notes.

The pocket opens toward the northeast (about 50°), so:

| Wind from | Effect on the pocket |
|---|---|
| N, NNE, NE, ENE, E | **Loading:** pushes trash in |
| S, SSW, SW, WSW, W | **Clearing:** pulls trash out |
| NW, NNW | **Along shore:** slides trash toward I-35 |
| SE, SSE | **Along shore:** slides trash toward Congress |

The exact boundaries depend on speed. The logger calculates the class for you.

## Cold fronts

A cold front is the leading edge of cooler, drier air. In Austin, fronts pass about weekly from fall through spring:

1. **Before:** warm, humid, south winds. The pocket should be clearing.
2. **Passage:** the wind flips to north or northwest within an hour or two, often gusty, sometimes with rain.
3. **After:** cool, dry, north winds of 10–20 mph for a day or so. The pocket should be loading.
4. **Recovery:** over 2–3 days the wind swings back to the south.

On the Camp Mabry table, a front shows up as the wind direction flipping from S to N while the temperature drops.
