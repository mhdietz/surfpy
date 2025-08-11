### **Implementation Plan: Create Session Page (Revised)**

This plan outlines the steps to create a new, fully functional `CreateSessionPage.jsx` component. The original plan to use a modal for user search has been revised in favor of a more streamlined, inline search experience.

---

### **Phase 1: Page Scaffolding & Static Form Layout (Complete)**

**Goal:** Create the basic structure of the page and add the form UI.

*This phase is complete.*

---

### **Phase 2: Location Data Integration (Complete)**

**Goal:** Make the location dropdown dynamic by fetching and displaying real surf spots from the backend.

*This phase is complete.*

---

### **Revised Phase 3: Inline User Search & Tagging**

**Goal:** Replace the modal with a seamless, inline user search and tagging experience to improve UX and resolve a rendering bug.

1.  **Remove Modal Logic**: In `CreateSessionPage.jsx`, remove the `isUserSearchOpen` state, the "Search & Tag Friends" button, and the conditional rendering for the `<UserSearch />` component.
2.  **Add Inline Search UI**:
    *   Add a new `Input` field to the form with the label "Tag Surfers".
    *   Add new state variables to manage the search query text and the list of search results.
3.  **Implement Live Search**:
    *   As the user types into the new search input, a `useEffect` hook will trigger a debounced call to the `/api/users/search` endpoint.
    *   The returned user list will be stored in the search results state.
4.  **Display Results Dropdown**:
    *   A dropdown list will appear directly below the search input, showing the names of matching users.
    *   Each name in the list will be a clickable button.
5.  **Implement User Selection**:
    *   Clicking a user from the results list will add them to the `taggedUsers` array and clear the search input and results list.
    *   The selected users will be displayed as dismissible tags on the form.

---

### **Phase 4: Form Submission & Full API Integration**

**Goal:** Make the form fully functional by handling submission, sending the data to the backend, and managing the response.

1.  **Form State**: Ensure all form inputs are controlled components, with their values tied to `useState` variables.
2.  **Submit Handler**: Create an `async` function `handleSubmit` that is triggered by the "Save Session" button.
3.  **Construct Payload**: Inside `handleSubmit`, assemble the form data into a JSON object that matches the payload expected by the `POST /api/surf-sessions` endpoint. This includes the array of `tagged_users` IDs.
4.  **API Call**: Use the `apiCall` service to send the `POST` request.
5.  **Handle Response**:
    *   **On Success**: Use `react-hot-toast` to show a success message and redirect the user.
    *   **On Error**: Use `react-hot-toast` to display a user-friendly error message.

---

### **Phase 5: Final Polish & Validation**

**Goal:** Improve the user experience with loading indicators and basic client-side validation.

1.  **Loading States**: Add `Spinner` components for any asynchronous operations.
2.  **Client-Side Validation**: Add `required` attributes and other simple checks to prevent invalid form submission.