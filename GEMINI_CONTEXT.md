# Project Surf App: Gemini Context

This document summarizes the current architecture and key features of the Surf App project. It is intended to be a living document, updated as the project evolves, to provide context for future development sessions.

## 1. System Architecture

The application is a full-stack surf logging and forecasting platform. The backend is a Python Flask application that serves a JSON API consumed by a frontend client.

-   **Backend (`surfdata.py`)**: The core of the application is a **Flask API**. It handles all incoming requests, user authentication, and API routing. It uses `Flask-Caching` for performance on data-intensive endpoints like the forecast.

-   **Database (`database_utils.py`)**: All persistent data is stored in a **PostgreSQL** database, managed via the `database_utils.py` module. This module uses the `psycopg2` library to interact with the database. Key tables include `surf_sessions_duplicate` for session logs, `auth.users` for user data, and `surf_spots` for location configurations.

-   **Data Abstraction Layer (`ocean_data/`)**: This Python package serves as a high-level interface for all external oceanographic data. It abstracts the complexities of fetching and processing data, providing simple functions like `get_surf_forecast` and `fetch_swell_data` to the main application. It is responsible for orchestrating data from various sources.

-   **Core Data Engine (`surfpy/`)**: This is a powerful, low-level library that acts as the engine for all data fetching and processing. It interfaces directly with external data sources:
    -   **NDBC Buoys**: Fetches real-time meteorological data, wave spectra, and pre-computed GFS wave model forecast bulletins via `surfpy/buoystation.py`.
    -   **NOAA Tide Stations**: Fetches tide predictions from the NOAA Tides and Currents API via `surfpy/tidestation.py`.
    -   **Weather Models**: Contains logic to interact with weather APIs (`weatherapi.py`) and parse GRIB data from models like GFS (`wavemodel.py`, `weathermodel.py`).

## 2. Core Features & Data Flow

### a. User Authentication & Management
-   **Auth**: User signup and login are handled via Supabase's REST API, as seen in the `/api/auth/signup` and `/api/auth/login` endpoints in `surfdata.py`.
-   **Authorization**: API endpoints are protected using a JWT-based `@token_required` decorator, which validates the user's access token.
-   **User Search**: The `/api/users/search` endpoint allows for finding other users on the platform.

### b. Surf Session Logging (CRUD)
-   **Flow**: When a user logs a session via a `POST` to `/api/surf-sessions`, the backend:
    1.  Validates the user's token and input data.
    2.  Uses `ocean_data.location.get_spot_config` to retrieve the correct buoy and tide station IDs from the `surf_spots` database table.
    3.  Calls the `ocean_data` package to fetch the historical swell, meteorological, and tide data for the session's time and location.
    4.  Saves the complete session object, including the raw ocean data, to the database using `database_utils.create_session`.
-   **Social Tagging**: Users can tag friends in a session, which creates duplicate session entries for each tagged user, linked by a `session_group_id`.

### c. 7-Day Surf Forecast
-   **Endpoint**: A cached `/api/forecast/<spot_name>` endpoint provides a detailed 7-day, hour-by-hour surf forecast.
-   **Data Flow**:
    1.  A request hits the endpoint. The system checks for a fresh (<1 hour) cached forecast.
    2.  If no cache exists, `ocean_data.forecast.get_surf_forecast` is called.
    3.  It retrieves the spot's configuration (buoy IDs, breaking wave parameters) from the database.
    4.  It fetches **historical "actuals"** for the last 24 hours from the NDBC buoy data.
    5.  It fetches **future "forecasts"** by downloading and parsing a GFS wave model **bulletin** from the NOAA website.
    6.  It fetches tide and wind forecasts from the respective APIs.
    7.  The data is resampled into a clean hourly grid, combining actuals and forecasts.
    8.  **Breaking wave height** is calculated for each hour using the spot's specific bathymetry parameters (`depth`, `angle`, `slope`).
    9.  The final JSON is formatted, cached, and returned to the user.

## 3. Key Technical Decisions & Concepts

-   **Database-Driven Configuration**: The application has evolved from hardcoded dictionaries to a database-centric approach. All surf spot configurations, including names, slugs, data source IDs, and breaking wave parameters, are stored in the `surf_spots` table. This makes the system more scalable and easier to manage.
-   **Hybrid Forecast Model**: The forecast intelligently combines real-world historical data ("actuals") with model-based forecast data to provide a seamless timeline from the past into the future.
-   **Breaking Wave Height**: This is a core value proposition. The system uses `surfpy`'s physics-based calculations to translate offshore swell energy into a user-friendly breaking wave height range (e.g., "2-3 ft") based on location-specific parameters.
-   **Backward Compatibility**: The use of a `LEGACY_LOCATION_MAP` in `ocean_data/location.py` ensures that older API clients or bookmarks still function even though the location management system has been updated.
