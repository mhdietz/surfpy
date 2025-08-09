# Frontend Authentication Plan

## 1. Overview

This document outlines the step-by-step plan for implementing the client-side authentication system for the Surf App frontend. The implementation will use JWT for authentication, React Context for global state management, and React Router for navigation and route protection.

## 2. Core Decisions

- **Logout:** Will be handled client-side by deleting the user's token from `localStorage`. No server call will be made.
- **Global State:** A `AuthContext` will be used to provide authentication status and user data to all components.
- **Signup Flow:** After a user successfully signs up, they will be automatically logged in and redirected to the main feed.
- **Route Protection:** A `<ProtectedRoute>` component will gate access to authenticated routes, redirecting unauthenticated users to the login page.

## 3. File Structure

The following files and directories will be created:

```
/frontend/src/
├── components/
│   └── ProtectedRoute.jsx      # Protects routes from unauthenticated access
├── pages/
│   └── Auth.jsx                # Contains Login and Signup forms
├── services/
│   ├── auth.js                 # Handles API calls and token management
│   └── api.js                  # Centralized API request handler (to be built out)
├── context/
│   └── AuthContext.jsx         # Global state for authentication
└── config/
    └── api.js                  # API base URL configuration
```

## 4. Implementation Steps

### Step 1: Scaffolding & Configuration

1.  **Create Directories:** Create the `pages`, `services`, `context`, and `config` directories inside `frontend/src`.
2.  **Create Files:** Create the empty files as laid out in the structure above.
3.  **Configure API URL:** In `frontend/src/config/api.js`, define and export the backend URL:
    ```javascript
    export const API_BASE_URL = 'http://localhost:5000';
    ```

### Step 2: Authentication Service (`services/auth.js`)

This service will be the single source of truth for interacting with the backend auth endpoints and managing the JWT.

-   **`login(email, password)`**:
    -   Sends a `POST` request to `/api/auth/login`.
    -   On success, saves the `access_token` to `localStorage`.
    -   Returns the user data from the response.
-   **`signup(email, password, firstName, lastName)`**:
    -   Sends a `POST` request to `/api/auth/signup`.
    -   On success, immediately calls `login(email, password)` to log the new user in.
-   **`logout()`**:
    -   Removes the `access_token` from `localStorage`.
-   **`getToken()`**:
    -   A helper function that retrieves the token from `localStorage`.

### Step 3: Global State (`context/AuthContext.jsx`)

This context will provide authentication state and functions to the entire application.

1.  **Create `AuthContext`**: Initialize a new React context.
2.  **Create `AuthProvider`**:
    -   This component will wrap the application.
    -   It will manage state for `user` and `isAuthenticated`.
    -   On initial load, it will check `localStorage` for a token. If a token exists, it will decode it to get user info and set `isAuthenticated` to `true`.
    -   It will provide the `login`, `signup`, and `logout` functions that call the `auth.js` service and update the context state.

### Step 4: UI Component (`pages/Auth.jsx`)

This component will render the login and signup forms.

1.  **Component State**: Use `useState` to manage form inputs and to toggle between the login and signup views.
2.  **Context Integration**: Use the `useContext(AuthContext)` hook to access the `login` and `signup` functions.
3.  **Redirection**: Use the `useNavigate` hook from `react-router-dom` to redirect the user to the `/feed` upon successful authentication.
4.  **Error Handling**: Display API error messages to the user (e.g., "Invalid credentials").

### Step 5: Protected Routes (`components/ProtectedRoute.jsx`)

This component will protect pages that require authentication.

1.  **Context Integration**: Use `useContext(AuthContext)` to check the `isAuthenticated` status.
2.  **Conditional Rendering**:
    -   If `isAuthenticated` is `true`, it will render its `children` props.
    -   If `isAuthenticated` is `false`, it will use the `<Navigate>` component from `react-router-dom` to redirect the user to `/auth/login`.

### Step 6: Main App & Routing (`App.jsx`)

This is where everything is tied together.

1.  **Wrap with Provider**: Wrap the entire application's component tree with the `<AuthProvider>`.
2.  **Define Routes**: Set up the application's routes using `react-router-dom`.
    -   **Public Route**: `/auth/login` will render the `<Auth />` component.
    -   **Protected Route**: `/feed` will be wrapped in the `<ProtectedRoute>` component.

    ```jsx
    <Routes>
      <Route path="/auth/login" element={<Auth />} />
      <Route path="/feed" element={
        <ProtectedRoute>
          <Feed />
        </ProtectedRoute>
      } />
      {/* ... other routes */}
    </Routes>
    ```
