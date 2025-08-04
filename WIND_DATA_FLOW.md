# Wind Data Retrieval Flow

This document outlines the end-to-end process of how wind and other meteorological data is retrieved in the Surf App, from the initial API request to the final data processing.

## High-Level Architecture

The system is designed with a layered architecture to separate concerns:

-   **`surfdata.py` (API Layer)**: Handles incoming web requests and orchestrates the data retrieval process.
-   **`ocean_data` (Abstraction Layer)**: Provides a simplified interface for fetching various types of oceanographic data, hiding the complexity of the underlying data sources.
-   **`surfpy` (Engine Layer)**: A low-level library responsible for the direct interaction with external data providers like the National Data Buoy Center (NDBC).

---

## Detailed Data Flow

The process of fetching meteorological data for a surf session follows these steps:

### 1. API Endpoint (`surfdata.py`)

-   **Entry Point**: The flow begins with a `POST` request to the `/api/surf-sessions` endpoint.
-   **Input**: The endpoint receives a JSON payload containing the `location` slug (e.g., "lido-beach"), `date`, and `time`.
-   **Authentication**: The request is first authenticated using a JWT token.

### 2. Location Configuration (`ocean_data/location.py`)

-   **Spot Lookup**: The `location` slug is passed to `get_spot_config(location)`.
-   **Database Query**: This function queries the `surf_spots` table to get the configuration for the specified location. This record contains the crucial `met_buoy_id`, which is the ID for the meteorological buoy associated with that surf spot.
-   **Timezone Conversion**: The spot's configured `timezone` is used to convert the user's local session time into a standardized **UTC datetime object**. This is essential for accurately querying the scientific data sources.

### 3. Data Fetching Orchestration (`ocean_data/meteorology.py`)

-   **Function Call**: The API endpoint calls `fetch_meteorological_data()`, passing it the `met_buoy_id` and the UTC `target_datetime`.
-   **Buoy Fetching**: This function is the bridge to the `surfpy` library. It calls `fetch_met_buoy(buoy_id)` to get the appropriate buoy object.

### 4. Deep Dive: The `surfpy` Engine

The `surfpy` library handles all the low-level details of communicating with the NDBC.

#### a. Finding All Buoys (`surfpy.buoystations.BuoyStations`)

-   **Fetching Station Metadata**: The process starts with the `BuoyStations` class. Its `fetch_stations()` method sends a request to the NDBC's active stations list: `https://www.ndbc.noaa.gov/activestations.xml`.
-   **Parsing Station Data**: The `parse_stations()` method then parses this XML data. For each `<station>` entry in the XML, it creates a `BuoyStation` object.
-   **Key Buoy Attributes**: During parsing, it extracts essential metadata for each buoy, including:
    -   `id`: The unique station ID (e.g., '44097').
    -   `lat` & `lon`: The **latitude and longitude** of the buoy. This is stored in a `Location` object.
    -   `name`: The human-readable name of the station.
    -   `owner`, `program`, and `type`: Additional metadata about the buoy.

#### b. Representing a Single Buoy (`surfpy.buoystation.BuoyStation`)

-   **Buoy Object**: The `BuoyStation` class holds all the information for a single buoy, including its ID and `Location` object (which contains the latitude and longitude).
-   **Data URLs**: It has properties that construct the specific URLs for fetching data from the NDBC. For meteorological data, the relevant property is `meteorological_reading_url`, which creates a URL like: `https://www.ndbc.noaa.gov/data/realtime2/{self.station_id}.txt`.

#### c. Fetching and Parsing Raw Data

-   **HTTP Request**: The `fetch_meteorological_reading()` method in `BuoyStation` makes an HTTP `GET` request to the data URL.
-   **Parsing**: The raw text response from the NDBC server is passed to the static method `parse_meteorological_reading_data()`. This method reads the space-delimited text file line by line.
-   **Creating Data Objects**: For each line (representing a single time-stamped reading), it creates a `BuoyData` object.

#### d. The `BuoyData` Object (`surfpy.buoydata.BuoyData`)

-   This object holds the parsed values for a single reading. Key meteorological attributes populated from the NDBC text file include:
    -   `date`
    -   `wind_direction` (degrees)
    -   `wind_speed` (m/s)
    -   `wind_gust` (m/s)
    -   `pressure` (hPa)
    -   `air_temperature` (°C)
    -   `water_temperature` (°C)

### 5. Data Processing and Selection (`ocean_data/utils.py`)

-   **Find Closest Match**: The list of `BuoyData` objects returned from `surfpy` is sent to the `find_closest_data()` utility. This function iterates through the list and finds the single data entry whose timestamp is closest to the user's session time.
-   **JSON Conversion**: The selected data point is converted into a clean JSON format.
-   **Unit Conversion**: `convert_met_data_to_imperial()` is called to convert metric units to imperial (e.g., m/s to knots, Celsius to Fahrenheit) for user-friendliness.

### 6. Response and Storage (`surfdata.py`)

-   **Finalize**: The processed, imperial-unit meteorological data is returned to the `/api/surf-sessions` endpoint.
-   **Database Storage**: The data is added to the session object under the `raw_met` key and the entire session record is saved to the database.

---

### Summary Flowchart

```
[User Request] -> [Flask API: surfdata.py] -> [Abstraction: ocean_data/meteorology.py] -> [Engine: surfpy] -> [NDBC Data Source]
                                                                                                |
                                                                                        (BuoyStations, BuoyStation, BuoyData)
```