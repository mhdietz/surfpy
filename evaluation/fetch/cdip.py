"""
evaluation/fetch/cdip.py

Fetches CDIP nearshore buoy wave data and writes to evaluation.swell_readings
with source='cdip_buoy'. Mirrors the spot config, slot-alignment, and CLI
patterns from fetch/ndbc.py and collect_surfline.py.

CDIP stations only cover the California spots in SPOTS below — CDIP has no
East Coast presence among rockaways/manasquan, so this fetcher only targets
steamer_lane, trestles, and ocean_beach_central. Station IDs are the ones
partiwave already validated (steamer_lane's original CDIP 158 was found
decommissioned and substituted with 254).

CDIP gives one dominant wave height/period/direction per reading (not a full
spectral decomposition into primary/secondary/tertiary components the way
NDBC's BuoySpectra does) — only primary_swell_* columns are populated here;
secondary/tertiary stay NULL.

Usage:
    python fetch/cdip.py                        # all CDIP spots
    python fetch/cdip.py steamer_lane            # one spot
    python fetch/cdip.py --dry-run               # fetch + parse, no DB writes
    python fetch/cdip.py steamer_lane --dry-run
"""

import sys
import os
import argparse
import psycopg2
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

from howsit import fetch_cdip_window

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

SPOTS = {
    'steamer_lane':        {'station_id': '254', 'timezone': 'America/Los_Angeles'},
    'trestles':            {'station_id': '284', 'timezone': 'America/Los_Angeles'},
    'ocean_beach_central': {'station_id': '142', 'timezone': 'America/Los_Angeles'},
}

# Time slots to capture, in local time — mirrors collect_surfline.py / fetch/ndbc.py
TARGET_HOURS_LOCAL = [6, 9, 12, 15, 18]
SLOT_TOLERANCE_SECONDS = 3 * 3600  # matches fetch/ndbc.py's ±3hr window

# CDIP realtime buoys report roughly every 30min; 350 samples ~ 7 days,
# comfortably covering a week between (at minimum weekly) collection runs.
WINDOW_COUNT = 350


def align_to_slots(readings: list, tz_name: str) -> list:
    """
    For each calendar day spanned by `readings`, find the reading closest to
    each TARGET_HOURS_LOCAL slot. Returns a list of {'timestamp': utc_target,
    'reading': reading_dict}.
    """
    tz = ZoneInfo(tz_name)
    parsed = [
        {**r, '_dt': datetime.fromisoformat(r['observed_at'])}
        for r in readings
    ]
    if not parsed:
        return []

    start_date = min(r['_dt'] for r in parsed).date()
    today = datetime.now(timezone.utc).date()
    results = []

    current = start_date
    while current <= today:
        for hour in TARGET_HOURS_LOCAL:
            local_target = datetime(current.year, current.month, current.day, hour, 0, 0, tzinfo=tz)
            utc_target = local_target.astimezone(timezone.utc)

            candidates = [
                r for r in parsed
                if abs((r['_dt'] - utc_target).total_seconds()) <= SLOT_TOLERANCE_SECONDS
            ]
            if not candidates:
                continue

            closest = min(candidates, key=lambda r: abs((r['_dt'] - utc_target).total_seconds()))
            results.append({'timestamp': utc_target, 'reading': closest})

        current += timedelta(days=1)

    return results


def write_to_db(conn, spot_name: str, station_id: str, rows: list) -> tuple:
    """Insert rows into evaluation.swell_readings. Returns (inserted, skipped)."""
    inserted = 0
    skipped = 0

    with conn.cursor() as cur:
        for row in rows:
            r = row['reading']
            height = round(r['wave_height_ft'], 1) if r['wave_height_ft'] is not None else None
            period = round(r['dominant_period_s'], 1) if r['dominant_period_s'] is not None else None
            direction = round(r['swell_direction_deg']) if r['swell_direction_deg'] is not None else None

            try:
                cur.execute("""
                    INSERT INTO evaluation.swell_readings (
                        source, location, spot_id, timestamp,
                        surf_min, surf_max, surf_optimal_score,
                        primary_swell_height, primary_swell_period, primary_swell_direction,
                        primary_swell_impact, primary_swell_power,
                        raw_data
                    ) VALUES (
                        'cdip_buoy', %s, %s, %s,
                        %s, %s, NULL,
                        %s, %s, %s,
                        NULL, NULL,
                        NULL
                    )
                    ON CONFLICT (source, location, timestamp) DO NOTHING
                """, (
                    spot_name, station_id, row['timestamp'],
                    height, height,
                    height, period, direction,
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


def process_spot(spot_name: str, dry_run: bool, conn) -> None:
    config = SPOTS[spot_name]
    station_id = config['station_id']
    tz_name = config['timezone']

    print(f"\n{'='*50}")
    print(f"Spot: {spot_name}  |  CDIP station: {station_id}  |  TZ: {tz_name}")
    print(f"{'='*50}")

    print(f"  Fetching from CDIP THREDDS/OPeNDAP...")
    try:
        readings = fetch_cdip_window(station_id, count=WINDOW_COUNT)
    except Exception as e:
        print(f"  Fetch failed for station {station_id}: {e}. Skipping.")
        return

    if not readings:
        print(f"  No data returned for station {station_id}. Skipping.")
        return

    earliest = readings[0]['observed_at']
    latest = readings[-1]['observed_at']
    print(f"  Fetched {len(readings)} readings  |  {earliest} → {latest}")

    rows = align_to_slots(readings, tz_name)
    print(f"  Aligned to {len(rows)} slot-matched readings")

    if dry_run:
        print(f"  DRY RUN — sample of first 3 rows:")
        for row in rows[:3]:
            r = row['reading']
            print(f"    {row['timestamp'].isoformat()}  primary={r['wave_height_ft']}ft @ {r['dominant_period_s']}s {r['swell_direction_deg']}°")
        return

    inserted, skipped = write_to_db(conn, spot_name, station_id, rows)
    print(f"  Inserted: {inserted}  |  Skipped (duplicates): {skipped}")


def main():
    parser = argparse.ArgumentParser(description='Fetch CDIP buoy data into evaluation.swell_readings')
    parser.add_argument('spot', nargs='?', default=None, help='Spot name (default: all CDIP spots)')
    parser.add_argument('--dry-run', action='store_true', help='Fetch and parse without writing to DB')
    args = parser.parse_args()

    if args.spot:
        if args.spot not in SPOTS:
            print(f"Unknown spot '{args.spot}'. Valid options: {', '.join(SPOTS.keys())}")
            sys.exit(1)
        target_spots = [args.spot]
    else:
        target_spots = list(SPOTS.keys())

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
