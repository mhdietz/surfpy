# Session Editing Implementation Plan

This plan outlines the necessary changes across the frontend and backend to allow users to edit their logged surf sessions. Each step is designed to be a small, incremental, and reviewable change.

---

### Phase 1: Frontend - Scaffolding the Edit Page

*Goal: Create the basic files, routes, and navigation for the edit feature.*

- [x] **Step 1.1: Create `EditSessionPage.jsx` File**
    - **Action**: Create a new file at `frontend/src/pages/EditSessionPage.jsx` with basic placeholder content.
    - **Validation**: This is a file-system-only change. The running application in your browser should not crash. I will confirm the file has been created.

- [x] **Step 1.2: Add Edit Page Route**
    - **Action**: Add a new route `/session/:id/edit` to the main application router, pointing to the `EditSessionPage` component.
    - **Validation**: Manually navigate your browser to a URL like `http://localhost:5173/session/1/edit`. You should see the placeholder text from the previous step.

- [x] **Step 1.3: Add Temporary "Edit" Button**
    - **Action**: In `frontend/src/pages/SessionDetail.jsx`, add a temporary "Edit Session" button that is visible to all users.
    - **Validation**: Navigate to any session detail page. You should see the new "Edit Session" button. Clicking it should take you to the edit page.

- [x] **Step 1.4: Implement Conditional "Edit" Button**
    - **Action**: Modify the "Edit Session" button to only be visible if the logged-in user is the session creator.
    - **Validation**: Log in and navigate to a session you created; the button should be visible. Navigate to a session created by another user; the button should be hidden.

---

### Phase 2: Frontend - Building the Edit Form

*Goal: Populate the edit page with data and make it interactive.*

- [x] **Step 2.1: Copy `CreateSessionPage` as Template**
    - **Action**: Replace the placeholder content in `EditSessionPage.jsx` with the full content from `CreateSessionPage.jsx`.
    - **Validation**: Navigate to an edit page URL. You should see the full session creation form.

- [x] **Step 2.2: Update Static Text**
    - **Action**: Change static text in `EditSessionPage.jsx` from "Create" to "Edit" or "Update" (e.g., page title, submit button).
    - **Validation**: Navigate to an edit page. The title and button text should reflect that you are editing, not creating.

- [x] **Step 2.3: Fetch Session Data**
    - **Action**: Implement the `useEffect` hook in `EditSessionPage.jsx` to call the `GET /api/surf-sessions/:id` endpoint.
    - **Validation**: Open your browser's **Developer Tools -> Network** tab. When you load an edit page, you should see a successful `fetch` request for the session data.

- [x] **Step 2.4: Pre-populate Form Fields**
    - **Action**: Use the fetched data to set the state for the form fields.
    - **Validation**: Navigate to an edit page. The form fields (Date, Location, Notes, etc.) should be pre-filled with the correct data for that session. Use **React DevTools** to inspect the component's state.

- [x] **Step 2.4a: Fix Location Population**
    - **Action (Backend)**: Modify the `get_session_detail` function in `database_utils.py` to include the location's `slug` by joining with the `surf_spots` table.
    - **Action (Frontend)**: Update the `useEffect` hook in `EditSessionPage.jsx` to use the new `session.location_slug` field to set the state for the location dropdown.
    - **Validation**: Navigate to an edit page. The "Location" dropdown should now be correctly pre-populated with the session's location.

- [x] **Step 2.5: Pre-populate Tagged Surfers**
    - **Action**: Use the `participants` array from the fetched data to pre-populate the `taggedUsers` state.
    - **Validation**: Navigate to an edit page for a session with participants. The "Tag Surfers" section should already contain the tagged users.

---

### Phase 3: Backend - Implementing the Update Logic

*Goal: Create and enhance the backend endpoints to handle session updates securely.*

- [x] **Step 3.1: Enhance `update_session` Endpoint**
    - **Action**: In `surfdata.py`, enhance the `PUT /api/surf-sessions/:session_id` endpoint to include an ownership check and handle basic field updates (e.g., `session_name`, `notes`).
    - **Validation**: This is a backend-only change. The primary validation is that the API server continues to run without errors. Testing will occur in the next step.

- [x] **Step 3.2: Connect Frontend Form to Update Endpoint**
    - **Action**: Wire up the `handleSubmit` function in `EditSessionPage.jsx` to send a `PUT` request.
    - **Validation**: Edit a simple field like "Notes" on the page and save. The **Network** tab should show a successful `PUT` request, and upon redirection to the detail page, the notes should be updated.

- [x] **Step 3.4: Handle Data Re-fetching on Backend**
    - **Action**: Add logic to the backend to re-fetch oceanographic data if the date or location changes.
    - **Validation**: Edit a session's date or location. After saving, the swell, wind, and tide data visualizations on the detail page should change to reflect the new inputs.
