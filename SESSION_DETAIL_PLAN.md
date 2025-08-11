# Session Detail View Implementation Plan

This document outlines the phased approach for implementing the Session Detail View in the frontend. Each step will be implemented and reviewed before proceeding to the next.

## Phase 1: Early Frontend Integration (Routing & Placeholder Component) - COMPLETE ✅

**Objective:** To establish the routing and a basic component structure, allowing for early visual verification in the local development environment.

*   **Task 1.1:** Create a new React component `SessionDetail.jsx` in `frontend/src/pages/`. Initially, this component will be a placeholder, displaying a simple message like "Loading session..." or "Session ID: {id}". - **COMPLETE ✅**
*   **Task 1.2:** Configure the frontend routing (likely in `frontend/src/App.jsx`) to include a route for `/session/:id` that renders the `SessionDetail.jsx` component. Ensure this route is protected by `ProtectedRoute`. - **COMPLETE ✅**

## Phase 2: Data Fetching and Basic Session Information Display

**Objective:** To integrate the component with the backend API and display the fundamental session details.

*   **Task 2.1:** Modify `SessionDetail.jsx` to fetch session data from the `/api/surf-sessions/:id` endpoint using `apiCall`.
*   **Task 2.2:** Implement loading and error states (e.g., a spinner for loading, a message for errors or session not found).
*   **Task 2.3:** Display the following core session information:
    *   `session_name`
    *   `location`
    *   `fun_rating`
    *   `session_started_at` (formatted)
    *   `session_ended_at` (formatted)
    *   `display_name` (creator)
    *   `participants` (list of names)
    *   `shakas` (count and preview of users)

## Phase 3: Swell Data Display

**Objective:** To display all relevant swell parameters from the fetched data.

*   **Task 3.1:** Add a dedicated section within `SessionDetail.jsx` to render swell data.
*   **Task 3.2:** Parse the `raw_swell[0].swell_components` object and display the `direction`, `height`, and `period` for each swell component (e.g., `swell_1`, `swell_2`, etc.).

## Phase 4: Wind Data Display (Conditional Rendering)

**Objective:** To display meteorological data, adapting to whether it comes from a weather station or a NOAA buoy.

*   **Task 4.1:** Add a dedicated section within `SessionDetail.jsx` to render wind data.
*   **Task 4.2:** Implement conditional rendering logic:
    *   If `raw_met[0]` contains additional parameters like `air_temperature`, `dewpoint_temperature`, `pressure`, `pressure_tendency`, `water_temperature`, or `wind_gust` (indicating NOAA buoy data), display all these parameters along with `wind_speed` and `wind_direction`.
    *   Otherwise (indicating weather station data, typically only `wind_speed` and `wind_direction` are present), display only `wind_speed` and `wind_direction`.

## Phase 5: Tide Data Display (with Timezone Conversion)

**Objective:** To display tide information, ensuring correct timezone conversion for future events.

*   **Task 5.1:** Add a dedicated section within `SessionDetail.jsx` to render tide data.
*   **Task 5.2:** Display `water_level`, `direction`, `next_event_type`, and `next_event_height`.
*   **Task 5.3:** Convert the `next_event_at` UTC timestamp to the user's local timezone before displaying it.

## Phase 6: Notes and Additional Information Display

**Objective:** To display the session notes and any other supplementary details.

*   **Task 6.1:** Add a section to display `session_notes`.
*   **Task 6.2:** Include any other general session details that are not part of the oceanographic data.

## Phase 7: Styling and Polish

**Objective:** To apply consistent styling and ensure a polished user interface.

*   **Task 7.1:** Apply Tailwind CSS utility classes throughout `SessionDetail.jsx` to match the project's mobile-first design principles.
*   **Task 7.2:** Refine the layout and spacing to ensure readability and a visually appealing presentation.

## Phase 8: Comprehensive Error and Loading States

**Objective:** To ensure robust handling of various data fetching scenarios.

*   **Task 8.1:** Review and enhance the loading spinner and error messages for clarity and user experience.
*   **Task 8.2:** Ensure graceful handling of cases where certain data fields (e.g., `raw_swell`, `raw_met`, `tide`) might be missing or empty.
