#!/usr/bin/env python3
"""
Weather Station Mapper for SLAPP Surf App
Maps surf spots to nearest NOAA weather stations for improved wind data accuracy.
"""

import requests
import json
import time
from typing import Dict, List, Tuple, Optional
import csv

# Your surf spots with coordinates (add more as needed)
SURF_SPOTS = {
    # West Coast
    'steamer-lane': (36.95, -122.02),
    'privates': (36.95, -121.98),
    'pleasure-point': (36.95, -121.97),
    'pacifica-north': (37.63, -122.51),
    'pacifica-south': (37.63, -122.51),
    'montara': (37.54, -122.52),
    'princeton-jetty': (37.50, -122.48),
    'ocean-beach-central': (37.76, -122.51),
    'ocean-beach-north': (37.76, -122.51),
    'ocean-beach-south': (37.76, -122.51),
    'san-onofre': (33.38, -117.58),
    'trestles': (33.38, -117.59),
    
    # East Coast
    'lido-beach': (40.58, -73.65),
    'manasquan': (40.12, -74.03),
    'rockaways': (40.57, -73.83),
    'belmar': (40.18, -74.01),
}

def get_weather_stations_for_location(lat: float, lon: float) -> Optional[List[Dict]]:
    """
    Get weather stations for a given lat/lon using NOAA API.
    Returns list of stations sorted by distance (closest first).
    """
    try:
        # Step 1: Get grid point info
        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        print(f"Fetching grid info for ({lat}, {lon})...")
        
        response = requests.get(points_url, timeout=10)
        response.raise_for_status()
        points_data = response.json()
        
        # Step 2: Get observation stations URL
        stations_url = points_data['properties']['observationStations']
        print(f"Fetching stations from: {stations_url}")
        
        # Add delay to be respectful to API
        time.sleep(0.5)
        
        response = requests.get(stations_url, timeout=10)
        response.raise_for_status()
        stations_data = response.json()
        
        # Step 3: Parse and sort stations by distance
        stations = []
        for feature in stations_data['features']:
            props = feature['properties']
            station_info = {
                'id': props['stationIdentifier'],
                'name': props['name'],
                'distance_meters': props['distance']['value'],
                'distance_miles': props['distance']['value'] * 0.000621371,  # Convert to miles
                'coordinates': feature['geometry']['coordinates'],  # [lon, lat]
                'elevation_meters': props.get('elevation', {}).get('value', 0)
            }
            stations.append(station_info)
        
        # Sort by distance (closest first)
        stations.sort(key=lambda x: x['distance_meters'])
        
        return stations
        
    except requests.RequestException as e:
        print(f"Error fetching data for ({lat}, {lon}): {e}")
        return None
    except KeyError as e:
        print(f"Error parsing response for ({lat}, {lon}): {e}")
        return None

def test_station_data_availability(station_id: str) -> bool:
    """
    Test if a weather station has recent wind data available.
    Returns True if data is available, False otherwise.
    """
    try:
        # Try to get latest observations
        obs_url = f"https://api.weather.gov/stations/{station_id}/observations/latest"
        response = requests.get(obs_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            props = data['properties']
            
            # Check if wind data is available
            wind_speed = props.get('windSpeed', {})
            wind_direction = props.get('windDirection', {})
            
            has_wind_data = (
                wind_speed.get('value') is not None and 
                wind_direction.get('value') is not None
            )
            
            return has_wind_data
        else:
            return False
            
    except Exception as e:
        print(f"Error testing station {station_id}: {e}")
        return False

def map_surf_spots_to_stations(spots: Dict[str, Tuple[float, float]], 
                              max_stations: int = 3,
                              test_data: bool = True) -> Dict[str, List[Dict]]:
    """
    Map all surf spots to their nearest weather stations.
    
    Args:
        spots: Dictionary of spot_slug -> (lat, lon)
        max_stations: Maximum number of stations to return per spot
        test_data: Whether to test stations for data availability
    
    Returns:
        Dictionary mapping spot_slug -> list of station info dicts
    """
    results = {}
    
    total_spots = len(spots)
    for i, (spot_slug, (lat, lon)) in enumerate(spots.items(), 1):
        print(f"\n[{i}/{total_spots}] Processing {spot_slug}...")
        
        stations = get_weather_stations_for_location(lat, lon)
        if not stations:
            print(f"❌ No stations found for {spot_slug}")
            results[spot_slug] = []
            continue
        
        # Take top stations and optionally test them
        candidate_stations = stations[:max_stations * 2]  # Get extra in case some don't have data
        valid_stations = []
        
        for station in candidate_stations:
            if len(valid_stations) >= max_stations:
                break
                
            if test_data:
                print(f"  Testing station {station['id']} ({station['name']})...")
                time.sleep(0.3)  # Be respectful to API
                
                if test_station_data_availability(station['id']):
                    print(f"  ✅ {station['id']} has wind data")
                    valid_stations.append(station)
                else:
                    print(f"  ❌ {station['id']} has no wind data")
            else:
                valid_stations.append(station)
        
        results[spot_slug] = valid_stations
        
        if valid_stations:
            primary = valid_stations[0]
            print(f"✅ {spot_slug} -> {primary['id']} ({primary['distance_miles']:.1f} mi)")
        else:
            print(f"❌ No valid stations found for {spot_slug}")
        
        # Be respectful to the API
        time.sleep(1)
    
    return results

def export_results_to_csv(results: Dict[str, List[Dict]], filename: str = 'surf_spot_weather_stations.csv'):
    """Export results to CSV for easy viewing and database import."""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'surf_spot_slug', 'spot_lat', 'spot_lon',
            'primary_station_id', 'primary_station_name', 'primary_distance_miles',
            'secondary_station_id', 'secondary_station_name', 'secondary_distance_miles',
            'tertiary_station_id', 'tertiary_station_name', 'tertiary_distance_miles'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for spot_slug, stations in results.items():
            if not stations:
                continue
                
            spot_lat, spot_lon = SURF_SPOTS[spot_slug]
            row = {
                'surf_spot_slug': spot_slug,
                'spot_lat': spot_lat,
                'spot_lon': spot_lon
            }
            
            # Add up to 3 stations
            for i, station in enumerate(stations[:3]):
                prefix = ['primary', 'secondary', 'tertiary'][i]
                row[f'{prefix}_station_id'] = station['id']
                row[f'{prefix}_station_name'] = station['name']
                row[f'{prefix}_distance_miles'] = round(station['distance_miles'], 1)
            
            writer.writerow(row)
    
    print(f"\n📄 Results exported to {filename}")

def print_summary(results: Dict[str, List[Dict]]):
    """Print a summary of the mapping results."""
    print("\n" + "="*60)
    print("WEATHER STATION MAPPING SUMMARY")
    print("="*60)
    
    total_spots = len(results)
    mapped_spots = len([s for s in results.values() if s])
    
    print(f"Total surf spots: {total_spots}")
    print(f"Successfully mapped: {mapped_spots}")
    print(f"Failed to map: {total_spots - mapped_spots}")
    
    print(f"\nTop station mappings:")
    print("-" * 40)
    
    for spot_slug, stations in results.items():
        if stations:
            primary = stations[0]
            print(f"{spot_slug:<20} -> {primary['id']:<8} ({primary['distance_miles']:.1f} mi)")
    
    print("\n" + "="*60)

def main():
    """Main execution function."""
    print("🌊 SLAPP Weather Station Mapper")
    print("Finding optimal weather stations for surf spots...\n")
    
    # Option to test with just a few spots first
    test_mode = input("Test with just Steamer Lane and Lido Beach first? (y/n): ").lower().strip() == 'y'
    
    if test_mode:
        test_spots = {
            'steamer-lane': SURF_SPOTS['steamer-lane'],
            'lido-beach': SURF_SPOTS['lido-beach']
        }
        spots_to_process = test_spots
        print("🧪 Running in test mode with 2 spots...")
    else:
        spots_to_process = SURF_SPOTS
        print(f"🚀 Processing all {len(SURF_SPOTS)} surf spots...")
    
    # Map spots to stations
    results = map_surf_spots_to_stations(
        spots_to_process, 
        max_stations=3,
        test_data=True  # Set to False to skip data availability testing
    )
    
    # Print results
    print_summary(results)
    
    # Export to CSV
    if results:
        filename = 'test_weather_stations.csv' if test_mode else 'surf_spot_weather_stations.csv'
        export_results_to_csv(results, filename)
    
    # Generate SQL for database migration
    if not test_mode and results:
        print("\n📝 Generating SQL for database migration...")
        with open('weather_station_migration.sql', 'w') as f:
            f.write("-- Weather Station Migration SQL\n")
            f.write("-- Replace met_buoy_id with weather_station_ids array\n\n")
            
            for spot_slug, stations in results.items():
                if stations:
                    station_ids = [f"'{s['id']}'" for s in stations[:3]]
                    station_array = '{' + ','.join(station_ids) + '}'
                    f.write(f"UPDATE surf_spots SET weather_station_ids = ARRAY[{','.join(station_ids)}] WHERE slug = '{spot_slug}';\n")
        
        print("📄 SQL migration script saved to weather_station_migration.sql")

if __name__ == "__main__":
    main()