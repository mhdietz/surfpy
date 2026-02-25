"""
collect_surfline.py
-------------------
Collects Surfline LOTUS forecast data for configured surf spots and stores it
in a local SQLite database for use as ground-truth in model evaluation.

Replaces the pysurfline-based collect_surfline_lotus.py with direct API calls
so it runs identically in VSCode, PyCharm, or any Python 3.8+ environment.

Usage:
    python collect_surfline.py                  # all spots, today
    python collect_surfline.py lido             # one spot, today
    python collect_surfline.py lido 2025-08-15  # one spot, specific date

The Surfline API is undocumented and unauthenticated. Responses may change.
This script targets the /kbyg/spots/forecasts/wave endpoint.
"""

import sys
import json
import sqlite3
import logging
from datetime import datetime, date, time
from pathlib import Path
from zoneinfo import ZoneInfo  # stdlib in Python 3.9+; use `pip install backports.zoneinfo` for 3.8

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# Database lives next to this script inside evaluation/
DB_PATH = Path(__file__).parent / "swell_data.db"

# Surfline spot IDs — add more spots here as needed
SPOTS = {
    "rockaways":    "5842041f4e65fad6a7708852",
    "lido":         "5842041f4e65fad6a77089e2",
    "belmar":       "5842041f4e65fad6a7708a01",
    "manasquan":    "5842041f4e65fad6a7708856",
    "steamer_lane": "5842041f4e65fad6a7708805",
    "trestles":     "5842041f4e65fad6a770888a",
}

# Timezone per spot — extend when adding new spots
SPOT_TIMEZONES = {
    "rockaways":    "America/New_York",
    "lido":         "America/New_York",
    "belmar":       "America/New_York",
    "manasquan":    "America/New_York",
    "steamer_lane": "America/Los_Angeles",
    "trestles":     "America/Los_Angeles",
}

# Local times to capture each day (hour, minute)
TARGET_TIMES = [
    time(6, 0),
    time(12, 0),
    time(18, 0),
]

# Surfline API base
SURFLINE_BASE = "https://services.surfline.com/kbyg/spots/forecasts/wave"

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
# Database
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS swell_readings (
    id                          INTEGER PRIMARY KEY AUTOINCREMENT,
    source                      TEXT    NOT NULL,
    location                    TEXT    NOT NULL,
    spot_id                     TEXT    NOT NULL,
    timestamp                   TEXT    NOT NULL,   -- ISO 8601 UTC
    surf_min                    REAL,               -- Surfline min surf height (ft)
    surf_max                    REAL,               -- Surfline max surf height (ft)
    surf_optimal_score          INTEGER,            -- 0, 1, or 2
    -- Swells sorted by impact descending (most influential swell at this break first)
    primary_swell_height        REAL,
    primary_swell_period        REAL,
    primary_swell_direction     REAL,
    primary_swell_impact        REAL,               -- Surfline impact score (0-1)
    primary_swell_power         REAL,               -- Surfline power value
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
    raw_data                    TEXT,               -- full JSON from Surfline
    created_at                  TEXT    DEFAULT (datetime('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_source_location_ts
    ON swell_readings (source, location, timestamp);

CREATE INDEX IF NOT EXISTS idx_location_ts
    ON swell_readings (location, timestamp);
"""

# Columns added in schema v2 — applied via ALTER TABLE if upgrading an existing DB
MIGRATION_COLUMNS = [
    ("primary_swell_impact",      "REAL"),
    ("primary_swell_power",       "REAL"),
    ("secondary_swell_impact",    "REAL"),
    ("secondary_swell_power",     "REAL"),
    ("tertiary_swell_height",     "REAL"),
    ("tertiary_swell_period",     "REAL"),
    ("tertiary_swell_direction",  "REAL"),
    ("tertiary_swell_impact",     "REAL"),
    ("tertiary_swell_power",      "REAL"),
]


def get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)

    # Migrate existing DB: add any columns introduced in v2 that don't exist yet
    existing = {row[1] for row in conn.execute("PRAGMA table_info(swell_readings)")}
    for col_name, col_type in MIGRATION_COLUMNS:
        if col_name not in existing:
            conn.execute(f"ALTER TABLE swell_readings ADD COLUMN {col_name} {col_type}")
            log.info("Migration: added column %s", col_name)

    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Surfline API
# ---------------------------------------------------------------------------

HEADERS = {
    # Mimic a browser request — Surfline doesn't require auth for basic forecasts
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": "https://www.surfline.com/",
}


def fetch_surfline(spot_id: str, days: int = 2) -> list[dict]:
    """
    Fetch hourly wave forecast from Surfline for a given spot.
    Returns the raw list of wave data dicts, or [] on failure.

    We request 2 days so that when running near midnight we still
    capture today's 6/12/18 windows regardless of timezone offsets.
    """
    params = {
        "spotId": spot_id,
        "days": days,
        "intervalHours": 1,
    }
    try:
        resp = requests.get(SURFLINE_BASE, params=params, headers=HEADERS, timeout=15)
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
    """Convert a Unix timestamp (UTC) to a timezone-aware UTC datetime."""
    return datetime.fromtimestamp(unix_ts, tz=ZoneInfo("UTC"))


def find_closest_reading(
    wave_data: list[dict],
    target_local: datetime,
    tolerance_minutes: int = 59,
) -> dict | None:
    """
    Find the wave reading closest to target_local time within tolerance.
    target_local must be a timezone-aware datetime.
    """
    target_utc = target_local.astimezone(ZoneInfo("UTC"))
    best = None
    best_diff = None

    for reading in wave_data:
        ts = reading.get("timestamp")
        if ts is None:
            continue
        reading_utc = utc_timestamp_to_dt(ts)
        diff = abs((reading_utc - target_utc).total_seconds())
        if diff <= tolerance_minutes * 60:
            if best_diff is None or diff < best_diff:
                best = reading
                best_diff = diff

    return best


def select_target_readings(
    wave_data: list[dict],
    target_date: date,
    tz_name: str,
) -> list[tuple[time, dict]]:
    """
    Return readings closest to each TARGET_TIME on target_date in local tz.
    """
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
    Extract structured fields from a single Surfline wave reading.

    Surfline returns exactly 6 swell slots, padded with zeroes. The array order
    is NOT sorted by size — it reflects break-specific impact ranking, which can
    put the dominant swell at any index. We filter out zero-height placeholders
    and sort by `impact` descending so primary is always the most influential
    swell at this specific break, regardless of array position.
    """
    surf = reading.get("surf", {})
    raw_swells = reading.get("swells", [])

    # Filter out empty placeholder slots (height=0) and sort by impact desc
    active_swells = sorted(
        [s for s in raw_swells if s.get("height", 0) > 0],
        key=lambda s: s.get("impact", 0),
        reverse=True,
    )

    def swell_field(index: int, field: str):
        try:
            val = active_swells[index].get(field)
            # Return None for zero values on directional/period fields to avoid
            # storing misleading zeros, but keep 0 for impact/power (valid value)
            if field in ("impact", "power"):
                return val
            return val if val else None
        except IndexError:
            return None

    return {
        "surf_min":                   surf.get("min"),
        "surf_max":                   surf.get("max"),
        "surf_optimal_score":         surf.get("optimalScore"),
        # Primary = highest impact swell for this break
        "primary_swell_height":       swell_field(0, "height"),
        "primary_swell_period":       swell_field(0, "period"),
        "primary_swell_direction":    swell_field(0, "direction"),
        "primary_swell_impact":       swell_field(0, "impact"),
        "primary_swell_power":        swell_field(0, "power"),
        # Secondary
        "secondary_swell_height":     swell_field(1, "height"),
        "secondary_swell_period":     swell_field(1, "period"),
        "secondary_swell_direction":  swell_field(1, "direction"),
        "secondary_swell_impact":     swell_field(1, "impact"),
        "secondary_swell_power":      swell_field(1, "power"),
        # Tertiary
        "tertiary_swell_height":      swell_field(2, "height"),
        "tertiary_swell_period":      swell_field(2, "period"),
        "tertiary_swell_direction":   swell_field(2, "direction"),
        "tertiary_swell_impact":      swell_field(2, "impact"),
        "tertiary_swell_power":       swell_field(2, "power"),
    }


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def save_reading(
    conn: sqlite3.Connection,
    location: str,
    spot_id: str,
    reading: dict,
) -> bool:
    """
    Insert a single reading. Returns True if inserted, False if duplicate.
    """
    ts_utc = utc_timestamp_to_dt(reading["timestamp"]).isoformat()
    p = parse_reading(reading)
    raw = json.dumps(reading)

    try:
        conn.execute(
            """
            INSERT INTO swell_readings (
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
                'surfline_lotus', ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?
            )
            """,
            (
                location, spot_id, ts_utc,
                p["surf_min"], p["surf_max"], p["surf_optimal_score"],
                p["primary_swell_height"], p["primary_swell_period"],
                p["primary_swell_direction"], p["primary_swell_impact"],
                p["primary_swell_power"],
                p["secondary_swell_height"], p["secondary_swell_period"],
                p["secondary_swell_direction"], p["secondary_swell_impact"],
                p["secondary_swell_power"],
                p["tertiary_swell_height"], p["tertiary_swell_period"],
                p["tertiary_swell_direction"], p["tertiary_swell_impact"],
                p["tertiary_swell_power"],
                raw,
            ),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        log.debug("Duplicate reading for %s @ %s — skipped", location, ts_utc)
        return False


# ---------------------------------------------------------------------------
# Main collection logic
# ---------------------------------------------------------------------------

def collect_spot(spot_name: str, target_date: date, conn: sqlite3.Connection) -> int:
    """Collect and store target readings for one spot. Returns number saved."""
    spot_id = SPOTS[spot_name]
    tz_name = SPOT_TIMEZONES[spot_name]

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


def collect_all(target_date: date, conn: sqlite3.Connection):
    """Collect all configured spots for target_date."""
    total = 0
    for spot_name in SPOTS:
        total += collect_spot(spot_name, target_date, conn)
    log.info("Done. %d total readings saved.", total)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def parse_args() -> tuple[list[str], date]:
    """
    Parse CLI args. Returns (spot_names, target_date).
    spot_names is all spots if no spot specified.
    """
    args = sys.argv[1:]

    target_date = date.today()
    spot_names = list(SPOTS.keys())

    if not args:
        return spot_names, target_date

    # First arg: spot name or date
    if args[0] in SPOTS:
        spot_names = [args[0]]
        if len(args) >= 2:
            try:
                target_date = date.fromisoformat(args[1])
            except ValueError:
                log.error("Invalid date '%s'. Use YYYY-MM-DD.", args[1])
                sys.exit(1)
    else:
        # Try parsing as a date (run all spots for that date)
        try:
            target_date = date.fromisoformat(args[0])
        except ValueError:
            log.error(
                "Unknown spot '%s'. Available: %s",
                args[0], ", ".join(SPOTS.keys())
            )
            sys.exit(1)

    return spot_names, target_date


def main():
    spot_names, target_date = parse_args()
    conn = get_db()

    log.info("DB: %s", DB_PATH)
    log.info("Date: %s | Spots: %s", target_date, ", ".join(spot_names))

    if len(spot_names) == 1:
        collect_spot(spot_names[0], target_date, conn)
    else:
        collect_all(target_date, conn)

    conn.close()


if __name__ == "__main__":
    main()