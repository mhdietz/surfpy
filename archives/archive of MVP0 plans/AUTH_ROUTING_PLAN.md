Part 1: Make the Auth State Smarter

  Goal: The AuthContext needs to know its own loading state. When the app first loads, it will perform a check to see if a 
  valid session already exists and only then will it declare the user as authenticated or unauthenticated.

   * [x ] Step 1.1: Add `isLoading` State
       * I will edit frontend/src/context/AuthContext.jsx to add a new state variable, isLoading, which will default to true.

   * [ x] Step 1.2: Implement Initial Authentication Check
       * I will add logic to the AuthContext that runs once when the app first loads.
       * This logic will look for an auth token in localStorage.
       * If a token is found, it will make a lightweight API call to a new endpoint (/api/users/me/profile) to validate the 
         token and get the current user's data.
       * Based on the result, it will either set the user as authenticated or clear the invalid token.
       * Finally, it will set isLoading to false.

   * [ x] Step 1.3: Expose `isLoading`
       * I will update the AuthContext provider to make the isLoading state available to the rest of the app.

  ---

  Part 2: Improve the Protected Route Guard

  Goal: The ProtectedRoute component, which guards pages that require a login, needs to wait for the AuthContext to finish 
  its initial check before deciding what to do.

   * [x ] Step 2.1: Read the `isLoading` State
       * I will edit frontend/src/components/ProtectedRoute.jsx.
       * It will now get the isLoading value from the useAuth() hook.

   * [ x] Step 2.2: Show a Spinner While Loading
       * I will add a check to the ProtectedRoute. If isLoading is true, the component will render a full-page loading 
         spinner instead of the page content.
       * Once isLoading is false, the component's existing logic will proceed, now with the certainty of the user's auth 
         status, and will correctly redirect to /auth/login if needed.

  ---

  Part 3: Handle Expired Sessions Globally

  Goal: If a user's session expires while they are actively using the app, any API call they make will fail. We need to 
  catch this specific failure globally and redirect them to the login page automatically.

   * [ ] Step 3.1: Update the `apiCall` Function
       * I will edit the central API function in frontend/src/services/api.js.
       * I will add logic to specifically check if the response status from the server is 401 Unauthorized.

   * [ ] Step 3.2: Implement Automatic Logout and Redirect
       * If a 401 error is detected, the function will automatically clear the user's token from localStorage and redirect 
         the browser to the /auth/login page. This prevents the user from ever getting stuck on an error screen due to an 
         expired token.