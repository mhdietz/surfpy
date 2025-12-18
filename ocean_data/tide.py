"""
Ocean Data Module - Tide

This module provides functions for retrieving and processing tide data
from NOAA tide stations using the noaa-coops library for detailed tide events.
"""

from datetime import datetime, timezone, timedelta
import noaa_coops as coops
import pandas as pd

# Custom class to mimic surfpy.TideData for historical data
class TideData:
    def __init__(self, date, water_level):
        self.date = date
        self.water_level = water_level

from .utils import convert_to_utc, meters_to_feet, is_valid_data, format_date

def get_detailed_tide_data(station_id: str, target_datetime: datetime):
    """
    Fetches detailed tide information for a specific time, including water level,
    tide direction, and details of the next tide event.

    Args:
        station_id (str): The NOAA station ID.
        target_datetime (datetime): The specific time for the tide data (in UTC).

    Returns:
        dict: A dictionary with detailed tide information or None on failure.
    """
    try:
        station = coops.Station(station_id)
        target_datetime = convert_to_utc(target_datetime)

        # 1. Fetch water level for the entire day of the target_datetime
        begin_date_wl = target_datetime.replace(hour=0, minute=0, second=0, microsecond=0).strftime("%Y%m%d %H:%M")
        end_date_wl = (target_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)).strftime("%Y%m%d %H:%M")
        
        df_water_level = station.get_data(
            begin_date=begin_date_wl,
            end_date=end_date_wl,
            product="predictions",
            datum="MLLW",
            time_zone="gmt"
        )

        if df_water_level.empty:
            return None

        # Ensure the DataFrame index is timezone-aware UTC for comparison
        if df_water_level.index.tz is None:
            df_water_level.index = df_water_level.index.tz_localize(timezone.utc)
        else:
            df_water_level.index = df_water_level.index.tz_convert(timezone.utc)

        # Calculate time differences and convert to absolute seconds
        time_deltas = (df_water_level.index - target_datetime).to_series()
        total_seconds_series = time_deltas.dt.total_seconds()
        total_seconds_abs = total_seconds_series.abs()
        df_water_level['time_diff'] = total_seconds_abs.values

        current_water_level_row = df_water_level.loc[df_water_level['time_diff'].dropna().idxmin()]
        current_water_level = float(current_water_level_row['v'])

        # 2. Fetch high/low tide predictions for a 48-hour window
        begin_date_hl = target_datetime.strftime("%Y%m%d")
        end_date_hl = (target_datetime + timedelta(days=2)).strftime("%Y%m%d")

        df_hilo = station.get_data(
            begin_date=begin_date_hl,
            end_date=end_date_hl,
            product="predictions",
            datum="MLLW",
            interval="hilo",
            time_zone="gmt"
        )

        if df_hilo.empty:
            return None

        # Ensure the DataFrame index is timezone-aware UTC for comparison
        if df_hilo.index.tz is None:
            df_hilo.index = df_hilo.index.tz_localize(timezone.utc)
        else:
            df_hilo.index = df_hilo.index.tz_convert(timezone.utc)

        # 3. Find the next tide event
        next_event = None
        for index, row in df_hilo.iterrows():
            if index > target_datetime:
                next_event = row
                next_event['t'] = index
                break
        
        if next_event is None:
            return None

        # 4. Determine tide direction
        next_event_height = float(next_event['v'])
        tide_direction = "rising" if next_event_height > current_water_level else "falling"

        # 5. Format the output
        return {
            "water_level": current_water_level,
            "direction": tide_direction,
            "next_event_type": 'high' if next_event['type'] == 'H' else 'low',
            "next_event_at": next_event['t'].to_pydatetime().replace(tzinfo=timezone.utc),
            "next_event_height": next_event_height,
            "units": "meters" # Raw data is in meters
        }

    except Exception as e:
        print(f"Error in get_detailed_tide_data: {e}")
        return None

def fetch_tide_data(station_id, target_datetime=None, use_imperial_units=True):
    """
    Orchestrates fetching detailed tide data and converts units if necessary.
    This function is the main public interface for the tide module.
    """
    if target_datetime is None:
        target_datetime = datetime.now(timezone.utc)
    
    target_datetime = convert_to_utc(target_datetime)

    detailed_data = get_detailed_tide_data(station_id, target_datetime)

    if not detailed_data:
        return None

    # Convert units if requested
    if use_imperial_units:
        detailed_data["water_level"] = round(meters_to_feet(detailed_data["water_level"]), 2)
        detailed_data["next_event_height"] = round(meters_to_feet(detailed_data["next_event_height"]), 2)
        detailed_data["units"] = "feet"

    return detailed_data
