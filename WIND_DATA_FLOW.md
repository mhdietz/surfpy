# Wind and Meteorological Data Retrieval Flow

This document outlines the end-to-end process of how wind and other meteorological data is retrieved in the Surf App, from the initial API request to the final data processing. The system can retrieve data from two primary sources: offshore NDBC buoys and onshore NOAA weather stations.

## High-Level Architecture

The system is designed with a layered architecture to separate concerns:

-   **`surfdata.py` (API Layer)**: Handles incoming web requests and orchestrates the data retrieval process.
-   **`ocean_data` (Abstraction Layer)**: Provides a simplified interface for fetching various types of oceanographic data, hiding the complexity of the underlying data sources.
-   **`surfpy` (Engine Layer)**: A low-level library responsible for the direct interaction with external data providers, including the National Data Buoy Center (NDBC) and the NOAA `api.weather.gov` service.

---

## Detailed Data Flow

The process of fetching meteorological data for a surf session follows these steps:

### 1. API Endpoint (`surfdata.py`)

-   **Entry Point**: The flow begins with a `POST` request to the `/api/surf-sessions` endpoint.
-   **Input**: The endpoint receives a JSON payload containing the `location` slug (e.g., "lido-beach"), `date`, and `time`.
-   **Authentication**: The request is first authenticated using a JWT token.

### 2. Location Configuration (`ocean_data/location.py`)

-   **Spot Lookup**: The `location` slug is passed to `get_spot_config(location)`.
-   **Database Query**: This function queries the `surf_spots` table to get the configuration for the specified location. This record contains the crucial `met_station_id`.
-   **Station ID**: The `met_station_id` can be either a numeric ID for an NDBC buoy (e.g., '44097') or a non-numeric station identifier for a NOAA weather station (e.g., 'KNYC'). This ID determines which data source will be used.
-   **Timezone Conversion**: The spot's configured `timezone` is used to convert the user's local session time into a standardized **UTC datetime object**. This is essential for accurately querying the scientific data sources.

### 3. Data Fetching Orchestration (`ocean_data/meteorology.py`)

-   **Function Call**: The API endpoint calls `fetch_meteorological_data()`, passing it the `met_station_id` and the UTC `target_datetime`.
-   **Conditional Logic**: This function inspects the `met_station_id` to determine the data source.
    -   If the ID is **numeric**, it calls `fetch_buoy_data()` to retrieve data from an NDBC buoy.
    -   If the ID is **non-numeric**, it calls `fetch_weather_station_data()` to retrieve data from a NOAA weather station.

---

### 4. Data Source Flow 1: NDBC Buoys

This flow is used for numeric station IDs and retrieves data from offshore buoys.

#### a. Finding the Buoy (`surfpy.buoystations`)

-   **Fetching Station Metadata**: The `BuoyStations` class fetches and parses the NDBC's active stations list from `https://www.ndbc.noaa.gov/activestations.xml` to find the metadata for the requested buoy ID.

#### b. Fetching and Parsing Raw Data (`surfpy.buoystation`)

-   **HTTP Request**: The `BuoyStation` object constructs a URL (e.g., `https://www.ndbc.noaa.gov/data/realtime2/{station_id}.txt`) and makes an HTTP `GET` request.
-   **Parsing**: The raw, space-delimited text response is parsed by `parse_meteorological_reading_data()`.
-   **Creating Data Objects**: For each line (representing a single time-stamped reading), it creates a `BuoyData` object with data in metric units (e.g., wind speed in m/s).

---

### 5. Data Source Flow 2: NOAA Weather Stations

This flow is used for non-numeric station IDs and retrieves data from onshore weather stations via the `api.weather.gov` service.

#### a. Fetching Observations (`surfpy.weatherapi`)

-   **API Call**: The `fetch_weather_station_data()` function in `ocean_data/meteorology.py` calls `WeatherApi.fetch_station_observations()`.
-   **HTTP Request**: This method constructs the appropriate URL (e.g., `https://api.weather.gov/stations/{station_id}/observations`) and retrieves a JSON-formatted list of recent observations.

#### b. Parsing Raw Data (`surfpy.weatherapi`)

-   **Parsing**: The JSON response is parsed by the static method `WeatherApi.parse_station_observations()`.
-   **Creating Data Objects**: This function iterates through the observations in the JSON response and creates a `BuoyData` object for each one. This ensures the data structure is consistent with the buoy data flow.
-   **Unit Conversion**: The NOAA API provides wind speed in km/h. During parsing, this is converted to **knots** and stored in the `BuoyData` object.

---

### 6. Data Processing and Selection (`ocean_data/utils.py`)

-   **Find Closest Match**: The list of `BuoyData` objects, regardless of its source (buoy or weather station), is sent to the `find_closest_data()` utility. This function iterates through the list and finds the single data entry whose timestamp is closest to the user's session time.
-   **JSON Conversion**: The selected data point is converted into a clean JSON format.
-   **Unit Conversion**: If the data came from an NDBC buoy, `convert_met_data_to_imperial()` is called to convert metric units to imperial (e.g., m/s to knots, Celsius to Fahrenheit) for user-friendliness. Data from weather stations is already in a friendly format (knots).

### 7. Response and Storage (`surfdata.py`)

-   **Finalize**: The processed meteorological data is returned to the `/api/surf-sessions` endpoint.
-   **Database Storage**: The data is added to the session object under the `raw_met` key and the entire session record is saved to the database.

---

### Summary Flowchart

```
[User Request] -> [Flask API: surfdata.py]
      |
      v
[Abstraction: ocean_data/meteorology.py] --(ID is Numeric)--> [Engine: surfpy/buoystation] -> [NDBC Buoy Source]
      |
      '--(ID is Non-Numeric)--> [Engine: surfpy/weatherapi] -> [NOAA API Source]
      |
      v
[Processing: ocean_data/utils.py] -> [Response to User & DB Storage]
```