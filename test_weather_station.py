import datetime
import pytz
from surfpy.weatherapi import WeatherApi

def find_closest_data_point(data_list, target_time):
    """Find the data point with the timestamp closest to the target time."""
    if not data_list:
        return None
    return min(data_list, key=lambda x: abs(x.date - target_time))

def test_station_data_availability():
    print("--- Testing F2595 Weather Station Data Availability (Last 7 Days) ---")
    station_id = "F2595"
    now = datetime.datetime.now(pytz.utc)
    availability_summary = {}

    for i in range(8):
        target_day = now - datetime.timedelta(days=i)
        day_str = target_day.strftime('%Y-%m-%d')
        print(f"\n--- Checking {day_str} ---")

        # Define a 24-hour window for the API call
        start_time = target_day.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)

        print(f"Fetching observations for {station_id} from {start_time.strftime('%Y-%m-%dT%H:%M:%SZ')} to {end_time.strftime('%Y-%m-%dT%H:%M:%SZ')}")
        raw_data = WeatherApi.fetch_station_observations(station_id, start_time, end_time)

        if raw_data and raw_data.get('features'):
            observations = WeatherApi.parse_station_observations(raw_data)
            if observations:
                # Set the target time for finding the sample data point
                sample_target_time = target_day.replace(hour=now.hour, minute=now.minute, second=now.second) - datetime.timedelta(hours=1)
                closest_point = find_closest_data_point(observations, sample_target_time)

                if closest_point:
                    summary_text = (
                        f"{len(observations)} observations found. "
                        f"Sample at {closest_point.date.strftime('%H:%M:%S Z')}: "
                        f"Wind Speed: {closest_point.wind_speed:.2f} knots, "
                        f"Direction: {closest_point.wind_direction}°"
                    )
                    availability_summary[day_str] = summary_text
                    print(f"  - SUCCESS: {summary_text}")
                else:
                    availability_summary[day_str] = f"{len(observations)} observations found, but sample point could not be determined."
                    print(f"  - SUCCESS: {len(observations)} observations found, but failed to find a sample point.")
            else:
                availability_summary[day_str] = "Data found but failed to parse."
                print("  - FAILED: Data found but could not be parsed.")
        else:
            availability_summary[day_str] = "No data available."
            print("  - FAILED: No data available for this day.")

    print("\n--- Availability Summary (Last 7 Days) ---")
    for day, status in sorted(availability_summary.items()):
        print(f"- {day}: {status}")

if __name__ == "__main__":
    test_station_data_availability()
