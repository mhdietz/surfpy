"""
collect_surfline.py
-------------------
Collects Surfline LOTUS forecast data for configured surf spots and stores it
in Postgres (Supabase) for use as ground-truth in model evaluation.

Intentionally self-contained — no imports from the main SLAPP codebase.
Connects to the same Supabase instance as SLAPP but writes only to the
evaluation.swell_readings table, which is fully separate from app tables.

Usage:
    python collect_surfline.py                  # all spots, today
    python collect_surfline.py lido             # one spot, today
    python collect_surfline.py lido 2025-08-15  # one spot, specific date

Environment variables:
    DATABASE_URL  — standard psycopg2 connection string
                    e.g. postgresql://user:pass@host:5432/dbname
                    Loaded from .env if present, otherwise from environment.

The Surfline API is undocumented and unauthenticated. Responses may change.
This script targets the /kbyg/spots/forecasts/wave endpoint.
"""

import os
import sys
import json
import logging
from datetime import datetime, date, time
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Load .env if present (local dev). In GitHub Actions the secret is injected
# directly into the environment, so this is a no-op there.
load_dotenv(Path(__file__).parent / ".env")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SPOTS = {
    "rockaways":            "5842041f4e65fad6a7708852",
    "manasquan":            "5842041f4e65fad6a7708856",
    "steamer_lane":         "5842041f4e65fad6a7708805",
    "trestles":             "5842041f4e65fad6a770888a",
    "ocean_beach_central":  "638e32a4f052ba4ed06d0e3e",
}

SPOT_TIMEZONES = {
    "rockaways":            "America/New_York",
    "manasquan":            "America/New_York",
    "steamer_lane":         "America/Los_Angeles",
    "trestles":             "America/Los_Angeles",
    "ocean_beach_central":  "America/Los_Angeles",
}

# Five snapshots covering the full surfable day, always past by 8pm local
TARGET_TIMES = [
    time(6, 0),
    time(9, 0),
    time(12, 0),
    time(15, 0),
    time(18, 0),
]

SURFLINE_BASE = "https://services.surfline.com/kbyg/spots/forecasts/wave"

M_TO_FT = 3.28084

# ---------------------------------------------------------------------------
# Units normalization
# ---------------------------------------------------------------------------

def is_meters(surf_min) -> bool:
    """
    Surfline returns whole numbers when units are feet, decimals when meters.
    If surf_min has a fractional component, treat the entire reading as meters.
    """
    if surf_min is None:
        return False
    return surf_min != int(surf_min)


def normalize_to_feet(parsed: dict) -> dict:
    """
    Convert all height fields from meters to feet in-place.
    Called only when is_meters() returns True.
    surf_min/surf_max rounded to whole numbers; swell heights to 1 decimal.
    """
    surf_fields = ["surf_min", "surf_max"]
    swell_fields = [
        "primary_swell_height",
        "secondary_swell_height",
        "tertiary_swell_height",
    ]
    for field in surf_fields:
        if parsed.get(field) is not None:
            parsed[field] = round(parsed[field] * M_TO_FT)
    for field in swell_fields:
        if parsed.get(field) is not None:
            parsed[field] = round(parsed[field] * M_TO_FT, 1)
    direction_fields = [
        "primary_swell_direction",
        "secondary_swell_direction",
        "tertiary_swell_direction",
    ]
    for field in direction_fields:
        if parsed.get(field) is not None:
            parsed[field] = round(parsed[field])
    log.debug("Normalized reading from meters to feet.")
    return parsed


def round_heights(parsed: dict) -> dict:
    """
    Apply rounding to readings already in feet.
    surf_min/surf_max to whole numbers; swell heights to 1 decimal;
    swell directions to nearest degree.
    """
    surf_fields = ["surf_min", "surf_max"]
    swell_fields = [
        "primary_swell_height",
        "secondary_swell_height",
        "tertiary_swell_height",
    ]
    direction_fields = [
        "primary_swell_direction",
        "secondary_swell_direction",
        "tertiary_swell_direction",
    ]
    for field in surf_fields:
        if parsed.get(field) is not None:
            parsed[field] = round(parsed[field])
    for field in swell_fields:
        if parsed.get(field) is not None:
            parsed[field] = round(parsed[field], 1)
    for field in direction_fields:
        if parsed.get(field) is not None:
            parsed[field] = round(parsed[field])
    return parsed


# ---------------------------------------------------------------------------
# Database — Postgres
# ---------------------------------------------------------------------------

CREATE_TABLE_SQL = """
CREATE SCHEMA IF NOT EXISTS evaluation;

CREATE TABLE IF NOT EXISTS evaluation.swell_readings (
    id                          SERIAL PRIMARY KEY,
    source                      TEXT        NOT NULL,
    location                    TEXT        NOT NULL,
    spot_id                     TEXT        NOT NULL,
    timestamp                   TIMESTAMPTZ NOT NULL,
    surf_min                    REAL,
    surf_max                    REAL,
    surf_optimal_score          INTEGER,
    primary_swell_height        REAL,
    primary_swell_period        REAL,
    primary_swell_direction     REAL,
    primary_swell_impact        REAL,
    primary_swell_power         REAL,
    secondary_swell_height      REAL,
    secondary_swell_period      REAL,
    secondary_swell_direction   REAL,
    secondary_swell_impact      REAL,
    secondary_swell_power       REAL,
    tertiary_swell_height       REAL,
    tertiary_swell_period       REAL,
    tertiary_swell_direction    REAL,
    tertiary_swell_impact       REAL,
    tertiary_swell_power        REAL,
    raw_data                    JSONB,
    created_at                  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (source, location, timestamp)
);

CREATE INDEX IF NOT EXISTS idx_eval_location_ts
    ON evaluation.swell_readings (location, timestamp);
"""


def get_db():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        log.error("DATABASE_URL environment variable not set.")
        sys.exit(1)
    try:
        conn = psycopg2.connect(database_url)
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
        conn.commit()
        log.info("Connected to Postgres and schema ready.")
        return conn
    except psycopg2.OperationalError as exc:
        log.error("Could not connect to Postgres: %s", exc)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Surfline API
# ---------------------------------------------------------------------------

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": "https://www.surfline.com/",
}

SCRAPINGBEE_URL = "https://app.scrapingbee.com/api/v1/"


def fetch_surfline(spot_id: str, days: int = 2) -> list[dict]:
    """
    Fetch hourly wave forecast from Surfline.

    Uses ScrapingBee as a proxy when SCRAPINGBEE_API_KEY is set (required for
    GitHub Actions to avoid Surfline 403s from datacenter IPs). Falls back to
    direct requests when running locally without the key.
    """
    target_url = (
        f"{SURFLINE_BASE}?spotId={spot_id}&days={days}&intervalHours=1"
    )
    api_key = os.environ.get("SCRAPINGBEE_API_KEY")

    try:
        if api_key:
            # Route through ScrapingBee residential proxy
            resp = requests.get(
                SCRAPINGBEE_URL,
                params={
                    "api_key": api_key,
                    "url": target_url,
                    "render_js": "false",      # No JS rendering needed, saves credits
                    "premium_proxy": "false",  # Standard proxy sufficient for Surfline
                },
                timeout=30,
            )
            log.debug("ScrapingBee request for spot %s — status %s", spot_id, resp.status_code)
        else:
            # Direct request — works fine locally
            resp = requests.get(SURFLINE_BASE, params={
                "spotId": spot_id, "days": days, "intervalHours": 1
            }, headers=HEADERS, timeout=15)

        resp.raise_for_status()
        data = resp.json()
        return data.get("data", {}).get("wave", [])
    except requests.RequestException as exc:
        log.error("Surfline API request failed for spot %s: %s", spot_id, exc)
        return []
    except (KeyError, ValueError) as exc:
        log.error("Unexpected Surfline response shape for spot %s: %s", spot_id, exc)
        return []


# ---------------------------------------------------------------------------
# Filtering & processing
# ---------------------------------------------------------------------------

def utc_timestamp_to_dt(unix_ts: int) -> datetime:
    return datetime.fromtimestamp(unix_ts, tz=ZoneInfo("UTC"))


def find_closest_reading(wave_data, target_local, tolerance_minutes=59):
    target_utc = target_local.astimezone(ZoneInfo("UTC"))
    best = None
    best_diff = None
    for reading in wave_data:
        ts = reading.get("timestamp")
        if ts is None:
            continue
        diff = abs((utc_timestamp_to_dt(ts) - target_utc).total_seconds())
        if diff <= tolerance_minutes * 60:
            if best_diff is None or diff < best_diff:
                best = reading
                best_diff = diff
    return best


def select_target_readings(wave_data, target_date, tz_name):
    tz = ZoneInfo(tz_name)
    results = []
    for t in TARGET_TIMES:
        local_dt = datetime.combine(target_date, t, tzinfo=tz)
        reading = find_closest_reading(wave_data, local_dt)
        if reading:
            results.append((t, reading))
            log.info("  ✓ Found reading for %s local → %s UTC",
                     t.strftime("%H:%M"),
                     utc_timestamp_to_dt(reading["timestamp"]).isoformat())
        else:
            log.warning("  ✗ No reading within tolerance for %s local", t.strftime("%H:%M"))
    return results


def parse_reading(reading: dict) -> dict:
    """
    Sort swells by impact descending, skip zero-height placeholders.
    Primary = most influential swell at this specific break.
    Normalizes height fields to feet if Surfline returns meters
    (detected via fractional surf_min).
    """
    surf = reading.get("surf", {})
    active_swells = sorted(
        [s for s in reading.get("swells", []) if s.get("height", 0) > 0],
        key=lambda s: s.get("impact", 0),
        reverse=True,
    )

    def sf(index, field):
        try:
            val = active_swells[index].get(field)
            return val if (field in ("impact", "power") or val) else None
        except IndexError:
            return None

    parsed = {
        "surf_min":                 surf.get("min"),
        "surf_max":                 surf.get("max"),
        "surf_optimal_score":       surf.get("optimalScore"),
        "primary_swell_height":     sf(0, "height"),
        "primary_swell_period":     sf(0, "period"),
        "primary_swell_direction":  sf(0, "direction"),
        "primary_swell_impact":     sf(0, "impact"),
        "primary_swell_power":      sf(0, "power"),
        "secondary_swell_height":   sf(1, "height"),
        "secondary_swell_period":   sf(1, "period"),
        "secondary_swell_direction":sf(1, "direction"),
        "secondary_swell_impact":   sf(1, "impact"),
        "secondary_swell_power":    sf(1, "power"),
        "tertiary_swell_height":    sf(2, "height"),
        "tertiary_swell_period":    sf(2, "period"),
        "tertiary_swell_direction": sf(2, "direction"),
        "tertiary_swell_impact":    sf(2, "impact"),
        "tertiary_swell_power":     sf(2, "power"),
    }

    # Normalize to feet if Surfline returned meters, otherwise just round
    if is_meters(parsed["surf_min"]):
        parsed = normalize_to_feet(parsed)
    else:
        parsed = round_heights(parsed)

    return parsed


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

INSERT_SQL = """
INSERT INTO evaluation.swell_readings (
    source, location, spot_id, timestamp,
    surf_min, surf_max, surf_optimal_score,
    primary_swell_height, primary_swell_period, primary_swell_direction,
    primary_swell_impact, primary_swell_power,
    secondary_swell_height, secondary_swell_period, secondary_swell_direction,
    secondary_swell_impact, secondary_swell_power,
    tertiary_swell_height, tertiary_swell_period, tertiary_swell_direction,
    tertiary_swell_impact, tertiary_swell_power,
    raw_data
) VALUES (
    'surfline_lotus', %(location)s, %(spot_id)s, %(timestamp)s,
    %(surf_min)s, %(surf_max)s, %(surf_optimal_score)s,
    %(primary_swell_height)s, %(primary_swell_period)s, %(primary_swell_direction)s,
    %(primary_swell_impact)s, %(primary_swell_power)s,
    %(secondary_swell_height)s, %(secondary_swell_period)s, %(secondary_swell_direction)s,
    %(secondary_swell_impact)s, %(secondary_swell_power)s,
    %(tertiary_swell_height)s, %(tertiary_swell_period)s, %(tertiary_swell_direction)s,
    %(tertiary_swell_impact)s, %(tertiary_swell_power)s,
    %(raw_data)s
)
ON CONFLICT (source, location, timestamp) DO NOTHING;
"""


def save_reading(conn, location, spot_id, reading) -> bool:
    ts_utc = utc_timestamp_to_dt(reading["timestamp"])
    params = {
        "location": location,
        "spot_id": spot_id,
        "timestamp": ts_utc,
        "raw_data": json.dumps(reading),
        **parse_reading(reading),
    }
    try:
        with conn.cursor() as cur:
            cur.execute(INSERT_SQL, params)
            inserted = cur.rowcount == 1
        conn.commit()
        if not inserted:
            log.debug("Duplicate reading for %s @ %s — skipped", location, ts_utc)
        return inserted
    except psycopg2.Error as exc:
        conn.rollback()
        log.error("DB error saving reading for %s @ %s: %s", location, ts_utc, exc)
        return False


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------

def collect_spot(spot_name, target_date, conn) -> int:
    spot_id = SPOTS[spot_name]
    tz_name = SPOT_TIMEZONES[spot_name]
    # If no date specified, use today in the spot's local timezone — not UTC.
    # This matters when the script runs after midnight UTC but is still
    # the same evening locally (e.g. 8pm PT = 4am UTC next day).
    if target_date is None:
        target_date = datetime.now(tz=ZoneInfo(tz_name)).date()
    log.info("Collecting %s (spot_id=%s) for %s", spot_name, spot_id, target_date)

    wave_data = fetch_surfline(spot_id)
    if not wave_data:
        log.warning("No data returned for %s", spot_name)
        return 0

    readings = select_target_readings(wave_data, target_date, tz_name)
    saved = 0
    for target_time, reading in readings:
        if save_reading(conn, spot_name, spot_id, reading):
            saved += 1
            log.info("  → Saved %s @ %s local", spot_name, target_time.strftime("%H:%M"))

    log.info("  %d/%d readings saved for %s", saved, len(readings), spot_name)
    return saved


def collect_all(target_date, conn) -> int:
    total = sum(collect_spot(name, target_date, conn) for name in SPOTS)
    log.info("Done. %d total readings saved.", total)
    return total


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    args = sys.argv[1:]
    target_date = None  # Each spot will resolve to its own local date
    spot_names = list(SPOTS.keys())

    if not args:
        return spot_names, target_date

    if args[0] in SPOTS:
        spot_names = [args[0]]
        if len(args) >= 2:
            try:
                target_date = date.fromisoformat(args[1])
            except ValueError:
                log.error("Invalid date '%s'. Use YYYY-MM-DD.", args[1])
                sys.exit(1)
    else:
        try:
            target_date = date.fromisoformat(args[0])
        except ValueError:
            log.error("Unknown spot '%s'. Available: %s", args[0], ", ".join(SPOTS.keys()))
            sys.exit(1)

    return spot_names, target_date


def main():
    spot_names, target_date = parse_args()
    conn = get_db()
    log.info("Date: %s | Spots: %s", target_date, ", ".join(spot_names))
    if len(spot_names) == 1:
        collect_spot(spot_names[0], target_date, conn)
    else:
        collect_all(target_date, conn)
    conn.close()


if __name__ == "__main__":
    main()