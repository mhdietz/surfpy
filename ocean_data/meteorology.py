"""
Ocean Data Module - Meteorology

This module provides functions for retrieving and processing meteorological data
from NDBC buoys and NOAA weather stations using the surfpy library.
"""

from datetime import datetime, timezone, timedelta
import surfpy
from surfpy.weatherapi import WeatherApi
import math

from .utils import find_closest_data, is_valid_data, convert_met_data_to_imperial

def is_weather_station(station_id: str) -> bool:
    """
    Check if the station ID is for a weather station (non-numeric) or a buoy (numeric).
    """
    return not station_id.isdigit()

def fetch_met_buoy(buoy_id):
    """
    Fetch a meteorological buoy object by ID.
    """
    try:
        stations = surfpy.BuoyStations()
        stations.fetch_stations()
        return next((s for s in stations.stations if s.station_id == buoy_id), None)
    except Exception as e:
        print(f"Error fetching met buoy: {str(e)}")
        return None

def fetch_weather_station_data(station_id, target_datetime, use_imperial_units=True):
    """
    Fetch and process meteorological data from a NOAA weather station.
    """
    try:
        if target_datetime.tzinfo is None:
            target_datetime = target_datetime.replace(tzinfo=timezone.utc)
        
        # Define a window around the target time to fetch observations
        start_time = target_datetime - timedelta(hours=1)
        end_time = target_datetime + timedelta(hours=1)

        raw_observations = WeatherApi.fetch_station_observations(station_id, start_time, end_time)
        if not raw_observations:
            print(f"No weather station observations found for {station_id}")
            return []

        met_data = WeatherApi.parse_station_observations(raw_observations)
        if not met_data:
            print(f"Failed to parse weather station data for {station_id}")
            return []

        closest_data = find_closest_data(met_data, target_datetime)
        if not closest_data:
            print(f"No matching weather station data found for time {target_datetime}")
            return []

        json_data = met_data_to_json([closest_data])
        # The parse function already returns data in imperial units (knots)
        # if use_imperial_units:
        #     json_data = convert_met_data_to_imperial(json_data)
        return json_data
    except Exception as e:
        print(f"Error fetching weather station data: {str(e)}")
        return []

def fetch_buoy_data(buoy_id, target_datetime, count=500, use_imperial_units=True):
    """
    Fetch and process meteorological data for a specific buoy and time.
    """
    try:
        if target_datetime.tzinfo is None:
            target_datetime = target_datetime.replace(tzinfo=timezone.utc)
        buoy = fetch_met_buoy(buoy_id)
        if not buoy:
            print(f"No meteorological buoy found with ID {buoy_id}")
            return []
        met_data = buoy.fetch_meteorological_reading(count)
        if not met_data:
            latest_data = buoy.fetch_latest_reading()
            if latest_data:
                met_data = [latest_data]
            else:
                print(f"No meteorological data found for buoy {buoy_id}")
                return []
        closest_data = find_closest_data(met_data, target_datetime)
        if not closest_data:
            print(f"No matching meteorological data found for time {target_datetime}")
            return []
        json_data = met_data_to_json([closest_data])
        if use_imperial_units:
            json_data = convert_met_data_to_imperial(json_data)
        return json_data
    except Exception as e:
        print(f"Error fetching meteorological data: {str(e)}")
        return []

def fetch_meteorological_data(station_id, target_datetime, count=500, use_imperial_units=True):
    """
    Fetch and process meteorological data from the appropriate source 
    (weather station or buoy) based on the station ID.
    """
    if is_weather_station(station_id):
        return fetch_weather_station_data(station_id, target_datetime, use_imperial_units)
    else:
        return fetch_buoy_data(station_id, target_datetime, count, use_imperial_units)

def fetch_historical_met_data(buoy_id: str, start_date: datetime, end_date: datetime, use_imperial_units: bool = True) -> list:
    """
    Fetch a range of historical meteorological data from a buoy.
    """
    try:
        buoy = fetch_met_buoy(buoy_id)
        if not buoy:
            print(f"No meteorological buoy found with ID {buoy_id}")
            return []
        met_data = buoy.fetch_meteorological_reading()
        if not met_data:
            print(f"No historical meteorological data found for buoy {buoy_id}")
            return []
        historical_data = [
            entry for entry in met_data 
            if start_date <= entry.date.replace(tzinfo=timezone.utc) <= end_date
        ]
        return historical_data
    except Exception as e:
        print(f"Error fetching historical meteorological data: {str(e)}")
        return []

def met_data_to_json(met_data):
    """
    Convert meteorological data to JSON format.
    """
    met_json = []
    if met_data:
        for entry in met_data:
            data_point = {"date": entry.date.isoformat() if hasattr(entry, 'date') else datetime.now(timezone.utc).isoformat()}
            for attr in ['wind_speed', 'wind_direction', 'wind_gust', 'pressure', 'air_temperature', 'water_temperature', 'dewpoint_temperature', 'visibility', 'pressure_tendency']:
                if hasattr(entry, attr):
                    value = getattr(entry, attr)
                    if is_valid_data(value):
                        data_point[attr] = value
            met_json.append(data_point)
    return met_json
