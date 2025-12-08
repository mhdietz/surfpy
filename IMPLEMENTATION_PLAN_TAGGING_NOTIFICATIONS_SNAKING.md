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
