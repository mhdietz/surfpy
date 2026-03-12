# evaluation/

Ground-truth collection and model evaluation pipeline for SLAPP swell data.

The goal: compare public wave data sources (WW3, ERA5, CDIP, NOAA buoys) against
Surfline's LOTUS model to identify which combinations produce the most accurate
nearshore estimates — without building a forecasting system.

This pipeline is **evaluation-only**. It does not feed into the production SLAPP
data layer. It connects to the same Supabase instance as SLAPP but writes only to
the `evaluation` schema, which is invisible to the main app.

---

## Current contents

| File | Purpose |
|------|---------|
| `collect_surfline.py` | Pulls Surfline LOTUS data for configured spots, stores in Supabase Postgres |

---

## Infrastructure

### Storage
Data is stored in Supabase Postgres under the `evaluation` schema. The main table
is `evaluation.swell_readings`. This schema is fully separate from SLAPP's
application tables.

### Automation
The workflow is defined in `.github/workflows/collect_surfline.yml`. It can also
be triggered manually via GitHub Actions → "Run workflow", with an optional input
to target `east`, `west`, or `all` spots — useful for testing or recovering a
missed run.

Collection runs automatically via **GitHub Actions** on a cron schedule:
- **1am UTC daily** — East coast spots (rockaways, manasquan)
- **4am UTC daily** — West coast spots (steamer_lane, trestles, ocean_beach_central)

This corresponds to 8pm local time for each coast, ensuring all 5 daily target
readings (6am–6pm) are in the past by collection time.

### Proxy
Surfline returns 403s for requests originating from datacenter IPs (including
GitHub Actions). A **Cloudflare Worker** proxies requests through Cloudflare's
network to bypass this. The Worker URL is stored as a GitHub Actions secret
(`CLOUDFLARE_WORKER_URL`). When `CLOUDFLARE_WORKER_URL` is not set (local dev),
the script falls back to direct requests, which work fine from residential IPs.

---

## Setup

```bash
# From the evaluation/ directory
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install requests psycopg2-binary python-dotenv
```

Requires Python 3.9+ (uses `zoneinfo`). On Python 3.8 add: `pip install backports.zoneinfo`

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

Captures readings at **6am, 9am, 12pm, 3pm, and 6pm local time** for each spot.
Duplicate runs are safe — existing timestamps are skipped via unique constraint.

---

## Database schema

**Table: `evaluation.swell_readings`**

| Column | Description |
|--------|-------------|
| `source` | Always `surfline_lotus` for this script |
| `location` | Spot name key (e.g. `rockaways`, `steamer_lane`) |
| `spot_id` | Surfline spot ID |
| `timestamp` | UTC timestamptz of the reading |
| `surf_min` | Surfline min breaking wave height (ft, whole number) |
| `surf_max` | Surfline max breaking wave height (ft, whole number) |
| `surf_optimal_score` | Surfline quality score (0, 1, or 2) |
| `primary_swell_height` | Height of most impactful swell at this break (ft, 1 decimal) |
| `primary_swell_period` | Period of primary swell (seconds) |
| `primary_swell_direction` | Direction of primary swell (degrees, whole number) |
| `primary_swell_impact` | Surfline break-specific impact score for primary swell |
| `primary_swell_power` | Power of primary swell |
| `secondary_swell_*` | Same fields for secondary swell component |
| `tertiary_swell_*` | Same fields for tertiary swell component |
| `raw_data` | Full Surfline JSON for the reading (for reprocessing) |
| `created_at` | Row insertion timestamp |

**Unique constraint:** `(source, location, timestamp)` — prevents duplicate collection.

**Swell slot ordering:** Swells are sorted by `impact` descending, not by height.
Primary swell is always the most influential at the specific break, which differs
from offshore height ordering — critical for East Coast spots where the dominant
nearshore swell is not always the largest offshore component.

### Units normalization

Surfline's API inconsistently returns swell heights in meters for some spots
despite claiming feet in the `associated.units` field. The script detects this
by checking whether `surf_min` has a fractional component — Surfline always
returns whole numbers when units are feet. Meter responses are converted to feet
on ingest via a `3.28084` multiplier. The `raw_data` JSONB column always preserves
the original API response for reprocessing if needed.

---

## Configured spots

| Name | Surfline ID | Timezone | Coast |
|------|------------|----------|-------|
| rockaways | 5842041f4e65fad6a7708852 | America/New_York | East |
| manasquan | 5842041f4e65fad6a7708856 | America/New_York | East |
| steamer_lane | 5842041f4e65fad6a7708805 | America/Los_Angeles | West |
| trestles | 5842041f4e65fad6a770888a | America/Los_Angeles | West |
| ocean_beach_central | 638e32a4f052ba4ed06d0e3e | America/Los_Angeles | West |

Lido Beach and Belmar were removed — they returned identical values to Rockaways
and Manasquan respectively, adding no signal.

To add a spot: find the Surfline spot ID in the URL of the spot's Surfline page,
then add entries to `SPOTS` and `SPOT_TIMEZONES` in `collect_surfline.py`.

---

## Useful Supabase queries

```sql
-- Overview: what's in the table
SELECT location, COUNT(*) as readings, MIN(timestamp) as earliest, MAX(timestamp) as latest
FROM evaluation.swell_readings
GROUP BY location
ORDER BY location;

-- Today's readings across all spots
SELECT location, timestamp, surf_min, surf_max,
       primary_swell_height, primary_swell_period, primary_swell_direction
FROM evaluation.swell_readings
WHERE timestamp >= CURRENT_DATE
ORDER BY location, timestamp;

-- Spot-specific deep dive
SELECT timestamp, surf_min, surf_max,
       primary_swell_height, primary_swell_period, primary_swell_direction, primary_swell_impact,
       secondary_swell_height, secondary_swell_period, secondary_swell_direction
FROM evaluation.swell_readings
WHERE location = 'rockaways'
ORDER BY timestamp DESC
LIMIT 20;
```

---

## Roadmap

### Completed
- [x] Surfline LOTUS collection — `collect_surfline.py`
- [x] Supabase Postgres storage with `evaluation` schema isolation
- [x] GitHub Actions automation (cron, dual-timezone schedule)
- [x] Cloudflare Worker proxy (replaced ScrapingBee trial)
- [x] Units normalization (meters → feet detection and conversion)
- [x] Swell slot ordering by impact (not height)
- [x] `--dry-run` mode for testing without DB writes

### Next
- [ ] `evaluate.py` — comparison engine: query Surfline ground truth, score any model's predictions via MAE/bias/variance, stratified by swell size and period
- [ ] `fetch/ndbc.py` — NOAA buoy data fetcher
- [ ] `models/model_0_buoy.py` — baseline: raw NDBC buoy height vs Surfline
- [ ] `models/model_1_shoaling.py` — Green's Law shoaling correction using `breaking_wave_depth` from `surf_spots`
- [ ] `fetch/ww3.py` — WaveWatch III via NOAA OPeNDAP
- [ ] `models/model_2_ww3.py` — WW3 directional spectrum + refraction coefficient
- [ ] `fetch/cdip.py` — CDIP nearshore buoy data (California spots only)
- [ ] `models/model_3_cdip.py` — CDIP nearshore buoy where available
- [ ] Conditional ensemble logic — Model 3 when available, fall back to Model 2

---

## Important notes

- The Surfline API is undocumented and unofficial. It may change without notice.
- Meaningful model training requires at least 2–3 months of readings across diverse conditions.
- The `raw_data` JSONB column is intentional — it allows reprocessing historical rows if parsing logic changes without re-fetching from Surfline.