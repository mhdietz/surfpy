from typing import List
import requests
import datetime
import pytz

from . import units
from .location import Location
from .buoydata import BuoyData
from surfpy import buoydata


class WeatherApi():

    _API_ROOT_URL = 'https://api.weather.gov/'

    @staticmethod
    def points(location: Location) -> dict:
        # points API https://api.weather.gov/points/41.4302,-71.455
        url = f'{WeatherApi._API_ROOT_URL}points/{location.latitude:4f},{location.longitude:4f}'
        resp = requests.get(url)
        resp_json = resp.json()
        return resp_json['properties']

    @staticmethod
    def gridpoints(office: str, grid_x: int, grid_y: int) -> dict:
        # https://api.weather.gov/gridpoints/BOX/65,32
        url = f'{WeatherApi._API_ROOT_URL}gridpoints/{office}/{grid_x},{grid_y}'
        resp = requests.get(url)
        resp_json = resp.json()
        return resp_json['properties']

    @staticmethod
    def forecast(office: str, grid_x: int, grid_y: int) -> dict:
        # https://api.weather.gov/gridpoints/BOX/65,32/forecast
        url = f'{WeatherApi._API_ROOT_URL}gridpoints/{office}/{grid_x},{grid_y}/forecast'
        resp = requests.get(url)
        resp_json = resp.json()
        return resp_json['properties']

    @staticmethod
    def hourly_forecast(office: str, grid_x: int, grid_y: int) -> dict:
        # https://api.weather.gov/gridpoints/BOX/65,32/forecast/hourly
        url = f'{WeatherApi._API_ROOT_URL}gridpoints/{office}/{grid_x},{grid_y}/forecast/hourly'
        resp = requests.get(url)
        resp_json = resp.json()
        return resp_json['properties']

    @staticmethod
    def fetch_station_observations(station_id: str, start_date: datetime.datetime, end_date: datetime.datetime) -> dict:
        # https://api.weather.gov/stations/KNYC/observations?start=2024-08-05T12:00:00Z&end=2024-08-05T13:00:00Z
        start_iso = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_iso = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        url = f'{WeatherApi._API_ROOT_URL}stations/{station_id}/observations?start={start_iso}&end={end_iso}'
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            print(f'Http Error: {e}')
        except requests.exceptions.ConnectionError as e:
            print(f'Error Connecting: {e}')
        except requests.exceptions.Timeout as e:
            print(f'Timeout Error: {e}')
        except requests.exceptions.RequestException as e:
            print(f'OOps: Something Else {e}')
        return None

    @staticmethod
    def parse_station_observations(observation_data: dict) -> List[BuoyData]:
        buoy_data = []
        if not observation_data or 'features' not in observation_data:
            return buoy_data

        for feature in observation_data['features']:
            properties = feature.get('properties', {})
            if not properties:
                continue

            buoy_data_point = BuoyData(units.Units.english)
            
            # Date
            timestamp_str = properties.get('timestamp')
            if timestamp_str:
                buoy_data_point.date = datetime.datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S%z').astimezone(pytz.utc)

            # Wind Speed (convert from km/h to knots)
            wind_speed_data = properties.get('windSpeed', {})
            if wind_speed_data and wind_speed_data.get('value') is not None:
                kph = wind_speed_data['value']
                if kph is not None:
                    # Convert km/h to knots
                    knots = kph * 0.539957
                    buoy_data_point.wind_speed = knots

            # Wind Direction
            wind_direction_data = properties.get('windDirection', {})
            if wind_direction_data and wind_direction_data.get('value') is not None:
                buoy_data_point.wind_direction = int(wind_direction_data['value'])

            buoy_data.append(buoy_data_point)

        return buoy_data
    
    @staticmethod
    def parse_weather_forecast(forecast_data: dict) -> List[BuoyData]:
        buoy_data = []

        if forecast_data is None:
            return buoy_data

        periods = forecast_data['periods']
        for period in periods:
            buoy_data_point = BuoyData(units.Units.english)
            buoy_data_point.date = datetime.datetime.strptime(period['startTime'], '%Y-%m-%dT%H:%M:%S%z').astimezone(pytz.utc)
            raw_temp = period['temperature']
            if raw_temp:
                buoy_data_point.air_temperature = int(raw_temp)
            buoy_data_point.short_forecast = period['shortForecast']
            raw_speed = period['windSpeed']
            if raw_speed:
                buoy_data_point.wind_speed = int(raw_speed.split(' ')[0])
            buoy_data_point.wind_compass_direction = period['windDirection']
            buoy_data_point.wind_direction =  units.direction_to_degree(buoy_data_point.wind_compass_direction)
            buoy_data.append(buoy_data_point)

        return buoy_data

    @staticmethod
    def fetch_hourly_forecast(location: Location) -> List[BuoyData]:
        meta = WeatherApi.points(location)
        raw_hourly = WeatherApi.hourly_forecast(meta['gridId'], meta['gridX'], meta['gridY'])
        return WeatherApi.parse_weather_forecast(raw_hourly)

    @staticmethod
    def fetch_hourly_forecast_from_metadata(meta: dict) -> List[BuoyData]:
        if not meta['gridId'] or not meta['gridX'] or not meta['gridY']:
            return []

        raw_hourly = WeatherApi.hourly_forecast(meta['gridId'], meta['gridX'], meta['gridY'])
        return WeatherApi.parse_weather_forecast(raw_hourly)
