### Revised Journal Page Implementation Plan (Piecemeal)

This revised plan breaks down the Journal Page implementation into smaller, testable steps, allowing for incremental verification and quicker issue identification.

---

**Phase 1: Backend API Foundation (Re-establish & Verify)**
*   **Goal:** Ensure all necessary backend API endpoints are fully functional and accessible from the frontend, both locally and on Vercel.
*   **Piecemeal Steps:**

    1.  **Re-implement `get_user_profile_by_id` in `database_utils.py` (if reverted).**
        *   **Action:** Add or confirm the `get_user_profile_by_id` function in `database_utils.py`.
        *   **Test:** Run a Python interpreter or a local Flask shell and call `database_utils.get_user_profile_by_id('a_valid_user_id')`. Confirm it returns the expected user profile data.

    2.  **Re-implement `/api/users/<user_id>/profile` endpoint in `surfdata.py` with `GET` and `OPTIONS` methods.**
        *   **Action:** Add or confirm the `@app.route('/api/users/<string:user_id>/profile', methods=['GET', 'OPTIONS'])` decorator and its associated function in `surfdata.py`.
        *   **Test:**
            *   **Local:** Start your Flask backend (`python surfdata.py`). Use Postman (or `curl`) to send `GET` and `OPTIONS` requests to `http://localhost:5000/api/users/<your_user_id>/profile` (using a valid JWT in the `Authorization` header). Confirm both return `200 OK` and the `GET` request returns the correct profile data.
            *   **Vercel:** Deploy these changes to Vercel. Use Postman to send `GET` and `OPTIONS` requests to your Vercel backend URL (e.g., `https://your-backend.vercel.app/api/users/<your_user_id>/profile`). Confirm both return `200 OK` and the `GET` request returns the correct profile data.

    3.  **Re-implement global `OPTIONS` handler in `surfdata.py` (if reverted).**
        *   **Action:** Add or confirm the `@app.before_request` global `OPTIONS` handler in `surfdata.py`.
        *   **Test:**
            *   **Local:** Start your Flask backend. Use Postman to send an `OPTIONS` request to *any* endpoint (e.g., `http://localhost:5000/api/auth/login`). Confirm `200 OK`.
            *   **Vercel:** Deploy these changes to Vercel. Use Postman to send an `OPTIONS` request to *any* endpoint on your Vercel backend URL. Confirm `200 OK`.

    4.  **Re-implement `vercel.json` rewrite rules.**
        *   **Action:** Add or confirm the rewrite rules in `vercel.json` that prepend `/api/` to incoming requests (e.g., `src: "/(.*)", dest: "/api/$1"`).
        *   **Test:**
            *   **Vercel:** Deploy these changes to Vercel. Use Postman to send a `GET` request to `https://your-backend.vercel.app/users/<your_user_id>/profile` (note: *without* `/api/` in the URL). Confirm it returns `200 OK` and the correct profile data. This verifies the rewrite rule.

    5.  **Verify `get_user_journal_sessions` endpoint in `surfdata.py` (already exists).**
        *   **Action:** Confirm the `get_user_journal_sessions` endpoint is present and correctly calls `database_utils.get_user_sessions`.
        *   **Test:**
            *   **Local:** Start your Flask backend. Use Postman to send a `GET` request to `http://localhost:5000/api/users/<your_user_id>/sessions`. Confirm `200 OK` and that it returns sessions for the specified user.
            *   **Vercel:** Deploy these changes to Vercel. Use Postman to send a `GET` request to `https://your-backend.vercel.app/api/users/<your_user_id>/sessions`. Confirm `200 OK` and correct data.

---

**Phase 2: Frontend Journal Page - Basic Display**
*   **Goal:** Get the Journal page to display the user's name and a list of sessions.
*   **Piecemeal Steps:**

    1.  **Create `JournalPage.jsx` (basic structure).**
        *   **Action:** Create `frontend/src/pages/JournalPage.jsx` with the initial `useState`, `useEffect`, and basic JSX structure (as previously discussed, but without the `PageTabs` for now).
        *   **Test:** Run your frontend dev server (`npm run dev`). Navigate to `http://localhost:5173/journal/me` (or any valid user ID). Confirm the page loads with a placeholder title.

    2.  **Implement routing in `App.jsx` for `/journal/:userId` and redirect `/journal` to `/journal/me`.**
        *   **Action:** Modify `frontend/src/App.jsx` to include the route for `/journal/:userId` and the redirect from `/journal` to `/journal/me`.
        *   **Test:** Navigate to `http://localhost:5173/journal` (should redirect to `/journal/me`). Navigate to `http://localhost:5173/journal/some-valid-user-id`. Confirm correct routing.

    3.  **Fetch and display user's `display_name` in `JournalPage.jsx`.**
        *   **Action:** In `JournalPage.jsx`, implement the `useEffect` to call the `/users/:userId/profile` endpoint and update the `profileUser` state. Display `profileUser.display_name` in the `<h1>` tag.
        *   **Test:** Navigate to the Journal page. Confirm the correct user's display name appears at the top of the page. Check console for any errors.

    4.  **Fetch and display sessions using `SessionsList` in `JournalPage.jsx`.**
        *   **Action:** In `JournalPage.jsx`, implement the `useEffect` to call the `/users/:userId/sessions` endpoint and update the `sessions` state. Integrate the `SessionsList` component, passing `sessions`, `loading`, and `error` props.
        *   **Test:** Navigate to the Journal page. Confirm sessions load and display correctly. Verify loading and error states are handled.

---

**Phase 3: Frontend Journal Page - Filter UI**
*   **Goal:** Implement the minimalist filter toggle and its controls.
*   **Piecemeal Steps:**

    1.  **Create `JournalFilter.jsx` with toggle mechanism and static filter options.**
        *   **Action:** Create `frontend/src/components/JournalFilter.jsx` with the toggle logic and static dropdowns/inputs for region, swell height, period, and direction.
        *   **Test:** Verify the component renders correctly. Click the toggle button and confirm it expands/collapses.

    2.  **Integrate `JournalFilter.jsx` into `JournalPage.jsx`.**
        *   **Action:** Import and render `JournalFilter.jsx` in `JournalPage.jsx`.
        *   **Test:** Verify the filter component is visible on the Journal page.

---

**Phase 4: Frontend Journal Page - Filter Logic & API Integration**
*   **Goal:** Make the filters functional and update the URL.
*   **Piecemeal Steps:**

    1.  **Fetch regions and populate "Region" filter in `JournalFilter.jsx`.**
        *   **Action:** In `JournalFilter.jsx` (or `JournalPage.jsx` and pass down), fetch regions from `/api/regions` and populate the "Region" dropdown.
        *   **Test:** Verify the "Region" dropdown is populated with actual regions.

    2.  **Implement state management for filters in `JournalPage.jsx` and pass to `JournalFilter.jsx`.**
        *   **Action:** In `JournalPage.jsx`, manage filter state. Pass filter values and an `onFilterChange` handler to `JournalFilter.jsx`.
        *   **Test:** Interact with filter controls. Verify filter values can be selected/entered and their state is correctly managed in `JournalPage.jsx`.

    3.  **Modify session fetching to include filter parameters.**
        *   **Action:** Update the `useEffect` in `JournalPage.jsx` to include the current filter values as query parameters when calling the `/users/:userId/sessions` endpoint.
        *   **Test:** Apply various filters (e.g., min swell height, region). Verify that the displayed sessions change accordingly.

    4.  **Update URL with filter parameters.**
        *   **Action:** Use `react-router-dom`'s `useSearchParams` hook in `JournalPage.jsx` to reflect the active filters in the URL.
        *   **Test:** Apply filters. Verify the URL updates (e.g., `.../journal/me?min_swell_height=3&region=East%20Coast`). Refresh the page and confirm filters persist.