# Journal Page Stats Feature Plan

This document outlines the plan to implement the "Stats" tab on the user Journal page. The implementation will be broken into two main phases: Backend and Frontend.

## Backend Plan

1.  **Create a New Stats Database Function:**
    *   In `database_utils.py`, create a new function: `get_user_stats(user_id)`.
    *   This function will calculate and return aggregate statistics for the specified `user_id`.
    *   The function will compute the following metrics:
        *   `total_sessions`: The total count of surf sessions for the user.
        *   `total_surf_time`: The sum of the duration of all sessions.
        *   `average_fun_rating`: The average of the `fun_rating` across all sessions.

2.  **Create a New API Endpoint:**
    *   In `surfdata.py`, add a new route: `/api/users/<string:profile_user_id>/stats`.
    *   This endpoint will be protected and will call the `get_user_stats(profile_user_id)` function.
    *   It will return a JSON object with the three calculated statistics.

## Frontend Plan

1.  **Update `JournalPage.jsx` Data Fetching:**
    *   Introduce new state variables: `stats`, `statsLoading`, and `statsError`.
    *   Modify the main `useEffect` hook to fetch data from the new `/api/users/<user_id>/stats` endpoint when the `currentTab` is 'stats'.
    *   Store the fetched data in the `stats` state.

2.  **Create `StatsDisplay.jsx` Component:**
    *   Create a new reusable component at `frontend/src/components/StatsDisplay.jsx`.
    *   This component will accept `stats`, `loading`, and `error` as props.
    *   It will be responsible for rendering the three key statistics in a clear and user-friendly way (e.g., in separate `Card` components).
    *   It will handle displaying a loading spinner or an error message as needed.

3.  **Integrate into `JournalPage.jsx`:**
    *   In the render function of `JournalPage.jsx`, replace the current placeholder for the 'stats' tab with the `<StatsDisplay />` component.
    *   Pass the `stats`, `statsLoading`, and `statsError` state variables as props to the component.
