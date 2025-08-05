#!/usr/bin/env python3
"""
Analyze distances between surf spots and their assigned meteorological buoys.
This script helps quantify whether current wind data sources are too far from surf spots.

Usage:
    python analyze_wind_data_distances.py --csv surf_spots_rows_4.csv
    python analyze_wind_data_distances.py --csv surf_spots_rows_4.csv --output wind_analysis.json
"""

import argparse
import csv
import json
import requests
from math import radians, cos, sin, asin, sqrt
from datetime import datetime
import sys
import os

# Add parent directory for ocean_data imports if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in miles
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in miles
    r = 3956
    return c * r

def get_buoy_coordinates(buoy_id):
    """
    Fetch buoy coordinates from NDBC API
    Returns (lat, lon) tuple or None if not found
    """
    try:
        # Try to get buoy info from NDBC active stations
        url = "https://www.ndbc.noaa.gov/activestations.xml"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse XML to find our buoy
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)
        
        for station in root.findall('station'):
            station_id = station.get('id')
            if station_id == str(int(buoy_id)):  # Convert to int to handle float buoy IDs
                lat = float(station.get('lat'))
                lon = float(station.get('lon'))
                name = station.get('name', 'Unknown')
                return lat, lon, name
                
        print(f"Warning: Buoy {buoy_id} not found in active stations")
        return None, None, None
        
    except Exception as e:
        print(f"Error fetching buoy {buoy_id}: {e}")
        return None, None, None

def load_surf_spots(csv_file):
    """Load surf spots from CSV file"""
    spots = []
    skipped = []
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Check for required data before conversion
                if not row['wind_lat'] or not row['wind_long'] or not row['met_buoy_id']:
                    skipped.append(f"{row['name']} - missing coordinates or buoy ID")
                    continue
                
                if row['wind_lat'].strip() == '' or row['wind_long'].strip() == '' or row['met_buoy_id'].strip() == '':
                    skipped.append(f"{row['name']} - empty coordinates or buoy ID")
                    continue
                
                # Clean up the data
                spot = {
                    'id': int(row['id']),
                    'slug': row['slug'],
                    'name': row['name'],
                    'region': row['region'],
                    'lat': float(row['wind_lat']),
                    'lon': float(row['wind_long']),
                    'met_buoy_id': row['met_buoy_id'].strip()
                }
                
                # Skip spots with 'nan' or invalid buoy IDs
                if spot['met_buoy_id'].lower() == 'nan' or spot['met_buoy_id'] == '':
                    skipped.append(f"{spot['name']} - invalid buoy ID: {spot['met_buoy_id']}")
                    continue
                
                spots.append(spot)
                
            except ValueError as e:
                skipped.append(f"{row['name']} - conversion error: {e}")
                continue
            except KeyError as e:
                skipped.append(f"{row.get('name', 'Unknown')} - missing column: {e}")
                continue
    
    print(f"Loaded {len(spots)} surf spots with valid buoy assignments")
    if skipped:
        print(f"Skipped {len(skipped)} spots:")
        for skip_reason in skipped:
            print(f"  - {skip_reason}")
    
    return spots

def analyze_distances(spots):
    """Analyze distances between spots and their buoys"""
    results = []
    buoy_cache = {}  # Cache buoy coordinates to avoid duplicate API calls
    
    print("\n=== Analyzing Surf Spot to Buoy Distances ===")
    
    for spot in spots:
        # Handle buoy ID conversion more carefully
        try:
            buoy_id = str(int(float(spot['met_buoy_id'])))
        except (ValueError, TypeError):
            print(f"  ✗ Invalid buoy ID for {spot['name']}: {spot['met_buoy_id']}")
            continue
        
        print(f"\nProcessing: {spot['name']} ({spot['slug']})")
        print(f"  Location: {spot['lat']:.4f}°N, {spot['lon']:.4f}°W")
        print(f"  Assigned Buoy: {buoy_id}")
        
        # Get buoy coordinates (use cache if available)
        if buoy_id not in buoy_cache:
            buoy_lat, buoy_lon, buoy_name = get_buoy_coordinates(buoy_id)
            buoy_cache[buoy_id] = {
                'lat': buoy_lat,
                'lon': buoy_lon,
                'name': buoy_name
            }
        else:
            buoy_info = buoy_cache[buoy_id]
            buoy_lat, buoy_lon, buoy_name = buoy_info['lat'], buoy_info['lon'], buoy_info['name']
        
        if buoy_lat is None:
            print(f"  ✗ Could not find coordinates for buoy {buoy_id}")
            continue
            
        print(f"  Buoy Location: {buoy_lat:.4f}°N, {buoy_lon:.4f}°W ({buoy_name})")
        
        # Calculate distance
        distance = haversine_distance(spot['lat'], spot['lon'], buoy_lat, buoy_lon)
        print(f"  Distance: {distance:.1f} miles")
        
        result = {
            'surf_spot': {
                'name': spot['name'],
                'slug': spot['slug'],
                'region': spot['region'],
                'lat': spot['lat'],
                'lon': spot['lon']
            },
            'buoy': {
                'id': buoy_id,
                'name': buoy_name,
                'lat': buoy_lat,
                'lon': buoy_lon
            },
            'distance_miles': round(distance, 1)
        }
        results.append(result)
    
    return results

def generate_summary(results):
    """Generate summary statistics"""
    if not results:
        return {}
        
    distances = [r['distance_miles'] for r in results]
    
    summary = {
        'total_spots': len(results),
        'distance_stats': {
            'min': min(distances),
            'max': max(distances),
            'average': round(sum(distances) / len(distances), 1),
            'median': round(sorted(distances)[len(distances)//2], 1)
        },
        'distance_distribution': {
            'under_10_miles': len([d for d in distances if d < 10]),
            'under_25_miles': len([d for d in distances if d < 25]),
            'under_50_miles': len([d for d in distances if d < 50]),
            'over_50_miles': len([d for d in distances if d >= 50])
        }
    }
    
    return summary

def print_analysis(results, summary):
    """Print detailed analysis results"""
    print(f"\n{'='*60}")
    print("WIND DATA DISTANCE ANALYSIS RESULTS")
    print(f"{'='*60}")
    
    print(f"\n=== Summary Statistics ===")
    print(f"Total surf spots analyzed: {summary['total_spots']}")
    print(f"Average distance to buoy: {summary['distance_stats']['average']} miles")
    print(f"Median distance to buoy: {summary['distance_stats']['median']} miles")
    print(f"Distance range: {summary['distance_stats']['min']} - {summary['distance_stats']['max']} miles")
    
    print(f"\n=== Distance Distribution ===")
    dist = summary['distance_distribution']
    print(f"Under 10 miles: {dist['under_10_miles']} spots ({dist['under_10_miles']/summary['total_spots']*100:.1f}%)")
    print(f"Under 25 miles: {dist['under_25_miles']} spots ({dist['under_25_miles']/summary['total_spots']*100:.1f}%)")
    print(f"Under 50 miles: {dist['under_50_miles']} spots ({dist['under_50_miles']/summary['total_spots']*100:.1f}%)")
    print(f"Over 50 miles: {dist['over_50_miles']} spots ({dist['over_50_miles']/summary['total_spots']*100:.1f}%)")
    
    print(f"\n=== Spots by Distance (Furthest First) ===")
    sorted_results = sorted(results, key=lambda x: x['distance_miles'], reverse=True)
    
    for result in sorted_results:
        spot = result['surf_spot']
        buoy = result['buoy']
        distance = result['distance_miles']
        
        status_emoji = "🔴" if distance > 50 else "🟡" if distance > 25 else "🟢"
        print(f"{status_emoji} {spot['name']} ({spot['region']}) -> Buoy {buoy['id']} ({buoy['name']}): {distance} miles")

def main():
    parser = argparse.ArgumentParser(description='Analyze distances between surf spots and meteorological buoys')
    parser.add_argument('--csv', required=True, help='Path to surf spots CSV file')
    parser.add_argument('--output', help='Save results to JSON file')
    parser.add_argument('--threshold', type=float, default=25, help='Distance threshold in miles for flagging (default: 25)')
    
    args = parser.parse_args()
    
    # Load surf spots
    try:
        spots = load_surf_spots(args.csv)
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return
    
    if not spots:
        print("No valid surf spots found in CSV file")
        return
    
    # Analyze distances
    results = analyze_distances(spots)
    
    if not results:
        print("No analysis results generated")
        return
    
    # Generate summary
    summary = generate_summary(results)
    
    # Print analysis
    print_analysis(results, summary)
    
    # Flag problematic distances
    threshold = args.threshold
    problematic_spots = [r for r in results if r['distance_miles'] > threshold]
    
    if problematic_spots:
        print(f"\n=== Spots Beyond {threshold} Mile Threshold ===")
        for result in problematic_spots:
            spot = result['surf_spot']
            print(f"⚠️  {spot['name']} ({spot['region']}): {result['distance_miles']} miles")
    
    # Save results if requested
    if args.output:
        try:
            output_data = {
                'analysis_date': datetime.now().isoformat(),
                'summary': summary,
                'detailed_results': results,
                'problematic_spots': problematic_spots,
                'threshold_miles': threshold
            }
            
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"\n✓ Results saved to {args.output}")
        except Exception as e:
            print(f"✗ Error saving results: {e}")
    
    print(f"\n{'='*60}")
    print("Analysis completed!")
    
    # Recommendations
    print(f"\n=== Quick Recommendations ===")
    avg_distance = summary['distance_stats']['average']
    if avg_distance > 50:
        print("🔴 HIGH PRIORITY: Most buoys are very far from surf spots")
    elif avg_distance > 25:
        print("🟡 MEDIUM PRIORITY: Buoys are moderately far from surf spots")
    else:
        print("🟢 LOW PRIORITY: Buoys are reasonably close to surf spots")
    
    print(f"Consider alternative wind data sources for spots beyond {threshold} miles")

if __name__ == "__main__":
    main()