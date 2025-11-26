# Swell Data Context

This document outlines the end-to-end data flow for how swell data is accessed, processed, and ultimately stored within a user's surf session log. It is intended to be a centralized resource for understanding the current system as we work to improve and expand its capabilities.

## High-Level Data Flow

The process can be summarized in the following steps:
1.  An API request to create a surf session triggers the data fetching process.
2.  The surf spot's location is used to find the correct NDBC buoy ID from a database configuration.
3.  The `surfpy` library fetches raw spectral data (energy and direction) from the NDBC servers for that buoy.
4.  The spectral data is processed to identify and partition individual swell components.
5.  The reading closest to the session's time is selected, converted to a user-friendly JSON format, and stored in the database.

## Detailed Breakdown

### 1. API Request & Configuration (`surfdata.py` & `ocean_data/location.py`)
- **Trigger**: The flow begins when a `POST` request is made to the `/api/surf-sessions` endpoint in `surfdata.py`. This request includes a `location` slug and the session's date and time.
- **Configuration**: The API calls `get_spot_config()` in `ocean_data/location.py`. This function queries the `surf_spots` database table to retrieve the configuration for the specified location, which includes the crucial `swell_buoy_id`.
- **Time Handling**: The session's timestamp is converted to a timezone-aware UTC `datetime` object, ensuring a standardized time is used for all subsequent data lookups.

### 2. High-Level Data Fetching (`ocean_data/swell.py`)
- **Orchestration**: The main API calls the `fetch_swell_data()` function in `ocean_data/swell.py`, passing it the `swell_buoy_id` and the session's UTC timestamp. This function acts as a high-level wrapper that coordinates the interaction with the `surfpy` library.

### 3. Buoy Station Identification (`surfpy/buoystations.py`)
- **Finding the Station**: `fetch_swell_data()` first calls `fetch_buoy_by_id()`, which initializes a `surfpy.BuoyStations` object. This object fetches an XML file (`activestations.xml`) from the NDBC server that lists all active buoys.
- **Selection**: The XML is parsed into a list of `BuoyStation` objects, and the station with the ID matching our `swell_buoy_id` is selected.

### 4. Raw Spectral Data Retrieval (`surfpy/buoystation.py`)
- **Fetching Raw Data**: The selected `BuoyStation` object's `fetch_wave_spectra_reading()` method is called. This method makes two critical HTTP requests to the NDBC's realtime data servers to download two raw text files:
    1.  `.data_spec`: Contains wave energy data across a spectrum of different wave frequencies.
    2.  `.swdir`: Contains the corresponding directional data for each frequency.

### 5. Processing and Swell Partitioning (`surfpy/buoystation.py` & `surfpy/buoyspectra.py`)
- **Parsing**: The raw text from these files is processed by `parse_wave_spectra_reading_data()`. For each available timestamp in the files, a `BuoySpectra` object is created.
- **The "Science" Step**: The `BuoySpectra` object is where the raw numbers are turned into meaningful swell data. The `swell_components` property performs the following key actions:
    - It uses a **`peakdetect`** algorithm to find the peaks in the wave energy spectrum. Each peak represents a distinct swell event (e.g., a primary groundswell and a secondary wind swell).
    - For each detected peak, it calculates the significant wave height, period (from the frequency of the peak), and mean direction for that specific swell component.
- **Output**: This step produces a list of `Swell` objects, one for each identified swell component, sorted by energy (most powerful first).

### 6. Final Formatting and Storage (`ocean_data` & `database_utils`)
- **Closest Match**: The list of processed readings is returned to `ocean_data/swell.py`. The `find_closest_data()` utility is used to select the single reading whose timestamp is nearest to the user's session time.
- **JSON Conversion**: This final data object is passed to `swell_data_to_json()`, which formats it into a clean JSON structure. It converts wave heights to feet and organizes the components into a dictionary (e.g., `"swell_1"`, `"swell_2"`).
- **Database Storage**: The final JSON is returned to the main `surfdata.py` API endpoint and assigned to the `raw_swell` key. This data is then passed to `database_utils.create_session()`, which saves the new surf log to the `surf_sessions_duplicate` table, storing the swell data in the `raw_swell` JSONB column.

## Future Considerations
This document serves as a baseline for future work on the swell data system, which may include:
-   **Component Display**: Improving the logic for how swell components are ordered and displayed to the user.
-   **Data Cleaning**: Filtering out or flagging irrelevant or minor swell components to reduce noise.
-   **Regional Expansion**: Adding new surf spots and their corresponding buoy configurations to the database to expand the app's geographic coverage.
