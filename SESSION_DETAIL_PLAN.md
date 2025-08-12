# Session Detail View Implementation Plan

This document outlines the phased approach for implementing the Session Detail View in the frontend. Each step will be implemented and reviewed before proceeding to the next.

## Phase 1: Early Frontend Integration (Routing & Placeholder Component) - COMPLETE ✅

**Objective:** To establish the routing and a basic component structure, allowing for early visual verification in the local development environment.

*   **Task 1.1:** Create a new React component `SessionDetail.jsx` in `frontend/src/pages/`. Initially, this component will be a placeholder, displaying a simple message like "Loading session..." or "Session ID: {id}". - **COMPLETE ✅**
*   **Task 1.2:** Configure the frontend routing (likely in `frontend/src/App.jsx`) to include a route for `/session/:id` that renders the `SessionDetail.jsx` component. Ensure this route is protected by `ProtectedRoute`. - **COMPLETE ✅**

## Phase 2: Data Fetching and Basic Session Information Display - COMPLETE ✅

**Objective:** To integrate the component with the backend API and display the fundamental session details.

*   **Task 2.1 (Mockup): Mockup Display with Static Data:** Before connecting to the API, update `SessionDetail.jsx` to render a complete but static view using hardcoded mock data. This allows for rapid UI development and styling of the basic session info display. - **COMPLETE ✅**
*   **Task 2.2 (API Call & Verification):** In `SessionDetail.jsx`, create an `async` function to call the `/api/surf-sessions/:id` endpoint. For now, call this function inside a `useEffect` and simply `console.log()` the response to verify the connection. - **COMPLETE ✅**
*   **Task 2.3 (State Management Setup):** Introduce state variables for `session`, `isLoading`, and `error` using `useState`. - **COMPLETE ✅**
*   **Task 2.4 (Connecting API to State):** Modify the `useEffect` hook to set the component's state based on the API call's outcome. - **COMPLETE ✅**
    *   **Verification:** Use React Developer Tools to inspect the `SessionDetail` component and confirm that the `session` state is updated with the live data from the API after the fetch completes.
*   **Task 2.5 (Final Integration):** Combine the conditional rendering logic and live data connection. Add JSX to handle loading and error states, and replace all mock data references in the component with the live data from the `session` state object. Remove the mock data variable. - **COMPLETE ✅**

## Phase 3: UI Refinement & Layout - COMPLETE ✅

**Objective:** To refactor the existing UI to be more compact and mobile-friendly based on user feedback, establishing a clear design pattern before adding more data components.

*   **Task 3.1: Refactor Time Display:** In `SessionDetail.jsx`, update the date formatting logic to display the start and end times in a single, compact line (e.g., "Mon, Aug 11, 2025, 10:10 PM - 12:10 AM"). - **COMPLETE ✅**
*   **Task 3.2: Refactor Swell Display (Order & Compactness):** In `SwellDisplay.jsx`, modify the component to sort swells sequentially (Swell 1, 2, 3...) and render each as a compact, single-line string (e.g., "Swell 2: 2.1 ft @ 8.3s WNW (296°)"). - **COMPLETE ✅**
*   **Task 3.3: Reorder Page Layout:** In `SessionDetail.jsx`, move the refactored `SwellDisplay` component to appear directly below the main session title and time information. - **COMPLETE ✅**

## Phase 4: Swell Data Integration - COMPLETE ✅

**Objective:** To ensure the swell data is correctly passed to the newly refactored component.

*   **Task 4.1 (Integration):** Pass the actual `raw_swell` array from the fetched session data into the `SwellDisplay` component. - **COMPLETE ✅**

## Phase 5: Wind Data Display (Conditional Rendering)

**Objective:** To display meteorological data, adapting to whether it comes from a weather station or a NOAA buoy.

*   **Task 5.1 (Mockup):** Create a `WindDisplay` component. This component will contain the conditional logic to render different fields based on the data it receives. Test its logic by passing it both shapes of mock `raw_met` data (the simple weather station version and the detailed NOAA buoy version).
*   **Task 5.2 (Integration):** Pass the actual `raw_met` data from the fetched session into the `WindDisplay` component.

## Phase 6: Tide Data Display (with Timezone Conversion)

**Objective:** To display tide information, ensuring correct timezone conversion for future events.

*   **Task 6.1 (Mockup):** Create a `TideDisplay` component. Use hardcoded mock `tide` data to build the UI, including the logic to format the `next_event_at` timestamp.
*   **Task 6.2 (Integration):** Pass the actual `tide` object from the fetched session into the `TideDisplay` component.

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
