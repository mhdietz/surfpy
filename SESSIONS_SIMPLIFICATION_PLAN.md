# Plan: Session Endpoint Simplification

This plan outlines the steps to implement lightweight session views for the main feed and user journals, as detailed in the `sessions_simplification_issue.md` file. The goal is to improve frontend performance by reducing response size and enabling powerful, efficient server-side filtering.

### Step 1: Create the Core Lightweight Database Function

The foundation of this change will be a new, versatile function in `database_utils.py` that can handle all lightweight session retrieval.

-   **Action:** Create a new function `get_sessions_lightweight`.
-   **File:** `database_utils.py`
-   **Details:**
    -   This function will accept `viewer_id`, an optional `user_id_filter`, an optional `location_slug_filter`, and a `filters` dictionary for oceanographic filtering.
    -   The SQL `SELECT` clause will be minimal, excluding `raw_swell`, `raw_met`, and detailed tide columns (`session_water_level`, etc.).
    -   The query will correctly join `session_participants` and `session_shakas` to provide the necessary social data, resolving the inconsistency previously noted in the `get_sessions_by_location` function.
    -   The `WHERE` clause will be built dynamically to support filtering by user, location, and other criteria from the `filters` argument.

### Step 2: Update API Endpoints in `surfdata.py`

Next, we'll modify the Flask route handlers to use the new database function based on a `view` query parameter.

-   **Action:** Modify the `get_surf_sessions`, `get_user_journal_sessions`, and `get_location_surf_sessions` endpoints.
-   **File:** `surfdata.py`
-   **Details:**
    1.  **`GET /api/surf-sessions`**:
        -   Read the `view` query parameter (e.g., `?view=feed`).
        -   If `view == 'feed'`, call `get_sessions_lightweight(viewer_id=user_id)`.
        -   Otherwise, maintain the existing behavior of returning full data.
        -   Remove the deprecated `user_only=true` logic.
    2.  **`GET /api/users/<profile_user_id>/sessions`**:
        -   Read the `view` query parameter (e.g., `?view=profile`).
        -   If `view == 'profile'`, call `get_sessions_lightweight(viewer_id=viewer_user_id, user_id_filter=profile_user_id)`.
        -   Otherwise, maintain the existing behavior.
    3.  **`GET /api/surf-sessions/location/<location_slug>`**:
        -   Update this endpoint to use `get_sessions_lightweight(viewer_id=user_id, location_slug_filter=location_slug)` to ensure participant data is consistent with the rest of the app.

### Step 3: Implement and Verify Filtering Logic

We will implement a flexible filtering system by passing a `filters` dictionary from the API layer down to the new `get_sessions_lightweight` function.

-   **Action:** Add logic to parse the `filters` dictionary and construct the appropriate SQL `WHERE` clauses.
-   **File:** `database_utils.py`
-   **Details:**
    -   The implementation will safely construct queries to filter on nested JSONB data.
    -   **Filtering Model:**
        -   The API will accept query parameters (e.g., `min_swell_height=2`).
        -   These will be passed to the database function in a `filters` dictionary.
        -   The function will build a parameterized `WHERE` clause.
    -   **Initial Filterable Fields:**
        -   From `raw_swell`: `significant_wave_height`, `dominant_period`, `mean_wave_direction`.
        -   From `raw_met`: `wind_speed`, `wind_direction`, `air_temperature`.

### Step 4: Create Tests for Verification

To ensure the changes are working correctly and haven't introduced regressions, we'll add targeted tests.

-   **Action:** Create a new test file `test_session_api_views.py`.
-   **File:** `test_session_api_views.py`
-   **Details:**
    -   Add tests to verify that the `?view=feed` and `?view=profile` parameters return a lightweight data structure (i.e., `raw_swell` is not present).
    -   Add tests to confirm that the default (full) views and the `GET /api/surf-sessions/<id>` endpoint are unaffected and still return all data.
    -   Add tests for the new filtering logic to ensure it correctly filters the results.

### Step 5: Final Review and Cleanup

After implementation and testing, we will perform a final review.

-   **Action:** Review the modified code for clarity, performance, and adherence to the project's coding standards.
-   **Details:**
    -   Confirm that all acceptance criteria from the issue document are met.
    -   Remove any temporary or redundant code.
    -   Ensure the new test file is clean and easy to understand.
