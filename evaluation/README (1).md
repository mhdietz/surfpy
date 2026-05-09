# evaluation/

Ground-truth collection and model evaluation pipeline for SLAPP swell data.

The goal: compare public wave data sources (NOAA buoys, WW3, ERA5, CDIP) against
Surfline's LOTUS model to identify which combinations produce the most accurate
nearshore estimates — and ultimately to build a viable open-source alternative
to Surfline's proprietary forecast pipeline.

This pipeline is **evaluation-only**. It does not feed into the production SLAPP
data layer. It connects to the same Supabase instance as SLAPP but writes only to
the `evaluation` schema, which is invisible to the main app.

---

## Current contents

| File | Purpose |
|------|---------|
| `collect_surfline.py` | Pulls Surfline LOTUS data for configured spots, stores in Supabase Postgres |
| `fetch/ndbc.py` | Fetches NDBC spectral buoy data for configured spots, stores alongside Surfline data |
| `evaluate.py` | Queries both sources, computes MAE/bias/std per spot, renders `report.html` dashboard |
| `report.html` | Generated HTML dashboard — do not edit directly, re-run `evaluate.py` to refresh |

---

## Infrastructure

### Storage
Data is stored in Supabase Postgres under the `evaluation` schema. The main table
is `evaluation.swell_readings`. This schema is fully separate from SLAPP's
application tables. Both `collect_surfline.py` and `fetch/ndbc.py` write to this
table, distinguished by the `source` column (`surfline_lotus` vs `ndbc_buoy`).

### Automation
Collection workflows are defined in `.github/workflows/`. Both can be triggered
manually via GitHub Actions → "Run workflow".

**Surfline collection** (`collect_surfline.yml`):
- **1am UTC daily** — East coast spots (rockaways, manasquan)
- **4am UTC daily** — West coast spots (steamer_lane, trestles, ocean_beach_central)

This corresponds to 8pm local time for each coast, ensuring all 5 daily target
readings (6am–6pm) are in the past by collection time.

**NDBC collection** (`collect_ndbc.yml`) — mirrors the Surfline schedule:
- **1:30am UTC daily** — East coast spots
- **4:30am UTC daily** — West coast spots

Running NDBC collection 30 minutes after Surfline ensures the same-day data is
available for both sources before the dashboard is refreshed.

### Proxy
Surfline returns 403s for requests originating from datacenter IPs (including
GitHub Actions). A **Cloudflare Worker** proxies requests through Cloudflare's
network to bypass this. The Worker URL is stored as a GitHub Actions secret
(`CLOUDFLARE_WORKER_URL`). When `CLOUDFLARE_WORKER_URL` is not set (local dev),
the script falls back to direct requests, which work fine from residential IPs.

NDBC is a public government API and requires no proxy.

---

## Setup

```bash
# From the evaluation/ directory
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install requests psycopg2-binary python-dotenv pytz numpy scipy
```

Requires Python 3.9+ (uses `zoneinfo`). On Python 3.8 add: `pip install backports.zoneinfo`

The `fetch/ndbc.py` script imports `surfpy` from the project root. Ensure the
project root is accessible — the script handles this via `sys.path` insertion.

### Environment variables

Create a `.env` file in the `evaluation/` directory for local development:

```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
CLOUDFLARE_WORKER_URL=https://your-worker.workers.dev   # optional locally
```

`DATABASE_URL` is required. `CLOUDFLARE_WORKER_URL` is optional locally — omitting
it causes the script to make direct requests to Surfline, which works fine from
a residential IP. In GitHub Actions both are injected as secrets.

`.env` is gitignored. Never commit credentials.

---

## Usage

### Surfline collection
```bash
# Collect all spots for today
python collect_surfline.py

# One spot, today
python collect_surfline.py rockaways

# One spot, specific date
python collect_surfline.py rockaways 2025-08-15

# All spots, specific date
python collect_surfline.py 2025-08-15

# Dry run — fetch and parse without writing to the database
python collect_surfline.py --dry-run
python collect_surfline.py rockaways --dry-run
```

### NDBC collection
```bash
# All spots (last ~45 days from NDBC realtime2)
python fetch/ndbc.py

# One spot
python fetch/ndbc.py rockaways

# Dry run
python fetch/ndbc.py --dry-run
python fetch/ndbc.py rockaways --dry-run
```

**Note on NDBC data window:** NDBC realtime2 endpoints serve approximately 45 days
of data. Historical data beyond 45 days requires fetching from the NDBC historical
archive (`data/historical/swden/` and `data/historical/swdir/` `.gz` files). This
is not yet implemented — see Roadmap.

### Evaluation dashboard
```bash
# Generate report.html for all spots
python evaluate.py

# One spot only
python evaluate.py rockaways
```

Opens `report.html` in any browser. Dashboard includes per-spot stats tables
(MAE, bias, std dev for height, period, direction), stacked time series charts
(height / direction / period on shared x-axis), and scatter plots with R²
and linear fit annotations.

Captures readings at **6am, 9am, 12pm, 3pm, and 6pm local time** for each spot.
Duplicate runs are safe — existing timestamps are skipped via unique constraint.

---

## Database schema

**Table: `evaluation.swell_readings`**

| Column | Description |
|--------|-------------|
| `source` | `surfline_lotus` or `ndbc_buoy` |
| `location` | Spot name key (e.g. `rockaways`, `steamer_lane`) |
| `spot_id` | Surfline spot ID or NDBC buoy ID |
| `timestamp` | UTC timestamptz of the reading |
| `surf_min` | Surfline min breaking wave height (ft); NDBC: significant wave height (Hs) as proxy |
| `surf_max` | Surfline max breaking wave height (ft); NDBC: same as surf_min |
| `surf_optimal_score` | Surfline quality score (0, 1, or 2); NULL for NDBC |
| `primary_swell_height` | Height of dominant swell component (ft, 1 decimal) |
| `primary_swell_period` | Period of primary swell (seconds) |
| `primary_swell_direction` | Direction of primary swell (degrees) |
| `primary_swell_impact` | Surfline break-specific impact score; NULL for NDBC |
| `primary_swell_power` | Surfline power score; NULL for NDBC |
| `secondary_swell_*` | Same fields for secondary swell component |
| `tertiary_swell_*` | Same fields for tertiary swell component (Surfline only) |
| `raw_data` | Full Surfline JSON for reprocessing; NULL for NDBC |
| `created_at` | Row insertion timestamp |

**Unique constraint:** `(source, location, timestamp)` — prevents duplicate collection.

### Swell slot ordering

**Surfline:** Swells are sorted by `impact` descending — primary is always the most
influential at the specific break, which differs from offshore height ordering.
Critical for East Coast spots where the dominant nearshore swell is not always the
largest offshore component.

**NDBC:** Swells are sorted by spectral peak energy (`max_energy`) descending,
computed by `surfpy`'s `BuoySpectra.swell_components` via spectral peak detection.
This is the correct physical ordering — a long-period swell with high spectral energy
ranks above a taller short-period wind swell. Do not re-sort by height.

**Component mismatch:** Because Surfline uses break-specific impact and NDBC uses
spectral energy, the two sources occasionally disagree on which component is primary.
This shows up as large spikes in period and direction time series. This is a known
comparison artifact, not a data error.

### Units normalization

**Surfline:** API inconsistently returns swell heights in meters for some spots
despite claiming feet in the `associated.units` field. Detected by checking whether
`surf_min` has a fractional component — Surfline always returns whole numbers when
units are feet. Meter responses are converted to feet on ingest via `3.28084`
multiplier. `raw_data` JSONB preserves original API response for reprocessing.

**NDBC:** `surfpy` returns heights in meters. Converted to feet via `3.28084`
multiplier on ingest.

---

## Configured spots

| Name | Surfline ID | NDBC Buoy ID | Timezone | Coast |
|------|------------|--------------|----------|-------|
| rockaways | 5842041f4e65fad6a7708852 | 44065 | America/New_York | East |
| manasquan | 5842041f4e65fad6a7708856 | 44091 | America/New_York | East |
| steamer_lane | 5842041f4e65fad6a7708805 | 46236 | America/Los_Angeles | West |
| trestles | 5842041f4e65fad6a770888a | 46277 | America/Los_Angeles | West |
| ocean_beach_central | 638e32a4f052ba4ed06d0e3e | 46237 | America/Los_Angeles | West |

Lido Beach and Belmar were removed — they returned identical values to Rockaways
and Manasquan respectively, adding no signal.

To add a spot: find the Surfline spot ID in the URL of the spot's Surfline page
and the NDBC buoy ID from https://www.ndbc.noaa.gov, then add entries to `SPOTS`
in both `collect_surfline.py` and `fetch/ndbc.py`.

---

## Key findings to date

Spots split into two tiers based on ~6 weeks of matched data (spring 2026):

**Tier 1 — NDBC is a reliable proxy:**
- **Trestles** (46277): primary height MAE 0.34ft, bias -0.14ft. Minimal correction needed.
- **East Coast** (Rockaways, Manasquan): small bias (-0.11 to -0.27ft), moderate noise.
  Green's Law shoaling correction expected to help.

**Tier 2 — Systematic gap requiring spot-specific correction:**
- **Steamer Lane** (46236): primary height bias -2.24ft, direction bias -16°.
  Large consistent gap, likely combination of buoy positioning and nearshore
  amplification (Monterey Canyon waveguiding effect). Direction offset is stable
  and correctable.
- **Ocean Beach** (46237): primary height bias -1.73ft, period bias +2.92s,
  direction bias -34.59°. The persistent period gap suggests NDBC and Surfline
  are identifying different spectral components as primary. R²=0.27 — weakest
  predictor relationship of all five spots.

R² across all spots is 0.27–0.52, indicating NDBC alone is a moderate predictor
of Surfline. Errors appear heteroscedastic — the gap grows with wave height —
suggesting a power law or multiplicative correction will outperform a simple
additive offset.

**Caveat:** Current data covers spring conditions only. Correction factors fit
on this data may not generalize to winter NW swells. Continue collecting.

---

## Useful Supabase queries

```sql
-- Overview: coverage by source and spot
SELECT source, location, COUNT(*) as readings,
       MIN(timestamp) as earliest, MAX(timestamp) as latest
FROM evaluation.swell_readings
GROUP BY source, location
ORDER BY location, source;

-- Today's readings across all spots
SELECT source, location, timestamp, surf_min, surf_max,
       primary_swell_height, primary_swell_period, primary_swell_direction
FROM evaluation.swell_readings
WHERE timestamp >= CURRENT_DATE
ORDER BY location, source, timestamp;

-- Yesterday's side-by-side comparison
SELECT location, timestamp,
       MAX(CASE WHEN source='surfline_lotus' THEN primary_swell_height END) as sl_height,
       MAX(CASE WHEN source='ndbc_buoy'      THEN primary_swell_height END) as nb_height,
       MAX(CASE WHEN source='surfline_lotus' THEN primary_swell_period END) as sl_period,
       MAX(CASE WHEN source='ndbc_buoy'      THEN primary_swell_period END) as nb_period,
       MAX(CASE WHEN source='surfline_lotus' THEN primary_swell_direction END) as sl_dir,
       MAX(CASE WHEN source='ndbc_buoy'      THEN primary_swell_direction END) as nb_dir
FROM evaluation.swell_readings
WHERE timestamp >= CURRENT_DATE - INTERVAL '1 day'
  AND timestamp <  CURRENT_DATE
GROUP BY location, timestamp
ORDER BY location, timestamp;

-- Spot-specific deep dive (Surfline)
SELECT timestamp, surf_min, surf_max,
       primary_swell_height, primary_swell_period, primary_swell_direction, primary_swell_impact,
       secondary_swell_height, secondary_swell_period, secondary_swell_direction
FROM evaluation.swell_readings
WHERE location = 'rockaways' AND source = 'surfline_lotus'
ORDER BY timestamp DESC
LIMIT 20;

-- Cases where NDBC secondary height exceeds primary (swell ordering check)
SELECT location, timestamp, primary_swell_height, primary_swell_period,
       secondary_swell_height, secondary_swell_period
FROM evaluation.swell_readings
WHERE source = 'ndbc_buoy'
  AND secondary_swell_height > primary_swell_height
ORDER BY location, timestamp DESC
LIMIT 20;
```

---

## Roadmap

### Completed
- [x] Surfline LOTUS collection — `collect_surfline.py`
- [x] NDBC spectral buoy collection — `fetch/ndbc.py`
- [x] Supabase Postgres storage with `evaluation` schema isolation
- [x] GitHub Actions automation — Surfline (cron, dual-timezone schedule)
- [x] Cloudflare Worker proxy for Surfline (replaced ScrapingBee trial)
- [x] Units normalization — meters → feet for both sources
- [x] Swell slot ordering — Surfline by impact, NDBC by spectral peak energy
- [x] `--dry-run` mode for both collection scripts
- [x] `evaluate.py` — HTML dashboard with per-spot MAE/bias/std, stacked time
      series (height/direction/period), scatter plots with R² and linear fit

### Next — data pipeline
- [ ] NDBC daily automation — GitHub Actions cron (`collect_ndbc.yml`) mirroring
      Surfline schedule, running 30 min after Surfline collection
- [ ] Prior-week comparison view — add "Last 7 Days" section to `evaluate.py` dashboard
      showing side-by-side NDBC vs Surfline for the previous week across all spots
- [ ] `fetch/ndbc_wind.py` — NDBC standard met data (wind speed, direction, gusts)
      from the same buoys; store in `evaluation` schema
- [ ] `fetch/tide.py` — NOAA CO-OPS API for tide predictions and observed water
      levels; store in `evaluation` schema
- [ ] NDBC historical archive backfill — fetch from `data/historical/swden/` and
      `data/historical/swdir/` `.gz` files to extend coverage beyond the 45-day
      realtime2 window; pairs against existing Surfline data going back to Feb 2026

### Next — modeling
- [ ] Model evaluation framework — extend `evaluate.py` to score multiple model
      outputs against Surfline ground truth in a structured, comparable way;
      build this harness before building models
- [ ] `models/model_1_empirical.py` — per-spot learned correction: fit directional
      offset, nonlinear height scaling (power law), and period adjustment from
      collected data. First real attempt to close the Steamer Lane / OB gap.
      Insert before Green's Law since systematic patterns are already visible.
- [ ] `models/model_2_shoaling.py` — Green's Law shoaling correction using
      `breaking_wave_depth` from `surf_spots`. Physics-based depth transformation,
      period-dependent. Expected to help East Coast more than California.
- [ ] `fetch/cdip.py` — CDIP nearshore buoy data (California spots). Highest-
      leverage input for Steamer Lane and OB since nearshore buoys have already
      felt bathymetric effects.
- [ ] `models/model_3_cdip.py` — CDIP nearshore buoy where available
- [ ] `fetch/ww3.py` — WaveWatch III via NOAA OPeNDAP
- [ ] `models/model_4_ww3.py` — WW3 directional spectrum + refraction coefficient;
      adds direction-dependent transformation relevant to consistent directional
      offsets at Steamer Lane and OB
- [ ] Conditional ensemble — Model 3 where CDIP available, fall back to Model 4

### Longer horizon
- [ ] SWAN phase-resolving wave model — run over NOAA high-resolution bathymetric
      grids for Monterey Bay. Prerequisite: 6+ months of ground truth and
      Models 1-2 benchmarked. Monterey Bay has good NOAA bathymetric coverage.
- [ ] Wind and tide modeling — apply same evaluation framework to wind and tide
      once collection is running; likely more tractable than swell
- [ ] Spot expansion — add 5-10 spots with diverse bathymetry to stress-test
      model generalization; prioritize spots with known CDIP coverage

---

## Important notes

- The Surfline API is undocumented and unofficial. It may change without notice.
- NDBC realtime2 endpoints serve ~45 days. Historical archive requires separate
  fetch logic — not yet implemented.
- Swell component mismatch between NDBC (spectral energy ordering) and Surfline
  (break-specific impact ordering) is a known artifact that produces large spikes
  in period and direction time series. It is not a data error.
- Current data covers spring 2026 conditions only. Models fit on this data may
  not generalize to winter NW swells. Keep collecting through fall.
- The `raw_data` JSONB column (Surfline only) allows reprocessing historical rows
  if parsing logic changes without re-fetching from Surfline.
- Meaningful model training requires at least 2–3 months of readings across
  diverse swell conditions (size, period, direction).