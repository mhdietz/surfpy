"""
Archived Tide Functions

This file contains functions that were previously used for fetching and processing 
the full day's tide data for generating visual charts. They have been archived 
to keep the active codebase clean while preserving the logic for potential future use.
"""

from datetime import datetime, timezone
import json

# Note: The following utility functions would need to be copied or imported from 
# the original project's `ocean_data/utils.py` if this module were to be reactivated.

def meters_to_feet(meters):
    return meters * 3.28084

def is_valid_data(value):
    return value is not None and value != 99.0

# Custom class to mimic surfpy.TideData for historical data
class TideData:
    def __init__(self, date, water_level):
        self.date = date
        self.water_level = water_level

def fetch_historical_tide_data(station_id: str, start_date: datetime, end_date: datetime, use_imperial_units: bool = True) -> list:
    """
    Fetch a range of historical tide data from a station.
    This function remains for fetching data for tide charts.
    """
    try:
        import noaa_coops as coops
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
