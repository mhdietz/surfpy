# Year in Review Feature - Implementation Plan

This document outlines the step-by-step implementation for the "Year in Review" feature, including testing and validation points.

## Phase 1: Backend API Development

The goal of this phase is to create a robust and correct API endpoint that provides all the necessary data for the "Year in Review" feature.

### 1.1 Create New Database Function (`database_utils.py`)
-   **Action**: Implement a new function, `get_user_stats_by_year(user_id, year)`.
-   **Logic**: This function will execute SQL queries to aggregate all the required statistics for the given user and year:
    *   Total sessions, total surf hours, and average stoke.
    *   Top 3 sessions, ordered by `fun_rating` (descending).
    *   Session counts for all 12 months of the year (returning 0 for months with no sessions).
    *   Average stoke for months that have sessions (only include months with data).
    *   -   **Status**: `[x] Completed`

### 1.2 Enhance the API Endpoint (`surfdata.py`)
-   **Action**: Modify the existing `/api/users/<profile_user_id>/stats` endpoint.
-   **Status**: `[x] Completed`

### 1.3 Validation (Postman)
-   **Your Task**: Once steps 1.1 & 1.2 are complete, I'll ask you to run a Postman request against your local server: `GET http://localhost:5000/api/users/me/stats?year=2025` (with a valid auth token).
-   **Checkpoints**:
    *   Does the API response structure exactly match the specification from `my_stats_enhancement_year_in_review.md`?
    *   Do the calculated values seem correct for a user with data?
    *   Does the API handle years with zero sessions gracefully (e.g., `total_sessions: 0`, empty arrays for `top_sessions`, `sessions_by_month` with all 0s, `stoke_by_month` empty)?
    *   `most_frequent_buddy`: If you have sessions with tagged users, does it correctly identify the user with whom the `profile_user_id` has the most sessions? Does it include their `name` and `count`? Does it correctly return `null` if no buddy is found or no shared sessions?
-   **Status**: `[x] Completed`

## Phase 2: Frontend - Basic UI & Data Integration

This phase focuses on connecting the frontend to the new API endpoint and building the main structure of the page.

### 2.1 Update API Service (`frontend/src/services/api.js`)
-   **Action**: Update the function that fetches user stats to accept and pass a `year` parameter to the backend API.
-   **Status**: `[ ] Pending`

### 2.2 Add State Management (My Stats Page Component)
-   **Action**: In the React component for the "My Stats" page (`frontend/src/pages/JournalPage.jsx` or relevant component), add state to manage the selected year (e.g., `useState(new Date().getFullYear())`).
-   **Logic**: Use `useEffect` to fetch stats from the API service when the component mounts or when the `selectedYear` state changes. Store the API response in a state variable.
-   **Status**: `[ ] Pending`

### 2.3 Implement Year Filter & Display Basic Stats
-   **Action**: Add the year filter buttons (e.g., for 2025, 2024, 2023) to the UI.
-   **Logic**: Set up `onClick` handlers for the buttons to update the `selectedYear` state. Update the display of the three main stat cards (`Total Sessions`, `Total Surf Time`, `Average Fun`) to reflect data from the new API response.
-   **Status**: `[ ] Pending`

### 2.4 Implement Empty State Display
-   **Action**: Add conditional logic to display the "You haven't logged any sessions..." message.
-   **Logic**: This message should appear when `total_sessions` for a given year is 0, as returned by the API. It should include a "Log Your First Session" CTA linking to `/sessions/create`.
-   **Status**: `[ ] Pending`

### 2.5 Validation (Browser)
-   **Your Task**: Navigate to your stats page (`/journal/me?tab=stats`) on your local frontend deployment.
-   **Checkpoints**:
    *   Are the new year filter buttons displayed?
    *   Does clicking a different year button trigger a new network request (check browser dev tools) and update the three main stat cards correctly?
    *   Does the "empty state" message appear correctly when a year with no sessions is selected, along with the CTA?
-   **Status**: `[ ] Pending`

## Phase 3: Frontend - Charts and Detailed Components

This phase builds the data visualizations and detailed lists.

### 3.1 Install Dependencies
-   **Action**: Install `recharts` and `html2canvas`.
-   **Command**: `npm install recharts html2canvas` in the `frontend` directory.
-   **Status**: `[ ] Pending`

### 3.2 Create "Top Sessions" Component
-   **Action**: Implement a new React component to display the `top_sessions` array.
-   **Logic**: Each session entry should be clickable and link to its corresponding session detail page (`/sessions/:id`).
-   **Status**: `[ ] Pending`

### 3.3 Create Chart Components
-   **Action**: Implement two new React components:
    *   A `SessionsByMonthChart` component using a `BarChart` from `recharts` (feeding it the `sessions_by_month` data).
    *   A `StokeByMonthChart` component using a `LineChart` from `recharts` (feeding it the `stoke_by_month` data).
-   **Status**: `[ ] Pending`

### 3.4 Create "Most Frequent Buddy" Component
-   **Action**: Implement a component to display the `most_frequent_buddy` data.
-   **Logic**: Conditionally render this component only if a buddy exists (i.e., the API returns data for it).
-   **Status**: `[ ] Pending`

### 3.5 Validation (Browser)
-   **Your Task**: View the stats page for a user with sufficient data to populate all new components.
-   **Checkpoints**:
    *   Do all new components (`Top Sessions`, `Sessions by Month Chart`, `Stoke by Month Chart`, `Most Frequent Surf Buddy`) render correctly on the page?
    *   Are the top sessions links functional and do they lead to the correct detail pages?
    *   Do the bar and line charts appear visually correct and accurately represent the data?
    *   Does the "Most Frequent Surf Buddy" component appear when expected and remain hidden when there's no data?
-   **Status**: `[ ] Pending`

## Phase 4: Shareable Image Generation

This phase implements the social sharing feature.

### 4.1 Create Hidden Shareable Card Component
-   **Action**: Implement a new React component (e.g., `ShareableImageCard.jsx`).
-   **Logic**: This component will take the stats data as props and be styled to precisely 1080x1080px, incorporating the specified gradient background, logo, user's name, total stats, best session, and most frequent buddy. It should be rendered on the stats page but positioned off-screen (e.g., `left: -9999px`).
-   **Status**: `[ ] Pending`

### 4.2 Implement Share Button & Logic
-   **Action**: Add the "[📸 Share My [Year] Year in Review]" button to the UI.
-   **Logic**: On click, use `html2canvas` to target the hidden `ShareableImageCard` component, generate a canvas from it, convert the canvas to a PNG, and trigger a download of the image (e.g., `year-in-review-2025.png`).
-   **Status**: `[ ] Pending`

### 4.3 Validation (Browser)
-   **Your Task**: Click the "Share" button on the stats page.
-   **Checkpoints**:
    *   Does a PNG file download?
    *   Is the downloaded image exactly 1080x1080px?
    *   Does the content of the image (logo, user name, stats, etc.) match the design specification from `my_stats_enhancement_year_in_review.md`?
-   **Status**: `[ ] Pending`

## Phase 5: Notification System (Revised)

This phase leverages the existing notification system to announce the feature.

### 5.1 Backend - Bulk Notification Generation (`database_utils.py`)
-   **Action**: Implement a new function, `create_year_in_review_notifications(year_to_notify)`.
-   **Logic**: This function is designed for bulk, system-generated notifications. It will:
    1.  Query for all unique `user_id`s that have logged sessions in the `year_to_notify`.
    2.  Loop through these user IDs.
    3.  For each user, it will insert a new row into the **existing `notifications` table** with:
        *   `type='year_in_review'`
        *   `recipient_user_id` set to the current user in the loop.
        *   `sender_user_id` set to `NULL` (as it's a system notification).
        *   `session_id` set to `NULL` (as it's not tied to a specific session).
        *   `read` set to `FALSE`.
-   **Temporary Endpoint**: I will add a temporary, secure endpoint to `surfdata.py` (e.g., `POST /api/admin/trigger-year-in-review-notifications`) that calls this function for testing purposes. This endpoint will be removed before deployment.
-   **Cleanup Note**: After running your tests and verifying the notifications on the frontend, you **must manually delete** these test notifications from the database to prevent them from appearing to live users when the new frontend code is deployed. You can use the following SQL command:
    ```sql
    DELETE FROM notifications WHERE type = 'year_in_review';
    ```
-   **Status**: `[ ] Pending`

### 5.2 Frontend - Notification Display (Existing `NotificationDropdown`)
-   **Action**: Update the existing `NotificationDropdown` React component.
-   **Logic**: It will now handle the new `'year_in_review'` notification type. When displaying this type, it will show a custom message (e.g., "🎉 Your [Year] Year in Review is Ready!") and ensure that clicking the notification navigates the user to `/journal/me?tab=stats&year=[year_to_notify]`.
-   **Status**: `[ ] Pending`

### 5.3 Validation (Postman & Browser)
-   **Your Task**:
    1.  Trigger the temporary backend endpoint (from 5.1) via Postman.
    2.  Log in as an eligible user on the frontend.
-   **Checkpoints**:
    *   Does the new "Year in Review" notification appear in the `NotificationDropdown`?
    *   Does clicking the notification correctly navigate to the stats page for the relevant year?
    *   Is the notification automatically marked as read after being clicked?
-   **Status**: `[ ] Pending`
