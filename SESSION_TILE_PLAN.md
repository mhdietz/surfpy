# SessionTile Component Development Plan

This document outlines the plan for creating, styling, and testing the `SessionTile` component, which is the first step in building the Core Component Library (Phase 2).

## 1. Objective

The `SessionTile` is a reusable, mobile-first component that provides a high-level summary of a single surf session. It will be the primary building block for all session lists, including the main feed and user journals. It must be clickable for navigation and allow for social interactions (giving a "shaka").

## 2. Component Definition

-   **File Location**: `frontend/src/components/SessionTile.jsx`
-   **Props**: The component will accept a single prop, `session`, which is an object containing all necessary data.

```javascript
// Expected structure for the 'session' prop
{
  id: 123, // Session ID
  session_name: "Fun morning waves",
  location: "Ocean Beach",
  fun_rating: 5,
  session_started_at: "2025-08-15T10:00:00Z",
  user_id: "uuid-for-user-1",
  display_name: "John Doe",
  participants: [
    { user_id: "uuid-for-user-2", display_name: "Jane Smith" }
  ],
  shakas: {
    count: 5,
    viewer_has_shakaed: false,
    preview: [
        { user_id: "uuid-for-user-3", display_name: "Sam Jones" }
    ]
  }
}
```

## 3. Development and Testing Strategy

### Step 1: Create Mock Data

-   **Action**: Create a new file: `frontend/src/utils/mockData.js`.
-   **Content**: Add a `mockSession` object to this file with the structure defined above. This will allow for isolated component development without needing to run the backend.

### Step 2: Initial Component Build (Static)

-   **Action**: Create the file `frontend/src/components/SessionTile.jsx`.
-   **Details**:
    -   Build the static JSX structure for the tile.
    -   Use the `Card` component from `components/UI/Card.jsx` as the base container.
    -   Style the component with Tailwind CSS, ensuring it is mobile-first and responsive.
    -   Use the `mockSession` data to populate the fields for previewing.

### Step 3: Visual Development & Preview

-   **Action**: Temporarily import and render the `SessionTile` component in `frontend/src/pages/Feed.jsx`.
-   **Details**:
    -   Pass the `mockSession` object as the `session` prop.
    -   This will allow for live visual feedback during the styling process using the Vite dev server.
    -   **Note**: This is a temporary measure and will be removed once the component is complete.

### Step 4: Implement Interactivity & Logic

-   **Action**: Add event handlers and navigation logic to `SessionTile.jsx`.
-   **Details**:
    -   Make the entire tile clickable to navigate to `/session/:id` using the `useNavigate` hook from `react-router-dom`.
    -   Make the creator's `display_name` a clickable link that navigates to their journal at `/journal/:userId`.
    -   Implement the `onClick` handler for the "shaka" button. This will initially just log to the console.

### Step 5: API Integration for Shaka Toggle

-   **Action**: Connect the shaka button to the backend.
-   **Details**:
    -   Create a new service file `frontend/src/services/sessions.js` if it doesn't exist.
    -   Add a `toggleShaka(sessionId)` function that makes a `POST` request to `/api/surf-sessions/<session_id>/shaka` using the centralized `apiCall` function.
    -   Update the `SessionTile` to use this service. Implement optimistic UI updates for the shaka count and button state.

### Step 6: Testing

-   **Action**: Create the test file `frontend/src/components/SessionTile.test.jsx`.
-   **Test Cases**:
    1.  **Renders Correctly**: Test that the component renders all data from the `mockSession` prop correctly (e.g., location, fun rating, user name).
    2.  **Navigation**: Simulate a click on the main tile and assert that the `useNavigate` hook is called with the correct path (`/session/123`).
    3.  **Shaka Interaction**: Simulate a click on the shaka button and assert that the `toggleShaka` API service function is called.
    4.  **Conditional Styling**: Test that the shaka button has a different style or class when `viewer_has_shakaed` is `true` vs. `false`.

### Step 7: Cleanup

-   **Action**: Remove the temporary `SessionTile` instance and `mockData` import from `frontend/src/pages/Feed.jsx`.

## 4. Progress

-   [x] **Step 1: Create Mock Data**
-   [x] **Step 2: Initial Component Build (Static)**
-   [x] **Step 3: Visual Development & Preview**
-   [ ] **Step 4: Implement Interactivity & Logic**
-   [ ] **Step 5: API Integration for Shaka Toggle**
-   [ ] **Step 6: Testing**
-   [ ] **Step 7: Cleanup**
