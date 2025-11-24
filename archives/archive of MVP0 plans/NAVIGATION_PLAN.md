# Navigation Component Development Plan

## 1. Objective

The `Navigation` component will provide the primary application shell, including a fixed top header and a fixed bottom navigation bar. Its purpose is to facilitate seamless routing between core application pages and provide access to user-specific actions like search and profile management.

## 2. Component Definition

-   **File Location**: `frontend/src/components/Navigation.jsx`
-   **Structure**: The component will consist of two main, fixed elements:
    -   A top header (e.g., for app title, search icon, profile dropdown).
    -   A bottom navigation bar (e.g., for main page links).
-   **Dependencies**: It will utilize `react-router-dom` for navigation (`Link`, `useNavigate`, `useLocation`) and the `AuthContext` for user authentication status.

## 3. Development Plan

-   **Step 1: Basic Structure (Header & Bottom Nav) (Completed)**:
    -   **Action**: Create the `Navigation.jsx` file.
    -   **Details**: Implement a fixed top header and a fixed bottom navigation bar with placeholder links.

-   **Step 2: Implement Navigation Links & Active State (Completed)**:
    -   **Action**: Connect the navigation placeholders to actual routes and add visual feedback for the active page.
    -   **Details**: Use `Link` components and `useLocation` for routing and active styling.

-   **Step 3: Header Functionality (User Search & Profile Dropdown) (Completed)**:
    -   **Action**: Add interactive elements to the header.
    -   **Details**: Include a user search icon placeholder and a conditional profile dropdown.

-   **Step 4: Integrate into `App.jsx` (Completed)**:
    -   **Action**: Render the `Navigation` component in the main application entry point.
    -   **Details**: Modify `frontend/src/App.jsx` to import and render the `Navigation` component.

-   **Step 5: Create Placeholder Pages & Update Routing (Completed)**:
    -   **Action**: Create new page components and update `App.jsx` to define their routes.
    -   **Details**: Placeholder pages for `CreateSessionPage.jsx` and `JournalPage.jsx` created, and `JournalPage.jsx` updated for tab toggling.

-   **Step 6: Implement Fixed Page Tabs (In Progress)**:
    -   **Step 6.1: Define Header Height & Main Content Padding (Completed)**:
        -   **Action**: Determine the height of the main `Navigation` header and adjust the top padding of the main content area in `App.jsx` to prevent content overlap.
        -   **Details**: The `Navigation` header is `p-4` (which is `1rem` or `16px`) and has a default height. We'll ensure the main content starts below it by adding `pt-16` (64px) to the main content wrapper in `App.jsx`.

    -   **Step 6.2: Create `PageTabs` Component (Completed)**:
        -   **Action**: Create a reusable `PageTabs.jsx` component.
        -   **File**: `frontend/src/components/PageTabs.jsx`
        -   **Details**: Accept `tabs`, `currentPath`, and `onTabClick` as props. Render a `fixed` container positioned `top-header-height` with `w-full`. Map over `tabs` to render `Link` components.

    -   **Step 6.3: Refactor `JournalPage.jsx` (Completed)**:
        -   **Action**: Integrate `PageTabs` into `JournalPage.jsx`.
        -   **Details**: Remove existing tab navigation buttons. Render `PageTabs` component. Adjust main content area of `JournalPage`.

    -   **Step 6.4: Refactor `Feed.jsx` (Completed)**:
        -   **Action**: Integrate `PageTabs` into `Feed.jsx`.
        -   **Details**: Remove existing conditional rendering. Render `PageTabs` component. Adjust main content area of `FeedPage`.

## 4. Testing

Initial testing will be manual by observing the component's behavior in the browser:
-   Verify that the header and bottom navigation bars are always visible and fixed in position.
-   Verify that clicking each navigation link correctly changes the URL and loads the corresponding page.
-   Verify that the active link styling works correctly.
-   Verify that the user search icon and profile dropdown placeholders are visible.
-   Verify that the profile dropdown conditionally renders based on authentication status.
-   Verify that the `ProtectedRoute` still functions correctly.
