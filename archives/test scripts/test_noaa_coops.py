

import noaa_coops as coops
from datetime import datetime, timedelta
import pandas as pd

# Define the station ID for Montauk, NY
STATION_ID = "8510560"

def test_noaa_api():
    """
    Tests the NOAA CO-OPS API to understand its data structures.
    """
    try:
        # 1. Initialize the station object
        station = coops.Station(STATION_ID)

        # 2. Define the time window for data fetching
        begin_date = (datetime.now()).strftime("%Y%m%d")
        end_date = (datetime.now() + timedelta(days=2)).strftime("%Y%m%d")

        print(f"Fetching data for station: {STATION_ID}")
        print(f"Time window: {begin_date} to {end_date}\n")

        # 3. Fetch high/low tide predictions
        print("--- High/Low Tide Predictions ---")
        df_hilo = station.get_data(
            begin_date=begin_date,
            end_date=end_date,
            product="predictions",
            datum="MLLW",
            interval="hilo",
            time_zone="gmt"
        )
        if not df_hilo.empty:
            print("High/Low Predictions DataFrame Info:")
            df_hilo.info()
            print("\nFirst 5 rows:")
            print(df_hilo.head())
        else:
            print("No high/low predictions found.")
        
        print("\n" + "="*40 + "\n")

        # 4. Fetch water level predictions (for a specific time)
        print("--- Water Level Predictions ---")
        df_water_level = station.get_data(
            begin_date=begin_date,
            end_date=end_date,
            product="predictions",
            datum="MLLW",
            # interval parameter is omitted to use the default (6-minute)
            time_zone="gmt"
        )

        if not df_water_level.empty:
            print("Water Level Predictions DataFrame Info:")
            df_water_level.info()
            print("\nFirst 5 rows:")
            print(df_water_level.head())
        else:
            print("No water level data found for the specified time.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_noaa_api()

