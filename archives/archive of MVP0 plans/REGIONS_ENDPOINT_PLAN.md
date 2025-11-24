# Plan: Create Regions API Endpoint

This document outlines the plan to create a new API endpoint that provides a list of all unique surf regions available in the database.

## 1. Create Database Function

-   **File:** `database_utils.py`
-   **Function:** Create a new function named `get_all_regions()`.
-   **Logic:**
    -   Connect to the database.
    -   Execute the SQL query: `SELECT DISTINCT region FROM surf_spots WHERE region IS NOT NULL AND region <> '' ORDER BY region;`
-   **Protection:** The API endpoint will be protected and require authentication.
    -   Fetch all results.
    -   Return the list of region names.

## 2. Create API Endpoint

-   **File:** `surfdata.py`
-   **Route:** Add a new route: `@app.route('/api/regions', methods=['GET'])`.
-   **Function:** Create a new handler function for this route.

## 3. Connect and Return Data

-   **Logic:**
    -   Inside the new endpoint handler in `surfdata.py`, call the `get_all_regions()` function from `database_utils.py`.
    -   Format the returned list into the standard success JSON structure.
    -   Return the JSON response.
-   **Example Response:**
    ```json
    {
      "status": "success",
      "data": [
        "East Coast",
        "West Coast",
        "Puerto Rico"
      ]
    }
    ```
