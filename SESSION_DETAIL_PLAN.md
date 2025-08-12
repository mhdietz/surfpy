# Session Detail View Implementation Plan

This document outlines the phased approach for implementing the Session Detail View in the frontend. Each step will be implemented and reviewed before proceeding to the next.

## Phase 1: Early Frontend Integration (Routing & Placeholder Component) - COMPLETE ✅

**Objective:** To establish the routing and a basic component structure, allowing for early visual verification in the local development environment.

*   **Task 1.1:** Create a new React component `SessionDetail.jsx` in `frontend/src/pages/`. Initially, this component will be a placeholder, displaying a simple message like "Loading session..." or "Session ID: {id}". - **COMPLETE ✅**
*   **Task 1.2:** Configure the frontend routing (likely in `frontend/src/App.jsx`) to include a route for `/session/:id` that renders the `SessionDetail.jsx` component. Ensure this route is protected by `ProtectedRoute`. - **COMPLETE ✅**

## Phase 2: Data Fetching and Basic Session Information Display

**Objective:** To integrate the component with the backend API and display the fundamental session details.

*   **Task 2.1 (Mockup): Mockup Display with Static Data:** Before connecting to the API, update `SessionDetail.jsx` to render a complete but static view using hardcoded mock data. This allows for rapid UI development and styling of the basic session info display.
*   **Task 2.2 (API Call & Verification):** In `SessionDetail.jsx`, create an `async` function to call the `/api/surf-sessions/:id` endpoint. For now, call this function inside a `useEffect` and simply `console.log()` the response to verify the connection.
*   **Task 2.3 (State Management Setup):** Introduce state variables for `session`, `isLoading`, and `error` using `useState`.
*   **Task 2.4 (Connecting API to State):** Modify the `useEffect` hook to set the component's state based on the API call's outcome.
*   **Task 2.5 (Conditional Rendering Logic):** Update the JSX to conditionally render a spinner, an error message, or the session view based on the component's state.
*   **Task 2.6 (Connecting Live Data to UI):** Replace the hardcoded mock data with the live data from the `session` state object.

## Phase 3: Swell Data Display

**Objective:** To display all relevant swell parameters from the fetched data.

*   **Task 3.1 (Mockup):** Create a dedicated `SwellDisplay` component. Use hardcoded mock `raw_swell` data to build the UI that loops through and displays each swell component's height, period, and direction.
*   **Task 3.2 (Integration):** Pass the actual `raw_swell` array from the fetched session data into the `SwellDisplay` component.

## Phase 4: Wind Data Display (Conditional Rendering)

**Objective:** To display meteorological data, adapting to whether it comes from a weather station or a NOAA buoy.

*   **Task 4.1 (Mockup):** Create a `WindDisplay` component. This component will contain the conditional logic to render different fields based on the data it receives. Test its logic by passing it both shapes of mock `raw_met` data (the simple weather station version and the detailed NOAA buoy version).
*   **Task 4.2 (Integration):** Pass the actual `raw_met` data from the fetched session into the `WindDisplay` component.

## Phase 5: Tide Data Display (with Timezone Conversion)

**Objective:** To display tide information, ensuring correct timezone conversion for future events.

*   **Task 5.1 (Mockup):** Create a `TideDisplay` component. Use hardcoded mock `tide` data to build the UI, including the logic to format the `next_event_at` timestamp.
*   **Task 5.2 (Integration):** Pass the actual `tide` object from the fetched session into the `TideDisplay` component.

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
