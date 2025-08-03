# Plan: User-Created Sessions Endpoint

This document outlines the plan to create a new API endpoint for fetching all surf sessions created by a specific user.

## 1. Objective

The goal is to create a `GET /api/users/{user_id}/sessions` endpoint that returns a list of all surf sessions a user has personally created. This endpoint is designed to display a user's personal surf journal (e.g., "Martin's surf logs") and will **not** include sessions where the user was only tagged as a participant.

This new endpoint will eventually replace the legacy `?user_only=true` parameter on the main sessions endpoint.

## 2. Endpoint Definition

-   **Method**: `GET`
-   **Path**: `/api/users/<string:profile_user_id>/sessions`
-   **URL Parameters**:
    -   `profile_user_id` (string, required): The UUID of the user whose created sessions are being requested. This can also be the string `"me"` as an alias for the authenticated user.
-   **Authentication**: Required. The endpoint will be protected by the `@token_required` decorator.

## 3. Authorization

-   Any authenticated user can view the created sessions of any other user.
-   The `user_id` from the JWT token (the "viewer") will be used to determine the `viewer_has_shakaed` status for each session.

## 4. Data Payload (JSON Response)

The endpoint will return a JSON object with a `data` key containing an array of session objects, identical in structure to the existing session endpoints.

## 5. Implementation Steps

### Step 1: Database Layer (`database_utils.py`)

1.  **Modify the existing `get_user_sessions` function**.
    -   The current function `get_user_sessions(user_id)` implicitly fetches sessions for the authenticated user.
    -   It will be modified to `get_user_sessions(profile_user_id, viewer_user_id)`.
2.  **Function Logic**:
    -   The core SQL query logic from the original `get_user_sessions` will be preserved.
    -   The `WHERE` clause will be updated to filter sessions where `surf_sessions_duplicate.user_id = profile_user_id`.
    -   The `viewer_user_id` will be used in the subquery for calculating the `viewer_has_shakaed` flag, ensuring the reaction data is always relative to the person making the request.

### Step 2: API Layer (`surfdata.py`)

1.  **Create a new Flask route**:
    ```python
    @app.route('/api/users/<string:profile_user_id>/sessions', methods=['GET'])
    @token_required
    def get_user_journal_sessions(viewer_user_id, profile_user_id):
        # ... implementation ...
    ```
2.  **Route Logic**:
    -   The function will take two arguments: `viewer_user_id` (from the `@token_required` decorator) and `profile_user_id` (from the URL).
    -   **Handle 'me' alias**: It will check if `profile_user_id == 'me'`. If true, it will replace it with the `viewer_user_id`.
    -   It will call the modified `database_utils.get_user_sessions()` function, passing both `profile_user_id` and `viewer_user_id`.
    -   It will return the data from the database function in the standard JSON success format.

### Step 3: Testing

1.  Make a `GET` request to `/api/users/me/sessions` and verify it returns the authenticated user's created sessions.
2.  Make a `GET` request to `/api/users/{some_other_uuid}/sessions` and verify it returns that specific user's created sessions.
3.  Verify that sessions where the user was only a participant are **NOT** included in the response.
4.  Verify that the `shakas.viewer_has_shakaed` flag is correct based on the authenticated user making the request.

## 6. Future Deprecation

-   Upon successful deployment of this new endpoint, the `?user_only=true` query parameter on the `GET /api/surf-sessions` endpoint will be considered **deprecated**.
-   Clients should be updated to use `GET /api/users/me/sessions` for fetching the current user's sessions and `GET /api/surf-sessions` (with no parameters) for the global feed.
