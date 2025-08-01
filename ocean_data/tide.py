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
        print(f"DEBUG: df_water_level after get_data:\n{df_water_level.head()}")

        if df_water_level.empty:
            print("DEBUG: df_water_level is empty after get_data.")
            return None

        # Ensure the DataFrame index is timezone-aware UTC for comparison
        if df_water_level.index.tz is None:
            df_water_level.index = df_water_level.index.tz_localize(timezone.utc)
        else:
            df_water_level.index = df_water_level.index.tz_convert(timezone.utc)
        print(f"DEBUG: df_water_level.index after tz handling:\n{df_water_level.index}")
        print(f"DEBUG: target_datetime: {target_datetime}")

        # Calculate time differences and convert to absolute seconds
        time_deltas = (df_water_level.index - target_datetime).to_series()
        print(f"DEBUG: time_deltas dtype: {time_deltas.dtype}")
        print(f"DEBUG: time_deltas before total_seconds:\n{time_deltas.head()}")
        
        # Debugging individual timedelta conversion
        if not time_deltas.empty:
            first_delta = time_deltas.iloc[0]
            print(f"DEBUG: first_delta: {first_delta}, type: {type(first_delta)}")
            print(f"DEBUG: first_delta.total_seconds(): {first_delta.total_seconds()}")

        total_seconds_series = time_deltas.dt.total_seconds()
        print(f"DEBUG: total_seconds_series before abs:\n{total_seconds_series.head()}")
        print(f"DEBUG: total_seconds_series dtype before abs: {total_seconds_series.dtype}")

        total_seconds_abs = total_seconds_series.abs()
        print(f"DEBUG: total_seconds_abs after abs:\n{total_seconds_abs.head()}")
        print(f"DEBUG: total_seconds_abs dtype after abs: {total_seconds_abs.dtype}")
        df_water_level['time_diff'] = total_seconds_abs.values
        print(f"DEBUG: df_water_level['time_diff'] before dropna:\n{df_water_level['time_diff'].head()}")

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
        return generate_dummy_tide_data(target_datetime, station_id, use_imperial_units)

    # Convert units if requested
    if use_imperial_units:
        detailed_data["water_level"] = round(meters_to_feet(detailed_data["water_level"]), 2)
        detailed_data["next_event_height"] = round(meters_to_feet(detailed_data["next_event_height"]), 2)
        detailed_data["units"] = "feet"

    return detailed_data

def fetch_historical_tide_data(station_id: str, start_date: datetime, end_date: datetime, use_imperial_units: bool = True) -> list:
    """
    Fetch a range of historical tide data from a station.
    This function remains for fetching data for tide charts.
    """
    try:
        station = coops.Station(station_id)
        begin_date_str = start_date.strftime("%Y%m%d %H:%M")
        end_date_str = end_date.strftime("%Y%m%d %H:%M")

        df_water_level = station.get_data(
            begin_date=begin_date_str,
            end_date=end_date_str,
            product="predictions",
            datum="MLLW",
            time_zone="gmt"
        )

        if df_water_level.empty:
            return []

        water_levels = []
        for index, row in df_water_level.iterrows():
            tide_obj = TideData(date=index.to_pydatetime().replace(tzinfo=timezone.utc), water_level=row['v'])
            water_levels.append(tide_obj)
        
        return water_levels

    except Exception as e:
        print(f"Error fetching historical tide data: {str(e)}")
        return []

def tide_data_list_to_json(tide_data_list, use_imperial_units=True):
    """
    Convert a list of tide data objects to a JSON-serializable list of dictionaries
    that matches the format expected by the frontend TideChart component.
    """
    tide_json = []
    if not tide_data_list:
        return tide_json
    
    for entry in tide_data_list:
        height_meters = entry.water_level
        if use_imperial_units and is_valid_data(height_meters):
            height_value = round(meters_to_feet(height_meters), 2)
            unit_str = "ft"
        else:
            height_value = height_meters
            unit_str = "meters"
            
        tide_json.append({
            "timestamp": entry.date.isoformat(),
            "tide": {
                "height": height_value,
                "unit": unit_str
            }
        })
    return tide_json

def generate_dummy_tide_data(target_datetime, station_id, use_imperial_units=True):
    """
    Generate dummy tide data for testing.
    """
    datetime_str = format_date(target_datetime)
    if use_imperial_units:
        height_value, units = 3.2, "feet"
    else:
        height_value, units = 1.0, "meters"
    
    return {
        "station_id": station_id,
        "date": datetime_str,
        "water_level": height_value,
        "direction": "rising",
        "next_event_type": "high",
        "next_event_at": (target_datetime + timedelta(hours=3)).isoformat(),
        "next_event_height": height_value + 1.0,
        "units": units
    }