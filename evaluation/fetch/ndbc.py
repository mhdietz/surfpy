"""
evaluation/fetch/ndbc.py

Fetches NDBC buoy spectral wave data for the last 45 days and writes to
evaluation.swell_readings with source='ndbc_buoy'.

Mirrors the spot config and CLI patterns from collect_surfline.py.
Uses surfpy's BuoyStation.parse_wave_spectra_reading_data() for parsing
so the spectral decomposition is identical to the main SLAPP data pipeline.

Usage:
    python fetch/ndbc.py                        # all spots
    python fetch/ndbc.py rockaways              # one spot
    python fetch/ndbc.py --dry-run              # fetch + parse, no DB writes
    python fetch/ndbc.py rockaways --dry-run
"""

import sys
import os
import argparse
import gzip
import requests
import psycopg2
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Path setup — surfpy-clean is two levels up from evaluation/fetch/
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from surfpy.buoystation import BuoyStation

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

SPOTS = {
    'rockaways':           {'buoy_id': '44065', 'timezone': 'America/New_York',    'coast': 'east'},
    'manasquan':           {'buoy_id': '44091', 'timezone': 'America/New_York',    'coast': 'east'},
    'steamer_lane':        {'buoy_id': '46236', 'timezone': 'America/Los_Angeles', 'coast': 'west'},
    'trestles':            {'buoy_id': '46277', 'timezone': 'America/Los_Angeles', 'coast': 'west'},
    'ocean_beach_central': {'buoy_id': '46237', 'timezone': 'America/Los_Angeles', 'coast': 'west'},
}

# Time slots to capture, in local time — mirrors collect_surfline.py
TARGET_HOURS_LOCAL = [6, 9, 12, 15, 18]

# surfpy realtime2 endpoints serve ~45 days
REALTIME_COUNT = 3000  # generous count to ensure full 45-day coverage

METERS_TO_FEET = 3.28084

# ---------------------------------------------------------------------------
# NDBC fetch — uses surfpy's existing realtime2 URLs and parser
# ---------------------------------------------------------------------------

def fetch_spectra_for_buoy(buoy_id: str) -> list:
    """
    Fetch spectral wave data from NDBC realtime2 endpoints.
    Returns a list of BuoyData objects parsed by surfpy, or [] on failure.
    """
    station = BuoyStation(buoy_id, None)

    try:
        energy_response = requests.get(station.wave_energy_reading_url, timeout=30)
        directional_response = requests.get(station.directional_wave_reading_url, timeout=30)
    except requests.RequestException as e:
        print(f"  Network error fetching buoy {buoy_id}: {e}")
        return []

    if not energy_response.text.strip() or not directional_response.text.strip():
        print(f"  Empty response for buoy {buoy_id}")
        return []

    # Strip trailing blank lines — surfpy's parser tries to parse every line
    # including empty ones at the end, causing a datetime construction error
    def clean(text):
        lines = text.splitlines()
        non_empty = [l for l in lines if l.strip()]
        return '\n'.join(non_empty)

    energy_text = clean(energy_response.text)
    directional_text = clean(directional_response.text)

    raw_mod = energy_response.headers.get('Last-Modified')
    modification_date = None
    if raw_mod:
        try:
            modification_date = datetime.strptime(raw_mod, '%a, %d %b %Y %H:%M:%S %Z')
        except ValueError:
            pass

    data = BuoyStation.parse_wave_spectra_reading_data(
        energy_text,
        directional_text,
        REALTIME_COUNT,
        modification_date
    )
    return data or []


# ---------------------------------------------------------------------------
# Align buoy data to target time slots
# ---------------------------------------------------------------------------

def align_to_slots(buoy_data: list, tz_name: str, start_date: datetime) -> list:
    """
    For each calendar day from start_date to today, find the buoy reading
    closest to each TARGET_HOURS_LOCAL slot. Returns a list of dicts ready
    for DB insertion.

    buoy_data entries are BuoyData objects with a timezone-aware .date (UTC).
    """
    tz = ZoneInfo(tz_name)
    today = datetime.now(timezone.utc).date()
    results = []

    current = start_date.date()
    while current <= today:
        for hour in TARGET_HOURS_LOCAL:
            # Build the target moment in local time, convert to UTC for comparison
            local_target = datetime(current.year, current.month, current.day, hour, 0, 0, tzinfo=tz)
            utc_target = local_target.astimezone(timezone.utc)

            # Find closest buoy reading within a 3-hour window
            candidates = [
                entry for entry in buoy_data
                if abs((entry.date.replace(tzinfo=timezone.utc) - utc_target).total_seconds()) <= 10800
            ]
            if not candidates:
                continue

            closest = min(candidates, key=lambda e: abs(
                (e.date.replace(tzinfo=timezone.utc) - utc_target).total_seconds()
            ))

            results.append({
                'timestamp': utc_target,
                'buoy_data': closest,
            })

        current += timedelta(days=1)

    return results


# ---------------------------------------------------------------------------
# Map BuoyData swell components to primary/secondary/tertiary
# Sorted by height descending (no impact scores available from NDBC)
# ---------------------------------------------------------------------------

def extract_swell_slots(buoy_data_entry) -> dict:
    """
    Extract up to 3 swell components from a BuoyData object.
    Returns a flat dict of primary/secondary/tertiary fields matching
    the evaluation.swell_readings schema.
    """
    # surfpy's BuoySpectra.swell_components already sorts by max_energy descending
    # (see buoyspectra.py: components.sort(key=lambda x: x.max_energy, reverse=True))
    # so primary = highest energy component, which is the correct ordering.
    # Do NOT re-sort by height — a long-period swell carries more energy than
    # a taller short-period wind swell and should remain primary.
    components = buoy_data_entry.swell_components

    result = {}
    labels = ['primary', 'secondary', 'tertiary']

    for i, label in enumerate(labels):
        if i < len(components):
            c = components[i]
            result[f'{label}_swell_height']    = round(c.wave_height * METERS_TO_FEET, 1) if not _is_nan(c.wave_height) else None
            result[f'{label}_swell_period']    = round(c.period, 1) if c.period and not _is_nan(c.period) else None
            result[f'{label}_swell_direction'] = round(c.direction) if c.direction and not _is_nan(c.direction) else None
            result[f'{label}_swell_impact']    = None  # not available from NDBC
            result[f'{label}_swell_power']     = None  # not available from NDBC
        else:
            result[f'{label}_swell_height']    = None
            result[f'{label}_swell_period']    = None
            result[f'{label}_swell_direction'] = None
            result[f'{label}_swell_impact']    = None
            result[f'{label}_swell_power']     = None

    return result


def _is_nan(value) -> bool:
    try:
        import math
        return math.isnan(value)
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# Build a surf_min / surf_max estimate from significant wave height
# NDBC gives significant wave height (Hs) in meters via wave_summary.
# We convert to feet and use it as a rough proxy — no breaking wave
# transformation is applied here; that belongs in model_1_shoaling.py.
# ---------------------------------------------------------------------------

def estimate_surf_height(buoy_data_entry) -> dict:
    ws = buoy_data_entry.wave_summary
    if ws and ws.wave_height and not _is_nan(ws.wave_height):
        hs_ft = round(ws.wave_height * METERS_TO_FEET, 1)
        return {'surf_min': hs_ft, 'surf_max': hs_ft}
    return {'surf_min': None, 'surf_max': None}


# ---------------------------------------------------------------------------
# DB write
# ---------------------------------------------------------------------------

def write_to_db(conn, spot_name: str, buoy_id: str, rows: list) -> tuple[int, int]:
    """
    Insert rows into evaluation.swell_readings.
    Returns (inserted, skipped) counts.
    Skips duplicates via the unique constraint on (source, location, timestamp).
    """
    inserted = 0
    skipped = 0

    with conn.cursor() as cur:
        for row in rows:
            entry = row['buoy_data']
            swells = extract_swell_slots(entry)
            surf = estimate_surf_height(entry)

            try:
                cur.execute("""
                    INSERT INTO evaluation.swell_readings (
                        source, location, spot_id, timestamp,
                        surf_min, surf_max, surf_optimal_score,
                        primary_swell_height,    primary_swell_period,    primary_swell_direction,    primary_swell_impact,    primary_swell_power,
                        secondary_swell_height,  secondary_swell_period,  secondary_swell_direction,  secondary_swell_impact,  secondary_swell_power,
                        tertiary_swell_height,   tertiary_swell_period,   tertiary_swell_direction,   tertiary_swell_impact,   tertiary_swell_power,
                        raw_data
                    ) VALUES (
                        'ndbc_buoy', %s, %s, %s,
                        %s, %s, NULL,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        NULL
                    )
                    ON CONFLICT (source, location, timestamp) DO NOTHING
                """, (
                    spot_name, buoy_id, row['timestamp'],
                    surf['surf_min'], surf['surf_max'],
                    swells['primary_swell_height'],   swells['primary_swell_period'],   swells['primary_swell_direction'],   swells['primary_swell_impact'],   swells['primary_swell_power'],
                    swells['secondary_swell_height'],  swells['secondary_swell_period'],  swells['secondary_swell_direction'],  swells['secondary_swell_impact'],  swells['secondary_swell_power'],
                    swells['tertiary_swell_height'],   swells['tertiary_swell_period'],   swells['tertiary_swell_direction'],   swells['tertiary_swell_impact'],   swells['tertiary_swell_power'],
                ))

                if cur.rowcount > 0:
                    inserted += 1
                else:
                    skipped += 1

            except Exception as e:
                print(f"  DB error on row {row['timestamp']}: {e}")
                conn.rollback()
                skipped += 1
                continue

    conn.commit()
    return inserted, skipped


# ---------------------------------------------------------------------------
# Per-spot orchestration
# ---------------------------------------------------------------------------

def process_spot(spot_name: str, dry_run: bool, conn) -> None:
    config = SPOTS[spot_name]
    buoy_id = config['buoy_id']
    tz_name = config['timezone']

    print(f"\n{'='*50}")
    print(f"Spot: {spot_name}  |  Buoy: {buoy_id}  |  TZ: {tz_name}")
    print(f"{'='*50}")

    # Fetch raw buoy data
    print(f"  Fetching spectra from NDBC realtime2...")
    buoy_data = fetch_spectra_for_buoy(buoy_id)

    if not buoy_data:
        print(f"  No data returned for buoy {buoy_id}. Skipping.")
        return

    # Determine available date range from fetched data
    dates = [e.date.replace(tzinfo=timezone.utc) for e in buoy_data]
    earliest = min(dates)
    latest = max(dates)
    print(f"  Fetched {len(buoy_data)} readings  |  {earliest.date()} → {latest.date()}")

    # Align to 5 daily time slots, going back as far as data allows
    rows = align_to_slots(buoy_data, tz_name, earliest)
    print(f"  Aligned to {len(rows)} slot-matched readings")

    if dry_run:
        # Print a sample without writing
        print(f"  DRY RUN — sample of first 3 rows:")
        for row in rows[:3]:
            entry = row['buoy_data']
            swells = extract_swell_slots(entry)
            surf = estimate_surf_height(entry)
            print(f"    {row['timestamp'].isoformat()}  surf={surf}  primary={swells['primary_swell_height']}ft @ {swells['primary_swell_period']}s {swells['primary_swell_direction']}°")
        return

    # Write to DB
    inserted, skipped = write_to_db(conn, spot_name, buoy_id, rows)
    print(f"  Inserted: {inserted}  |  Skipped (duplicates): {skipped}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Fetch NDBC buoy data into evaluation.swell_readings')
    parser.add_argument('spot', nargs='?', default=None, help='Spot name (default: all spots)')
    parser.add_argument('--dry-run', action='store_true', help='Fetch and parse without writing to DB')
    args = parser.parse_args()

    # Resolve target spots
    if args.spot:
        if args.spot not in SPOTS:
            print(f"Unknown spot '{args.spot}'. Valid options: {', '.join(SPOTS.keys())}")
            sys.exit(1)
        target_spots = [args.spot]
    else:
        target_spots = list(SPOTS.keys())

    # DB connection (skip if dry run)
    conn = None
    if not args.dry_run:
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            print("DATABASE_URL not set. Add it to evaluation/.env or environment.")
            sys.exit(1)
        try:
            conn = psycopg2.connect(db_url)
            print("Connected to database.")
        except Exception as e:
            print(f"Database connection failed: {e}")
            sys.exit(1)

    try:
        for spot_name in target_spots:
            process_spot(spot_name, args.dry_run, conn)
    finally:
        if conn:
            conn.close()

    print("\nDone.")


if __name__ == '__main__':
    main()