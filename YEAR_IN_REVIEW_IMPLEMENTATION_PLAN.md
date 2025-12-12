# Year in Review Feature - Implementation Plan

This document outlines the step-by-step implementation for the "Year in Review" feature, including testing and validation points.

## Phase 1: Backend API Development

The goal of this phase is to create a robust and correct API endpoint that provides all the necessary data for the "Year in Review" feature.

### 1.1 Create New Database Function (`database_utils.py`)
-   **Action**: Implement a new function, `get_user_stats_by_year(user_id, year)`.
-   **Logic**: This function will execute SQL queries to aggregate all the required statistics for the given user and year.
-   **Status**: `[x] Completed`

### 1.2 Enhance the API Endpoint (`surfdata.py`)
-   **Action**: Modify the existing `/api/users/<profile_user_id>/stats` endpoint.
-   **Logic**: The endpoint will now accept an optional `year` query parameter.
-   **Status**: `[x] Completed`

### 1.3 Validation (Postman)
-   **Your Task**: Run Postman requests against the local server to validate the backend endpoint.
-   **Checkpoints**:
    *   Response structure matches the specification.
    *   Calculations are correct for users with and without data for the selected year.
    *   Empty states (no sessions, no buddy) are handled gracefully.
-   **Status**: `[x] Completed`

## Phase 2: Frontend - Basic UI & Data Integration

This phase focuses on connecting the frontend to the new API endpoint and building the main structure of the page.

### 2.1 Update API Service (`frontend/src/services/api.js`)
-   **Action**: Update the function that fetches user stats to accept and pass a `year` parameter to the backend API.
-   **Status**: `[x] Completed`

### 2.2 Add State Management (My Stats Page Component)
-   **Action**: In the React component for the "My Stats" page (`frontend/src/pages/JournalPage.jsx` or relevant component), add state to manage the selected year.
-   **Logic**: Use `useEffect` to fetch stats from the API service when the component mounts or when the `selectedYear` state changes.
-   **Status**: `[x] Completed`

### 2.3 Implement Year Filter & Display Basic Stats
-   **Action**: Add the year filter buttons to the UI.
-   **Logic**: Set up `onClick` handlers to update the `selectedYear` state and update the display of the main stat cards.
-   **Status**: `[x] Completed`

### 2.4 Implement Empty State Display
-   **Action**: Add conditional logic to display the "You haven't logged any sessions..." message.
-   **Logic**: This message should appear when `total_sessions` for a given year is 0.
-   **Status**: `[x] Completed`

### 2.5 Validation (Browser)
-   **Your Task**: Navigate to your stats page (`/journal/me?tab=stats`) on your local frontend deployment.
-   **Checkpoints**:
    *   Are the new year filter buttons displayed and functional?
    *   Do the basic stats update correctly when the year is changed?
    *   Does the empty state message appear correctly for a year with no sessions?
-   **Status**: `[x] Completed`

## Phase 3: Frontend - Charts and Detailed Components

This phase builds the data visualizations and detailed lists.

### 3.1 Install Dependencies
-   **Action**: Install `recharts` and `html2canvas`.
-   **Command**: `npm install recharts html2canvas` in the `frontend` directory.
-   **Status**: `[x] Completed`

### 3.2 Create "Top Sessions" Component
-   **Action**: Implement a new React component to display the `top_sessions` array.
-   **Logic**: Each session entry should be clickable and link to its corresponding session detail page.
-   **Status**: `[x] Completed`

### 3.3 Create Chart Components
-   **Action**: Implement two new React components for the "Sessions by Month" and "Stoke by Month" charts using `recharts`.
-   **Status**: `[x] Completed`

### 3.4 Create "Most Frequent Buddy" Component
-   **Action**: Implement a component to display the `most_frequent_buddy` data, rendering it conditionally.
-   **Status**: `[x] Completed`

### 3.5 Validation (Browser)
-   **Your Task**: View the stats page for a user with sufficient data to populate all new components.
-   **Checkpoints**:
    *   Do all new components render correctly?
    *   Are the charts and links functional?
-   **Status**: `[x] Completed`

*Note: The complex "Most Frequent Buddy" logic, accounting for real-world events vs. database records and fuzzy time matching, has been deferred to a future implementation and is documented in `REFINING_THE_BUDDY_SCORE.md`.*

## Phase 4: Shareable Image Generation

This phase implements the social sharing feature.

### 4.1 Create Hidden Shareable Card Component
-   **Action**: Implement a new, off-screen React component styled to be the 1080x1080px shareable image.
-   **Status**: `[ ] Pending`

### 4.2 Implement Share Button & Logic
-   **Action**: Add the "Share" button to the UI.
-   **Logic**: On click, use `html2canvas` to capture the hidden component and trigger a PNG download.
-   **Status**: `[ ] Pending`

### 4.3 Validation (Browser)
-   **Your Task**: Click the "Share" button.
-   **Checkpoints**:
    *   Does a 1080x1080px PNG file download?
    *   Does the image content match the design specification?
-   **Status**: `[ ] Pending`

## Phase 5: Notification System (Revised)

This phase leverages the existing notification system to announce the feature.

### 5.1 Backend - Bulk Notification Generation (`database_utils.py`)
-   **Action**: Implement a new function, `create_year_in_review_notifications(year_to_notify)`.
-   **Logic**: This function will query for all eligible users and insert a `'year_in_review'` notification into the `notifications` table.
-   **Temporary Endpoint**: A temporary, secure endpoint will be added to `surfdata.py` to trigger this for testing.
-   **Cleanup Note**: After testing, you must manually delete these test notifications from the database.
-   **Status**: `[ ] Pending`

### 5.2 Frontend - Notification Display (Existing `NotificationDropdown`)
-   **Action**: Update the existing `NotificationDropdown` component to handle the `'year_in_review'` notification type.
-   **Status**: `[ ] Pending`

### 5.3 Validation (Postman & Browser)
-   **Your Task**: Trigger the test endpoint and log in as an eligible user.
-   **Checkpoints**:
    *   Does the notification appear correctly in the UI?
    *   Does it navigate to the correct page?
-   **Status**: `[ ] Pending`