# evaluation/

Ground-truth collection and model evaluation pipeline for SLAPP swell data.

The goal: compare public wave data sources (WW3, ERA5, CDIP, NOAA buoys) against
Surfline's LOTUS model to identify which combinations produce the most accurate
nearshore estimates — without building a forecasting system.

---

## Current contents

| File | Purpose |
|------|---------|
| `collect_surfline.py` | Pulls Surfline LOTUS data for configured spots, stores in SQLite |
| `swell_data.db` | Local SQLite database (created on first run, gitignored) |

---

## Setup

```bash
# From the evaluation/ directory
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install requests
```

Only `requests` is required. No pysurfline, no pandas, no environment-specific dependencies.

Requires Python 3.9+ (uses `zoneinfo`). On Python 3.8 add: `pip install backports.zoneinfo`

---

## Usage

```bash
# Collect all spots for today
python collect_surfline.py

# One spot, today
python collect_surfline.py lido

# One spot, specific date
python collect_surfline.py lido 2025-08-15

# All spots, specific date
python collect_surfline.py 2025-08-15
```

Captures readings at 6am, 12pm, and 6pm local time for each spot.
Duplicate runs are safe — existing timestamps are skipped via unique index.

---

## Database schema

**Table: `swell_readings`**

| Column | Description |
|--------|-------------|
| `source` | Always `surfline_lotus` for this script |
| `location` | Spot name (e.g. `lido`, `rockaways`) |
| `spot_id` | Surfline spot ID |
| `timestamp` | UTC ISO 8601 timestamp of the reading |
| `surf_min` | Surfline min breaking wave height (ft) |
| `surf_max` | Surfline max breaking wave height (ft) |
| `surf_optimal_score` | Surfline quality score (0, 1, or 2) |
| `primary_swell_*` | Height (ft), period (s), direction (°) of dominant swell |
| `secondary_swell_*` | Same for secondary swell component |
| `raw_data` | Full Surfline JSON for the reading |
| `created_at` | When this row was inserted |

The schema is designed to accept other sources (`ndbc_buoy`, `ww3`, `era5`, `cdip`)
in the same table as we add collection scripts for each.

---

## Configured spots

| Name | Surfline ID | Timezone |
|------|------------|----------|
| rockaways | 5842041f4e65fad6a7708852 | America/New_York |
| lido | 5842041f4e65fad6a77089e2 | America/New_York |
| belmar | 5842041f4e65fad6a7708a01 | America/New_York |
| manasquan | 5842041f4e65fad6a7708856 | America/New_York |
| steamer_lane | 5842041f4e65fad6a7708805 | America/Los_Angeles |
| trestles | 5842041f4e65fad6a770888a | America/Los_Angeles |

To add a spot: find the Surfline spot ID in the URL of the spot's Surfline page,
then add entries to `SPOTS` and `SPOT_TIMEZONES` in `collect_surfline.py`.

---

## Roadmap

- [ ] `collect_ndbc.py` — NOAA buoy data for the same spots/times
- [ ] `collect_ww3.py` — WaveWatch III model output via NOAA THREDDS
- [ ] `collect_cdip.py` — CDIP nearshore buoy data where available
- [ ] `evaluate.py` — Compare all sources against Surfline ground truth, compute MAE/bias per spot
- [ ] Scheduler setup (cron / launchd) for automatic daily collection

---

## Important notes

- `swell_data.db` is gitignored — don't commit it. Back it up separately.
- The Surfline API is undocumented and unofficial. It may change without notice.
- This pipeline is evaluation-only. It does not feed into the production SLAPP data layer.
