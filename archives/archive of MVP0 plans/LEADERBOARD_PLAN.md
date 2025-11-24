# Leaderboard Feature Plan

This document outlines the plan to implement the community Leaderboard, which will be accessible as a tab on the Feed page.

This plan follows a revised approach to create a dedicated, efficient backend endpoint for the leaderboard instead of reusing the broader `/api/dashboard` endpoint.

## Backend Plan

1.  **Create a New Database Function:**
    *   In `database_utils.py`, create a new function: `get_leaderboard(year=None, stat='sessions')`.
    *   This function will be responsible for querying and aggregating data specifically for the leaderboard.
    *   It will group sessions by user and calculate key metrics: total sessions, total surf time, and average fun rating.
    *   The function will accept parameters to allow filtering by `year` and sorting by a specific `stat` (e.g., 'sessions', 'time').
    *   The output will be a ranked list of users and their relevant stats.

2.  **Create a New API Endpoint:**
    *   In `surfdata.py`, add a new, protected route: `/api/leaderboard`.
    *   The endpoint will accept optional query parameters, such as `?year=2024` and `?stat=sessions`, to pass to the database function.
    *   It will return a clean, lean JSON array containing only the ranked user data required for the leaderboard.

## Frontend Plan

1.  **Create `Leaderboard.jsx` Component:**
    *   Create a new component at `frontend/src/components/Leaderboard.jsx`.
    *   This component will encapsulate all UI and logic for the leaderboard.
    *   **Data Fetching**: It will call the new `/api/leaderboard` endpoint to get its data.
    *   **State Management**: It will manage its own state for loading, errors, leaderboard data, and the currently selected filter values (e.g., year).
    *   **UI**:
        *   It will feature a dropdown menu to filter the leaderboard by year.
        *   It will render the data as a ranked list, showing each user's rank, display name, and the relevant statistic.
        *   The currently logged-in user's position on the leaderboard will be highlighted for easy visibility.

2.  **Integrate into `Feed.jsx`:**
    *   In `Feed.jsx`, the placeholder content for the "Leaderboard" tab will be replaced with the new `<Leaderboard />` component.
