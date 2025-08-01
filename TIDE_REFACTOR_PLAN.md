# Tide Feature Refactor: Plan (Final)

This document outlines the plan to refactor the `create_session` and `update_session` endpoints to provide more detailed tide information.

### **1. Goal**

The objective is to modify the surf session endpoints to fetch and store the following tide data for each session:
1.  The precise water level at the session's start time.
2.  The direction of the tide (e.g., "rising" or "falling").
3.  Details of the next tide event, including its type (high/low), timestamp, and height.
4.  Ensure all height values are in feet.

### **2. Rationale for Refactor: `surfpy` vs. `noaa-coops`**

This refactor is necessary because the existing implementation, which uses the `surfpy` library, is fundamentally limited to fetching simple, time-series data. To provide the desired rich tide information (direction and next event details), we need to access a different type of data product from NOAA, which the `noaa-coops` library is specifically designed to handle.

**a. The Insufficiency of the `surfpy` Library**

-   The `surfpy` library is a powerful tool for fetching raw, observational data from sources like NDBC buoys. In our current implementation, it treats tide data as a simple stream of water level measurements over time.
-   While it can tell us the water level at a specific minute, it **cannot tell us when the next high or low tide will occur**. To determine that, we would have to fetch a large dataset (e.g., 24-48 hours of 6-minute interval data) and then write complex, error-prone logic to manually find the "peaks" (high tide) and "troughs" (low tide) in that data. This would be inefficient and reinventing the wheel.

**b. A Fundamentally Different Data Source**

-   The core of this refactor is the switch to a more suitable data source provided by the NOAA CO-OPS API. Instead of just a raw feed of water levels, NOAA also offers a pre-calculated **predictions** product.
-   Our testing confirmed that using the `interval=hilo` parameter with this product provides direct access to the high and low tide **events**. We are no longer interpreting a raw signal; we are fetching a list of curated, meaningful events.
-   The `noaa-coops` library is the correct tool for this job because it is built specifically to interact with the NOAA CO-OPS API and its various data products, including the crucial `hilo` interval predictions. It abstracts away the direct API calls and provides the data in a clean, easy-to-use format (a pandas DataFrame).

By switching to `noaa-coops`, we are using the right tool to access the right data, allowing us to build the desired feature efficiently and reliably.

### **3. Database Schema**

To support this feature, the `surf_sessions_duplicate` table must be updated to the following state. The new columns will store the detailed tide event data, and the old `session_tide_data` column will be removed.

| Column Name              | Data Type                  | Notes                                                              |
| :----------------------- | :------------------------- | :----------------------------------------------------------------- |
| `session_water_level`    | `double precision`         | **New.** Stores the water level in feet at the session's start time. |
| `tide_direction`         | `text`                     | Stores 'rising' or 'falling'.                                      |
| `next_tide_event_type`   | `text`                     | Stores 'high' or 'low'.                                            |
| `next_tide_event_at`     | `timestamp with time zone` | The precise timestamp of the next tide event.                      |
| `next_tide_event_height` | `double precision`         | The water level of the next tide event in feet.                    |
| `session_tide_data`      | `jsonb`                    | **To be removed.** This column is made obsolete.                   |

### **4. High-Level Approach**

The implementation will be a three-step process focused on modifying the data-fetching layer, integrating it into the API layer, and ensuring it's persisted correctly in the database layer.

#### **Step 1: Refactor the Tide Data Fetching Logic (`ocean_data/tide.py`)**

The core of this effort involves overhauling the `fetch_tide_data` function to be the single source of detailed tide information.

1.  **Leverage `noaa-coops`:** The `noaa-coops` library is purpose-built for fetching the detailed event data required. I will use it to get high/low tide predictions.
2.  **Create New Core Function `get_detailed_tide_data`:** This new function will be the primary workhorse. It will take a `station_id` and a `target_datetime` (in UTC) and will:
    *   Fetch tide predictions for a 48-hour window to ensure the next event is always found.
    *   Fetch the precise water level for the exact `target_datetime`.
    *   Identify the next high or low tide event that occurs *after* the `target_datetime`.
    *   Determine the tide's direction (rising or falling) by comparing the current water level to the level of the next event.
3.  **Refactor `fetch_tide_data`**: The existing `fetch_tide_data` function will be simplified. It will now orchestrate the call to the new detailed function and format its output into a clean dictionary containing all the required fields: `water_level`, `direction`, `next_event_type`, `next_event_at`, `next_event_height`, and `units`.

#### **Step 2: API Endpoint Integration (`surfdata.py`)**

The `create_surf_session` and `update_surf_session` endpoints will be updated to use the new data.

1.  **Update Data Fetching Call**: The call to `fetch_tide_data` will now return the detailed dictionary described above.
2.  **Map New Data**: The new key-value pairs from the tide data dictionary will be added to the main `session_data` dictionary. For example:
    *   `session_data['tide_direction'] = tide_data.get('direction')`
    *   `session_data['next_tide_event_at'] = tide_data.get('next_event_at')`
    *   ...and so on for the other new fields.
3.  **Remove `session_tide_data`**: The new individual fields make the old `session_tide_data` JSON blob obsolete. The code will be updated to no longer fetch or save this field for new or updated sessions.
4.  **Fix Existing Bug**: I will correct the bug in `update_surf_session` where the detailed `raw_tide` data (used for charts) was being incorrectly overwritten. The new tide data will be mapped to its own distinct fields, and the `raw_tide` data will be preserved correctly.

#### **Step 3: Database Interaction (`database_utils.py`)**

The final step is to ensure the new data is correctly persisted in the database.

1.  **Verify Dynamic Inserts/Updates**: The `create_session` and `update_session` functions are written to dynamically handle new data fields based on the keys in the `session_data` dictionary. I will verify that they correctly map the new keys (e.g., `tide_direction`) to the corresponding database columns. This step is primarily for verification, as the dynamic nature of the functions should handle the changes automatically.

### **5. Final Confirmation**

This plan proceeds with the following confirmed assumptions:
*   The database schema will be updated as described above.
*   Backward compatibility for the old `session_tide_data` field is **not** required.
*   All tide height values will be handled in **feet**.
*   The existing timezone handling (localizing to the spot's timezone, then converting to UTC for fetching) is correct and will be maintained.

### **6. NOAA CO-OPS API Data Structures (from testing)**

Our testing of the `noaa-coops` library and the underlying API revealed the following data structures, which will inform the implementation.

#### **a. High/Low Tide Predictions**

-   **API URL**: `https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=predictions&interval=hilo&...`
-   **Raw JSON Output**: A list of dictionaries, each with `t` (timestamp), `v` (value), and `type` (`H` or `L`) keys.
    ```json
    { "predictions" : [
        {"t":"2025-08-01 01:44", "v":"0.78", "type":"L"},
        {"t":"2025-08-01 07:07", "v":"1.74", "type":"H"}
    ]}
    ```
-   **`noaa-coops` Library Output**: The library conveniently parses the raw JSON into a pandas DataFrame with the following structure:
    -   **Index**: A `DatetimeIndex` representing the timestamp of the tide event (in GMT/UTC).
    -   **Column `v` (float64)**: The water level (height) of the tide event.
    -   **Column `type` (object/string)**: The type of event, either `'H'` for high tide or `'L'` for low tide.

#### **b. Water Level Predictions**

-   **API URL**: `https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=predictions&...` (defaults to 6-min intervals)
-   **Raw JSON Output**: A list of dictionaries, each with `t` (timestamp) and `v` (value) keys.
-   **`noaa-coops` Library Output**: A pandas DataFrame with:
    -   **Index**: A `DatetimeIndex` representing the timestamp of the water level reading (in GMT/UTC).
    -   **Column `v` (float64)**: The water level (height) at that specific time.

This confirms that the `noaa-coops` library provides the necessary data in a structured format, which simplifies the logic required in our `get_detailed_tide_data` function.

I am ready to begin implementation. Please confirm if I should proceed.