# Delete Session Functionality Plan

This document outlines the plan for implementing the "Delete Session" functionality in the Surf App.

## 1. Backend API Endpoint (`surfdata.py`)

*   **Status**: Already exists and is correctly implemented.
*   **Endpoint**: `DELETE /api/surf-sessions/<int:session_id>`
*   **Authorization**: Protected by `@token_required`, ensuring only authenticated users can access it.
*   **Ownership Check**: The `database_utils.delete_session` function securely verifies that the `user_id` from the JWT token matches the `user_id` of the session creator, preventing unauthorized deletions.
*   **Related Data Deletion**: The database schema has `ON DELETE CASCADE` rules configured for foreign keys in `session_participants` and `session_shakas` tables referencing `surf_sessions_duplicate`. This means that when a session is deleted from `surf_sessions_duplicate`, all associated participant and shaka records are automatically deleted by the database.
*   **Action**: No changes are needed for this backend endpoint or its associated database function.

## 2. Frontend Implementation (`SessionDetail.jsx` and `services/api.js`)

*   **Goal**: Provide a user interface to trigger the session deletion and handle the process.

*   **Piecemeal Steps**:

    1.  **Add Dummy "Delete Session" Button (Visual Only)**:
        *   **Location**: Insert a simple `<button>` element with the text "Delete Session" at the bottom of the `SessionDetail.jsx` page, inside the main `div` of the `Card` component.
        *   **Functionality**: This button will not have any `onClick` handler or associated logic.
        *   **Visibility**: The button will be visible to all users viewing any session for this step.
        *   **Styling**: Apply basic Tailwind CSS classes to make it look like a button (e.g., `w-full`, `bg-red-600`, `hover:bg-red-700`, `text-white`, `font-bold`, `py-2`, `px-4`, `rounded-lg`, `focus:outline-none`, `focus:shadow-outline`, `transition`, `duration-150`, `ease-in-out`, `mt-6`).
        *   **Imports**: Do not add any new import statements in this step.

    2.  **Add API Service Function (`deleteSession`)**:
        *   Create a new asynchronous function named `deleteSession` in `frontend/src/services/api.js`.
        *   This function will use `apiCall` to make a `DELETE` request to the backend endpoint (`/api/surf-sessions/<session_id>`). It will take the `session_id` as an argument.

    3.  **Add Frontend Imports and `handleDeleteSession` Function**:
        *   In `SessionDetail.jsx`, add the necessary `import` statements for `useNavigate` from `react-router-dom`, `toast` from `react-hot-toast`, and `deleteSession` from `../services/api`.
        *   Also, update the `useAuth` import to destructure `user` (e.g., `const { isAuthenticated, user } = useAuth();`).
        *   Implement the `handleDeleteSession` function. This function will:
            *   Prompt the user for confirmation using `window.confirm()`.
            *   If confirmed, call `deleteSession(id)`.
            *   Use `toast.promise` for loading, success, and error messages.
            *   On success, redirect the user to `/journal`.

    4.  **Connect Button and Implement Conditional Visibility**:
        *   Modify the dummy button in `SessionDetail.jsx` to include an `onClick` handler that calls `handleDeleteSession`.
        *   Implement conditional rendering for the button: it must only be visible if the logged-in user (`user.id`) matches the session creator's ID (`session.user_id`).

    5.  **User Feedback and Redirection (Refinement)**:
        *   Ensure `toast.promise` provides clear loading, success, and error messages.
        *   Confirm redirection to `/journal` after successful deletion.