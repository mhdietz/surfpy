### **Implementation Plan: Create Session Page**

This plan outlines the steps to create a new, fully functional `CreateSessionPage.jsx` component that integrates with the backend to log new surf sessions.

---

### **Phase 1: Page Scaffolding & Static Form Layout**

**Goal:** Create the basic structure of the page and add the form UI. This will make the page visible and routable in the app immediately.

1.  **Create New File**: Create `frontend/src/pages/CreateSessionPage.jsx`.
2.  **Add Route**: In your main router file (likely `App.jsx` or a dedicated router config), add a new protected route for `/create-session` that renders `CreateSessionPage`. The existing bottom navigation should now link to this page correctly.
3.  **Build Static UI**:
    *   Inside `CreateSessionPage.jsx`, lay out the main form structure.
    *   Use the reusable `Input`, `Button`, and `Card` components from `frontend/src/components/UI/` to create fields for:
        *   Date (type="date")
        *   Location (placeholder `<select>` dropdown)
        *   Title (text input)
        *   Start Time (type="time")
        *   End Time (type="time")
        *   Fun Rating (e.g., a number input or a simple select 1-5)
        *   Notes (textarea)
        *   A placeholder button for "Tag Surfers".
    *   Add a "Save Session" button.

**Outcome:** You will be able to navigate to a `/create-session` page and see the complete, un-styled form layout.

---

### **Phase 2: Location Data Integration**

**Goal:** Make the location dropdown dynamic by fetching and displaying real surf spots from the backend.

1.  **State Management**: In `CreateSessionPage.jsx`, use `useState` to manage the list of locations and the selected location.
2.  **API Call**: Use a `useEffect` hook to call the `GET /api/surf-spots-by-region` endpoint when the component mounts. Use the centralized `apiCall` service for this.
3.  **Populate Dropdown**:
    *   Render the fetched data in the `<select>` element.
    *   Use `<optgroup>` to group the spots by their `region`.
    *   For each `<option>`, set its `value` to the spot's `slug` and display the spot's `name`. This is critical for the backend.

**Outcome:** The location dropdown will be populated with correctly grouped surf spots, and selecting one will update the component's state.

---

### **Phase 3: User Search & Tagging**

**Goal:** Integrate the user search functionality to allow tagging other surfers in the session.

1.  **State Management**: Create a `useState` variable (e.g., `taggedUsers`) to hold an array of selected user objects.
2.  **Integrate `UserSearch` Component**:
    *   The "Tag Surfers" button should open the `UserSearch.jsx` modal.
    *   Pass a callback function to the `UserSearch` component that adds a selected user to the `taggedUsers` array.
3.  **Display Tagged Users**: Render the `display_name` of each user in the `taggedUsers` array below the "Tag Surfers" button. Add a small "x" button next to each name to allow for their removal from the array.

**Outcome:** You will be able to click "Tag Surfers," search for users by name, add them to the session, and see them listed on the form.

---

### **Phase 4: Form Submission & Full API Integration**

**Goal:** Make the form fully functional by handling submission, sending the data to the backend, and managing the response.

1.  **Form State**: Ensure all form inputs are controlled components, with their values tied to `useState` variables.
2.  **Submit Handler**: Create an `async` function `handleSubmit` that is triggered by the "Save Session" button.
3.  **Construct Payload**: Inside `handleSubmit`, assemble the form data into a JSON object that matches the payload expected by the `POST /api/surf-sessions` endpoint.
    *   `date`: `YYYY-MM-DD` string.
    *   `time`: `HH:MM` string.
    *   `end_time`: `HH:MM` string.
    *   `location`: The selected location `slug` (not the name).
    *   `session_name`: The title string.
    *   `fun_rating`: The rating number.
    *   `session_notes`: The notes string.
    *   `tagged_users`: An array of user **IDs** (e.g., `['uuid-1', 'uuid-2']`), extracted from your `taggedUsers` state array.
4.  **API Call**: Use the `apiCall` service to send the `POST` request.
5.  **Handle Response**:
    *   **On Success**: Use `react-hot-toast` to show a success message. Redirect the user to their journal (`/journal`) or the new session's detail page. The API response should contain the new session's ID, which you'll need for the redirect (`/session/<new_id>`).
    *   **On Error**: Use `react-hot-toast` to display a user-friendly error message from the API response.

**Outcome:** The form will be fully operational. You can fill it out, tag users, and successfully create a new session that is saved to the database.

---

### **Phase 5: Final Polish & Validation**

**Goal:** Improve the user experience with loading indicators and basic client-side validation.

1.  **Loading States**:
    *   Display a `Spinner` while the locations are being fetched.
    *   Disable the "Save Session" button and show a spinner or "Saving..." text while the form is submitting.
2.  **Client-Side Validation**:
    *   Add `required` attributes to essential form fields.
    *   Implement a check to ensure `end_time` is after `start_time`.
    *   Provide clear error messages if validation fails before submitting.

**Outcome:** The page will feel robust, providing clear feedback to the user during asynchronous operations and preventing invalid data submission.
