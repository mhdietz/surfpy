# Journal Page Implementation Plan

This document outlines the phased implementation plan for the Journal Page feature, focusing on displaying surf sessions and implementing filtering capabilities. The "Stats" tab functionality is explicitly excluded from this phase.

## Phase 1: Backend Enhancement - New User Profile Endpoint

*   **Goal:** Create a dedicated API endpoint to fetch a user's display name and basic profile information, ensuring the display name is always available regardless of session count.
*   **Steps:**
    1.  **`database_utils.py`:** Add a new function, `get_user_profile_by_id(user_id)`, to query the `auth.users` table and return the `id`, `email`, and `display_name` for the given `user_id`.
    2.  **`surfdata.py`:** Add a new `GET` endpoint, `/api/users/<string:user_id>/profile`, which will call the new `database_utils` function. This endpoint must be protected by `@token_required`.

## Phase 2: Page Scaffolding and Routing

*   **Goal:** Create the basic `JournalPage` component and integrate it into the app's navigation.
*   **Steps:**
    1.  Create `frontend/src/pages/JournalPage.jsx`.
    2.  Set up the component to read the `userId` from the URL (`/journal/:userId`). It will handle the `'me'` alias to refer to the currently authenticated user.
    3.  Add the new route `/journal/:userId` to `App.jsx` within the `ProtectedRoute`.

## Phase 3: User Profile and Session Data Fetching

*   **Goal:** Fetch and display the user's display name and their surf sessions.
*   **Steps:**
    1.  In `JournalPage.jsx`, use the new `/api/users/:userId/profile` endpoint to fetch the `display_name` of the user whose journal is being viewed. Display this name prominently at the top of the page.
    2.  Fetch session data from the existing `/api/users/:userId/sessions` endpoint.
    3.  Use the existing `SessionsList.jsx` component to display the fetched sessions, handling loading, error, and empty states.

## Phase 4: Minimalist Filter UI Implementation

*   **Goal:** Implement the toggleable filter section.
*   **Steps:**
    1.  Create `frontend/src/components/JournalFilter.jsx`. This component will contain all the individual filter controls (Region, Swell Height, Swell Period, Swell Direction).
    2.  Implement a toggle mechanism within `JournalFilter.jsx` (e.g., a button that expands/collapses a div) to reveal or hide the filter options.
    3.  Add `JournalFilter.jsx` to `JournalPage.jsx`.

## Phase 5: Filter Logic and API Integration

*   **Goal:** Make the filters functional by connecting them to the API and updating the view.
*   **Steps:**
    1.  Fetch the list of available regions from the `/api/regions` endpoint and populate the "Region" filter dropdown in `JournalFilter.jsx`.
    2.  Implement state management in `JournalPage.jsx` to hold the current filter values.
    3.  When a filter value changes, update the state and re-fetch the session data from the backend, passing the filter values as query parameters to `/api/users/:userId/sessions`.
    4.  Update the URL with the current filter parameters using `react-router-dom`'s `useSearchParams` hook.
