# Wind Data Implementation Plan

**Objective:** Replace the current NDBC buoy-based wind data source with the more accurate and proximate NOAA weather station observations to improve data quality for the August 9th MVP launch.

**Owner:** Gemini
**Date:** 2025-08-04
**Target Completion Date:** 2025-08-05

---

## 1. Research & Station Mapping (2 hours)

The first step is to identify the best weather station for each of our predefined surf spots. We will use the NOAA API and online tools to find the closest, most reliable station for each location.

**Tasks:**
1.  **Get Surf Spot Coordinates:** Extract the latitude and longitude for all surf spots from the `surfspots_EC_WC_hardcoded.json` file.
2.  **Find Stations via API:** For each coordinate pair, use the NOAA API endpoint `https://api.weather.gov/points/{lat},{lon}` to find the `observationStations` list.
3.  **Select Best Station:** From the list of nearby stations, select the closest one that provides reliable wind data. The station ID will be a 4-letter code (e.g., `KSQL`).
4.  **Document Mappings:** Create a definitive list of `slug -> weather_station_id` mappings.

**Initial Mapping Results:**
*This section will be updated as research is completed.*

| Surf Spot Slug        | Lat/Lon          | Proposed Station ID | Station Name                  | Distance (approx) |
| --------------------- | ---------------- | ------------------- | ----------------------------- | ----------------- |
| **West Coast**        |                  |                     |                               |                   |
| `steamer-lane`        | 36.96, -122.02   | KCAWATSO92          | Watsonville                   | ~3 mi             |
| `privates`            | 36.95, -121.98   | KCAWATSO92          | Watsonville                   | ~3 mi             |
| `pleasure-point`      | 36.95, -121.97   | KCAWATSO92          | Watsonville                   | ~3 mi             |
| `pacifica-north`      | 37.63, -122.51   | KSFOC1              | San Francisco                 | ~5 mi             |
| `pacifica-south`      | 37.63, -122.51   | KSFOC1              | San Francisco                 | ~5 mi             |
| `montara`             | 37.54, -122.52   | KHAF                | Half Moon Bay Airport         | ~4 mi             |
| `princeton-jetty`     | 37.50, -122.48   | KHAF                | Half Moon Bay Airport         | ~2 mi             |
| `ocean-beach-central` | 37.76, -122.51   | KSFOC1              | San Francisco                 | ~2 mi             |
| `ocean-beach-north`   | 37.76, -122.51   | KSFOC1              | San Francisco                 | ~2 mi             |
| `ocean-beach-south`   | 37.76, -122.51   | KSFOC1              | San Francisco                 | ~2 mi             |
| `san-onofre`          | 33.38, -117.58   | KNFG                | Camp Pendleton                | ~5 mi             |
| `trestles`            | 33.38, -117.59   | KNFG                | Camp Pendleton                | ~5 mi             |
| **East Coast**        |                  |                     |                               |                   |
| `lido-beach`          | 40.58, -73.65    | KFRG                | Republic Airport              | ~8 mi             |
| `manasquan`           | 40.12, -74.03    | KBLM                | Belmar Airport                | ~2 mi             |
| `rockaways`           | 40.57, -73.83    | KJFK                | JFK Airport                   | ~5 mi             |
| `belmar`              | 40.18, -74.01    | KBLM                | Belmar Airport                | ~1 mi             |

---

## 2. Code Implementation (3 hours)

### `surfpy` Layer (1.5 hours)
-   **File:** `surfpy/weatherapi.py`
-   **Task 1: Create `fetch_station_observations` function.**
    -   This function will take a `station_id` as input.
    -   It will construct the URL: `https://api.weather.gov/stations/{station_id}/observations/latest`
    -   It will make the HTTP request and handle potential errors.
-   **Task 2: Create `parse_station_observations` function.**
    -   This function will take the JSON response from the API.
    -   It will parse the `properties` object to extract `windDirection.value` and `windSpeed.value`. Note: wind speed is in km/h and needs conversion.
    -   It will create and return a single `BuoyData` object, maintaining the existing data structure for seamless integration. The `date` will come from the `timestamp` field.

### `ocean_data` Layer (1 hour)
-   **File:** `ocean_data/meteorology.py`
-   **Task 1: Modify `fetch_meteorological_data`.**
    -   Change the function signature to accept `weather_station_id` instead of `met_buoy_id`.
    -   Remove the call to `fetch_met_buoy`.
    -   Add a call to the new `surfpy.weatherapi.fetch_station_observations(weather_station_id)`.
    -   The rest of the function (`find_closest_data`, unit conversion) should work as is, but since we are fetching the latest observation, `find_closest_data` might be redundant. We will simplify to just use the single returned data point.
-   **File:** `ocean_data/location.py`
-   **Task 2: Update `get_spot_config`.**
    -   This function already queries the `surf_spots` table. The query will be updated in the DB section to pull `weather_station_id`. No code change is needed here, but we must be aware of the dependency.

### `surfdata.py` API Layer (0.5 hours)
-   **File:** `surfdata.py`
-   **Task 1: Update `create_surf_session` logic.**
    -   The call to `get_spot_config` will now return a `weather_station_id`.
    -   The call to `fetch_meteorological_data` will now pass this new ID.
    -   The `met_buoy_id` field should be changed to `weather_station_id` when saving the session to the database.

---

## 3. Database Schema & Data Migration (1 hour)

**Tasks:**
1.  **Schema Change (0.5 hours):**
    -   Connect to the PostgreSQL database.
    -   Execute an `ALTER TABLE` command to rename the `met_buoy_id` column to `weather_station_id` and possibly change its type to `VARCHAR(10)`.
    ```sql
    ALTER TABLE surf_spots RENAME COLUMN met_buoy_id TO weather_station_id;
    ALTER TABLE surf_spots ALTER COLUMN weather_station_id TYPE VARCHAR(10);
    ```
    -   Do the same for the `surf_sessions_duplicate` table.
    ```sql
    ALTER TABLE surf_sessions_duplicate RENAME COLUMN met_buoy_id TO weather_station_id;
    ALTER TABLE surf_sessions_duplicate ALTER COLUMN weather_station_id TYPE VARCHAR(10);
    ```
2.  **Data Migration (0.5 hours):**
    -   Write and execute a series of `UPDATE` statements to populate the new `weather_station_id` column for all 20+ surf spots using the mappings from the research phase.
    ```sql
    UPDATE surf_spots SET weather_station_id = 'KCAWATSO92' WHERE slug = 'steamer-lane';
    -- Repeat for all other spots.
    ```

---

## 4. Testing Strategy (2 hours)

**Tasks:**
1.  **Unit Tests (1 hour):**
    -   Create `surfpy/tests/test_weatherapi.py`.
    -   Add a test for `fetch_station_observations` that mocks the `requests.get` call and ensures it handles success and failure cases.
    -   Add a test for `parse_station_observations` with a sample JSON payload to verify it correctly creates a `BuoyData` object with converted units.
2.  **Integration Test (1 hour):**
    -   Modify `test_db_functions.py` or create a new test file.
    -   Create a test that posts a new session to `/api/surf-sessions` for a spot (e.g., 'steamer-lane').
    -   Retrieve the session from the database and assert that `session['weather_station_id']` is 'KCAWATSO92'.
    -   Assert that the `raw_met` field contains wind data.

---

## 5. Rollout Strategy (0.5 hours)

This will be a single, coordinated deployment.
**Sequence:**
1.  Place the API in a brief maintenance mode.
2.  Apply the database schema changes (`ALTER TABLE`).
3.  Run the data migration script (`UPDATE` statements).
4.  Deploy the updated backend code.
5.  Disable maintenance mode.
6.  Perform a quick manual test by creating a session through the UI to confirm the end-to-end flow is working.

---
