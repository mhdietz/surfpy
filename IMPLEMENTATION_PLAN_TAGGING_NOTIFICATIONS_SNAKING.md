# Implementation Plan: Tagging, Notifications, and Session Snaking

This document outlines the phased approach to implementing the new features: tagging users in sessions, a notification system, and the ability to "snake" (copy) sessions from notifications.

## Phase 1: Backend Development

### 1. Database Schema for Notifications
   - **Action**: Define and create a new `notifications` table in the PostgreSQL database.
   - **Schema**:
     ```sql
     CREATE TABLE notifications (
         id SERIAL PRIMARY KEY,
         recipient_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
         sender_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
         session_id INTEGER REFERENCES surf_sessions_duplicate(id) ON DELETE CASCADE,
         type VARCHAR(255) NOT NULL CHECK (type IN ('session_tag', 'session_snake')),
         read BOOLEAN DEFAULT false,
         created_at TIMESTAMPTZ DEFAULT NOW()
     );

     -- Index for efficient querying of user's notifications
     CREATE INDEX idx_notifications_recipient_user_id ON notifications(recipient_user_id);

     -- Unique constraint to prevent duplicate notifications for the same user, session, and type.
     -- This aligns with the "one notification per user per session" rule.
     ALTER TABLE notifications
     ADD CONSTRAINT unique_notification_per_session
     UNIQUE (recipient_user_id, session_id, type);
     ```
   - **Note**: This table will be created manually via the Supabase dashboard or a direct SQL command.

### 2. Notification Logic in `database_utils.py`
   - **Action**: Implement a new function `create_notification` to insert records into the `notifications` table.
   - **Action**: Modify the `create_session_with_participants` function to call `create_notification` whenever a user is successfully tagged in a session. Ensure notification rules (notifying only once, not self, etc.) are respected.

### 3. Notification API Endpoints in `surfdata.py`
   - **Action**: Create `GET /api/notifications` endpoint: Fetches all unread notifications for the authenticated user, including details about the sender and the associated session.
   - **Action**: Create `GET /api/notifications/count` endpoint: Returns the count of unread notifications for the authenticated user, for displaying a badge in the UI.
   - **Action**: Create `POST /api/notifications/<notification_id>/read` endpoint: Marks a specific notification as read.

### 4. "Snake It" Session API Endpoint in `surfdata.py`
   - **Action**: Create `POST /api/surf-sessions/<int:session_id>/snake` endpoint.
   - **Functionality**:
     - Fetches details of the original session (`session_id`).
     - Creates a *new* session for the current authenticated user, copying the spot, date, time, title, and surf data from the original.
     - **Crucially**: Copies all participants from the original session but sets their `notify` flag to `false` for the new session, preventing notification loops.
     - Sets notes and fun rating to blank/null for the new session.
     - Returns the `id` of the newly created session.

## Detailed Backend Feature Breakdown

This section provides a more robust, implementation-specific explanation of how the new backend features work.

### User Tagging & Notification Generation

This process is initiated when a user creates or updates a session and includes other users in the `tagged_users` array.

1.  **Trigger**: The process starts in `surfdata.py` within the `create_surf_session` or `update_surf_session` endpoints. The request payload contains a `tagged_users` array of user UUIDs.

2.  **Logic Flow**:
    *   The API endpoint calls the `database_utils.create_session_with_participants` function.
    *   Inside this function, a loop iterates through each `tagged_user_id` provided.
    *   For each ID, a new record is inserted into the `session_participants` table to link the user to the new session.
    *   Immediately following a successful insertion into `session_participants`, the `create_notification` function is called. This function inserts a new row into the `notifications` table.

3.  **Rules Enforcement**:
    *   **No Self-Notification**: A check (`if tagged_user_id and str(tagged_user_id) != str(creator_user_id)`) within `create_session_with_participants` ensures that the session creator cannot be tagged in their own session, thus preventing self-notification.
    *   **One Notification Per Session**: The `notifications` table has a `UNIQUE` constraint on the combination of `(recipient_user_id, session_id, type)`. This database-level rule automatically prevents duplicate notifications from being created if a user were to be tagged multiple times for the same session.

### Notification System (API & Data)

This system provides the necessary endpoints for the frontend to display and manage notifications.

1.  **Data Retrieval (`GET /api/notifications`)**:
    *   This endpoint calls `database_utils.get_notifications`, which retrieves all notifications for the authenticated user.
    *   The underlying SQL query performs `JOIN` operations across three tables:
        *   `notifications`: The primary source.
        *   `auth.users`: To get the `display_name` of the **sender**.
        *   `surf_sessions_duplicate`: To get the `session_name` and `location` for context.
    *   The result is a comprehensive list of notification objects, each containing all necessary information for the frontend to render a meaningful message (e.g., "Frank tagged you in 'Epic Winter Swell at Lido'").

2.  **Unread Count (`GET /api/notifications/count`)**:
    *   This is a lightweight performance optimization for the UI. It calls `database_utils.get_unread_notifications_count`.
    *   It executes a simple `SELECT COUNT(*)` query on the `notifications` table with a `WHERE` clause to find records where `recipient_user_id` matches and `read = FALSE`. This is much faster than fetching the full list of notifications.

3.  **Marking as Read (`POST /api/notifications/<id>/read`)**:
    *   This endpoint calls `database_utils.mark_notification_read`.
    *   It performs an `UPDATE` query to set `read = TRUE` on a specific notification.
    *   For security, the `WHERE` clause of the query checks for both the `notification_id` AND the `recipient_user_id` (from the JWT token). This ensures that a user can only mark their own notifications as read.

### 'Snake It' (Session Copying) Workflow

This is the most complex flow, combining session creation, participant copying, and notification logic.

1.  **Trigger**: The flow begins when a user clicks the "Snake It" button in the frontend, which sends a request to `POST /api/surf-sessions/<original_session_id>/snake`.

2.  **Backend Process (`copy_session_as_new_user` function)**:
    *   **Fetch Original Data**: The function first calls `get_session_detail` on the `original_session_id` to retrieve the complete data object for the original session.
    *   **Prepare New Data**: A new `new_session_data` dictionary is built by copying key fields (`location`, `session_name`, `session_started_at`, `raw_swell`, `raw_met`, etc.). `session_notes` and `fun_rating` are explicitly set to `None` as per the requirements.
    *   **Gather Participants**: The function retrieves all participants from the original session. A list comprehension `[p['user_id'] for p in original_participants if p['user_id'] != new_user_id]` then creates the final list of users to be tagged. This logic correctly includes the original creator and other tagged users, while excluding the user who is snaking the session (as they will become the new creator).
    *   **Create New Session**: The `create_session_with_participants` function is called. It's passed the `new_session_data`, the snaker's ID as the new `creator_user_id`, and the filtered list of participants to tag.
    *   **Prevent Notification Loops**: This is the most critical rule. The call to `create_session_with_participants` explicitly includes the argument `send_notifications=False`. This parameter prevents the function from entering the block that calls `create_notification`, thus stopping a chain reaction of notifications for all copied users.
    *   **Return New ID**: Once the new session and its participants are successfully created, the function returns the `id` of the new session. The API endpoint then sends this ID back to the frontend, which can use it to redirect the user to the edit page for their newly snaked session.

## Phase 2: Frontend Development

### 1. User Tagging UI
   - **Action**: Integrate the existing `UserSearch.jsx` component or similar functionality into the session creation and editing forms.
   - **Goal**: Allow users to select and tag other users when creating or updating a session.

### 2. Notification User Interface
   - **Action**: Add a notification icon with an unread count badge to the `Navigation.jsx` component. This badge will fetch its count from `GET /api/notifications/count`.
   - **Action**: Create a new page component, `NotificationsPage.jsx`, accessible via a route (e.g., `/notifications`).
   - **Functionality**:
     - Fetches and displays the user's notifications using `GET /api/notifications`.
     - Each notification item will display the sender, session title, spot, and date.
     - Each notification will include two buttons:
       - **"View"**: Navigates to the `SessionDetailPage.jsx` for the associated session.
       - **"Snake It"**: Initiates the session copying process.

### 3. "Snake It" Workflow (Client-Side)
   - **Action**: Implement click handler for the "Snake It" button on notification items.
   - **Functionality**:
     - Calls the `POST /api/surf-sessions/<session_id>/snake` API endpoint.
     - Upon successful response, redirects the user to the edit page for the newly created session (e.g., `/sessions/edit/<new_session_id>`), allowing them to adjust details before saving.

## Backend Implementation Notes & Fixes

During the backend development and testing phase, two bugs were identified and resolved:

1.  **`tide_station_id` Data Type Mismatch**:
    -   **Issue**: An error occurred during the "Snake It" process (`copy_session_as_new_user`) because the `tide_station_id` column is incorrectly typed as `jsonb` in the database. When copying a session, a fetched integer ID was being rejected on re-insertion.
    -   **Fix**: The `create_session` function in `database_utils.py` was modified to explicitly wrap the `tide_station_id` value with `psycopg2.extras.Json()`. This ensures the data is correctly formatted for the `jsonb` column, resolving the `DatatypeMismatch` error.

2.  **Incorrect Participant Copying in "Snake It"**:
    -   **Issue**: When a session was "snaked," the original creator of that session was not being added as a participant to the new session.
    -   **Fix**: The logic in `copy_session_as_new_user` was corrected. It now correctly gathers all participants from the original session (including the creator) and only filters out the user who is performing the "snake" action, as they become the new creator.
