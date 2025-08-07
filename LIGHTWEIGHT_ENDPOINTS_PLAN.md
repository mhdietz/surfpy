# Lightweight Session Endpoints Refactoring Plan

## 1. Background & Goal

To improve frontend performance and create a faster user experience, we need to reduce the amount of data sent to list views like the main feed and user journals. These views do not require the large `raw_swell` and `raw_met` JSON objects.

The goal is to refactor the session endpoints to provide two distinct views:
1.  A **lightweight summary view** for lists (feeds, journals).
2.  A **full detail view** for a single session page.

This will be achieved by making the filtering logic server-side, ensuring that the client only ever receives the data it needs.

## 2. API Endpoint Strategy

The `view` will be determined by the endpoint called, not by a query parameter.

### a. Lightweight List Endpoints

These endpoints will always return a lightweight array of session objects, excluding the `raw_swell` and `raw_met` fields. They will, however, support server-side filtering based on parameters from those raw fields.

-   **Main Feed:** `GET /api/surf-sessions`
-   **Journal View:** `GET /api/users/{user_id}/sessions` (and its `me` alias)

### b. Full Detail Endpoint

This endpoint's behavior will not change. It will always return the complete session object with all fields, including `raw_swell` and `raw_met`.

-   **Session Detail:** `GET /api/surf-sessions/{id}`

## 2.5. API Response Fields

To ensure clarity, the exact data contract for each view is defined below.

### a. Lightweight Summary View (`/api/surf-sessions` and `/api/users/.../sessions`)

This view is designed for speed and will include only the essential data needed to render a list item in a feed or journal.

**Included Fields:**
*   `id`
*   `session_started_at` (ISO 8601 UTC String)
*   `session_ended_at` (ISO 8601 UTC String)
*   `created_at` (ISO 8601 UTC String)
*   `location`
*   `session_name`
*   `session_notes`
*   `fun_rating`
*   `user_id`
*   `display_name` (The creator's name)
*   `user_email`
*   `participants` (The lightweight list of tagged users)
*   `shakas` (The object containing count, preview, and viewer status)

**Specifically Excluded Fields:**
*   `raw_swell`
*   `raw_met`
*   The entire `tide` object and its contents.

### b. Full Detail View (`/api/surf-sessions/{id}`)

This view will return the complete session object, including all the detailed oceanographic data needed for the session detail page.

**Included Fields:**
*   All fields from the **Lightweight Summary View**.
*   **PLUS:**
    *   `raw_swell` (The full JSONB object)
    *   `raw_met` (The full JSONB object)
    *   The complete `tide` object.

## 3. Filtering Strategy (Server-Side)

The lightweight list endpoints will support the following query parameters for filtering. The database will perform the filtering, and only the matching results will be returned.

-   **Surf Region:**
    -   `?region=<region-slug>` (e.g., `?region=east-coast`)
-   **Swell Height (in feet):**
    -   `?min_swell_height=<number>`
    -   `?max_swell_height=<number>`
-   **Swell Period (in seconds):**
    -   `?min_swell_period=<number>`
    -   `?max_swell_period=<number>`
-   **Swell Direction:**
    -   `?swell_direction=<cardinal>` (e.g., `N`, `SW`, `W`, `NNE`). The backend will map this to the correct degree range for the query.

## 4. Backend Implementation Plan

### a. `database_utils.py`

We will create two distinct and clearly named functions:

1.  **`get_session_detail(session_id, viewer_id)`**
    -   **Purpose:** To fetch a single, complete session object.
    -   **Details:** This will be a simple refactoring of the existing `get_session` function. It will `SELECT *` and return all fields.
    -   **Called by:** `GET /api/surf-sessions/{id}`

2.  **`get_session_summary_list(viewer_id, profile_user_id_filter=None, filters={})`**
    -   **Purpose:** To fetch a filtered list of lightweight session summaries.
    -   **Details:** This new function will be the core of the implementation.
        -   The `SELECT` clause will explicitly list only the lightweight fields (no `raw_*` data).
        -   It will contain logic to dynamically build a `WHERE` clause based on the `profile_user_id_filter` and the `filters` dictionary passed in from the API layer.
        -   It will handle the logic for mapping cardinal swell directions to degree ranges.
    -   **Called by:** `GET /api/surf-sessions` and `GET /api/users/{user_id}/sessions`.

### b. `surfdata.py`

The API endpoints will be simplified to call the appropriate new function from `database_utils`.

-   The `get_surf_session` (by id) endpoint will call `get_session_detail`.
-   The `get_surf_sessions` (all) and `get_user_journal_sessions` endpoints will parse the filter parameters from the request URL and pass them into the new `get_session_summary_list` function.

## 5. Acceptance Criteria

-   The main feed (`/api/surf-sessions`) loads quickly, returning a lightweight JSON payload.
-   The journal views (`/api/users/.../sessions`) load quickly, returning a lightweight JSON payload.
-   Both feed and journal views can be filtered by region, swell height, period, and direction.
-   The session detail view (`/api/surf-sessions/{id}`) continues to return all oceanographic data.
-   The backend code has a clear separation of concerns between the detail and summary list functions.
