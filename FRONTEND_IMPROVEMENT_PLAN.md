# Frontend Improvement Plan

This document outlines the prioritized plan for addressing the identified frontend improvements and bugs. The goal is to work efficiently through the list, minimizing conflicts and ensuring a stable codebase.

## Prioritization Strategy

1.  **Textual/Display Changes (Low Risk, Quick Wins):** Focus on changes that primarily involve modifying text strings or simple display logic within a single component.
2.  **Component-Specific Logic (Contained Changes):** Address issues that are confined to a single component's functionality.
3.  **Global/Routing Changes (Inter-Component Impact):** Tackle changes that affect navigation or global text across multiple components. These are best done after component-specific changes are stable.
4.  **Debugging/Investigation (Higher Uncertainty):** Address issues that require more in-depth investigation and potential refactoring.

## Plan of Action

### Phase 1: Textual & Display Adjustments

*   **#7: Fun rating out of 10 (SessionTile.jsx)** - **COMPLETE**
    *   **Description:** Changed the display of the fun rating from `X / 5` to `X / 10`.
    *   **Affected File:** `frontend/src/components/SessionTile.jsx`
    *   **Granular Actions:**
        1.  Located the `<span>` element displaying `fun_rating} / 5`.
        2.  Changed `5` to `10` in the displayed text.
    *   **Test/Validation:**
        1.  Navigated to a session detail page or a list of sessions (Feed or Journal).
        2.  Verified that the "Fun Rating" now displays as "X / 10" for all session tiles.

*   **#2: Change "Martin's log" to "Your log" when viewing own journal (JournalPage.jsx)** - **COMPLETE**
    *   **Description:** The previous dynamic display of "[User's Name]'s Log" or "[User's Name]'s Stats" in the main title has been removed. The title now defaults to "Journal" or "Stats" based on the active tab.
    *   **Affected File:** `frontend/src/pages/JournalPage.jsx`
    *   **Granular Actions:**
        1.  The conditional rendering for the main `<h1>` title was modified to remove the dynamic display of the user's name.
    *   **Test/Validation:**
        1.  Log in as a user.
        2.  Navigate to your own journal (`/journal/me`).
        3.  Verify that the page title now simply says "Journal" or "Stats" (depending on the tab) and no longer includes the user's name.
        4.  Navigate to another user's journal.
        5.  Verify that the page title also simply says "Journal" or "Stats" and no longer includes the other user's name.

*   **#5: Change "my journal" to "surf log" throughout (JournalPage.jsx, Navigation.jsx)** - **COMPLETE**
    *   **Description:** Replaced all instances of "Journal" or "My Journal" with "Surf Log".
    *   **Affected Files:** `frontend/src/pages/JournalPage.jsx`, `frontend/src/components/Navigation.jsx` (and potentially other minor references).
    *   **Granular Actions:**
        1.  In `JournalPage.jsx`, replaced "Journal" with "Surf Log" in the `journalTabs` array and the main `<h1>` title.
        2.  In `Navigation.jsx`, replaced "Journal" with "Surf Log" in the bottom navigation link.
    *   **Test/Validation:**
        1.  Navigated to your own journal (`/journal/me`).
        2.  Verified that the page title and tab labels now say "Surf Log" (e.g., "Your Surf Log", "Your Stats").
        3.  Checked the bottom navigation bar and confirmed the "Journal" link now says "Surf Log".

*   **#27: Dynamic Empty State Message** - **COMPLETE**
    *   **Description:** The empty state message in the session list should be dynamic. It will show one message if the user is viewing their own empty journal and a different message if they are viewing another user's empty journal.
    *   **Affected Files:** `frontend/src/pages/JournalPage.jsx`, `frontend/src/components/SessionsList.jsx`
    *   **Granular Actions:**
        1.  **In `JournalPage.jsx`:**
            *   **Action 1.1:** Calculate a boolean `isOwnJournal`. Pass `isOwnJournal` and the `profileUser` object as props to the `SessionsList` component.
            *   **Test/Validation 1.1:** Use `console.log` or React DevTools to verify that `isOwnJournal` and `profileUser` are correctly passed to `SessionsList`.
        2.  **In `SessionsList.jsx`:**
            *   **Action 2.1:** Update the component to receive the new `isOwnJournal` and `profileUser` props.
            *   **Test/Validation 2.1:** Use `console.log` or React DevTools to verify the props are received correctly.
            *   **Action 2.2:** Implement conditional rendering for the empty state message.
                *   If `isOwnJournal` is `true`, display: "You're dry mate" and "get your ass in the water".
                *   If `isOwnJournal` is `false`, display: `${profileUser.display_name}'s dry` and "get that ass in the water".
            *   **Test/Validation 2.2:**
                *   Log in as a user with no sessions and navigate to your journal. Verify the "You're dry..." message appears.
                *   Find another user with no sessions and navigate to their journal. Verify the "[User's Name]'s dry..." message appears.

*   **#New1: Reduce extra space between tabs and content (JournalPage.jsx, Feed.jsx)** - **COMPLETE**
    *   **Description:** The vertical gap between `PageTabs` and the content (`SessionsList` or `StatsDisplay`) is too large in both Journal and Feed pages.
    *   **Affected Files:** `frontend/src/pages/JournalPage.jsx`, `frontend/src/pages/Feed.jsx`
    *   **Granular Actions:**
        1.  **JournalPage.jsx:** Remove `space-y-6` from the `main` element.
        2.  **Feed.jsx:** Remove `space-y-6` from the `main` element.
    *   **Test/Validation:**
        1.  Navigate to the Journal page. Verify the gap between tabs and content is reduced/removed. Check overall layout.
        2.  Navigate to the Feed page. Verify the gap between tabs and content is reduced/removed. Check overall layout.

*   **#New2: Shorten user's name in other users' surf logs/stats (JournalPage.jsx)** - **ON HOLD**
    *   **Description:** When viewing another user's journal, the full display name (e.g., "Stefano Scotti's Surf Log") takes up too much space. It should be shortened to just the first name (e.g., "Stefano's Surf Log").
    *   **Affected File:** `frontend/src/pages/JournalPage.jsx`
    *   **Granular Actions:**
        1.  Locate the line where `journalOwnerPrefix` is set to `${profileUser.display_name}'s`.
        2.  Change it to use `profileUser.first_name` instead.
    *   **Test/Validation:**
        1.  Log in.
        2.  Navigate to another user's journal (e.g., `/journal/<some_other_user_id>`).
        3.  Verify that the tab labels now display the other user's first name (e.g., "Stefano's Surf Log", "Stefano's Stats").

### Phase 2: Navigation & Global Functionality

*   **#3: Logo clicks go to home (Navigation.jsx)** - **COMPLETE**
    *   **Description:** Make the "Surf App" logo in the header clickable and link it to the home page.
    *   **Affected File:** `frontend/src/components/Navigation.jsx`
    *   **Granular Actions:**
        1.  In `Navigation.jsx`, locate the `<h1>Surf App</h1>` element within the header.
        2.  Wrap this `<h1>` element with a `Link` component, setting its `to` prop to `/feed` (or `/journal/me` if #6 is implemented first).
    *   **Test/Validation:**
        1.  Click on the "Surf App" logo in the top left corner.
        2.  Verify that you are navigated to the specified home page (`/feed` or `/journal/me`).

*   **#6: Default routing to "my Journal" (Auth.jsx, Routing)** - **COMPLETE**
    *   **Description:** After successful login or session creation, redirect the user to their own journal (`/journal/me`).
    *   **Affected Files:** `frontend/src/pages/Auth.jsx` (for login/signup success), `frontend/src/pages/CreateSessionPage.jsx` (for session creation success).
    *   **Granular Actions:**
        1.  In `Auth.jsx` (for login success), change `navigate('/feed')` to `navigate('/journal/me')`.
        2.  In `Auth.jsx` (for signup success), change `navigate('/feed')` to `navigate('/journal/me')`.
        3.  In `CreateSessionPage.jsx` (for session creation success), modify the `navigate` call to redirect to `/journal/me`.
    *   **Test/Validation:**
        1.  Log out.
        2.  Log in with an existing user. Verify you are redirected to your journal.
        3.  Sign up as a new user. Verify you are redirected to your journal.
        4.  Create a new session. Verify you are redirected to your journal.

### Phase 3: Debugging & Refinement

*   **#28: Fix leaderboard stats issues (Feed.jsx, Leaderboard.jsx)**
    *   **Description:** Debug and resolve any issues with the statistics displayed in the `Leaderboard` component.
    *   **Affected Files:** `frontend/src/pages/Feed.jsx` (as it renders `Leaderboard`), `frontend/src/components/Leaderboard.jsx` (the primary component to investigate).
    *   **Granular Actions:**
        1.  Inspect network requests for the leaderboard data when the "Leaderboard" tab is active in `Feed.jsx`.
        2.  Examine the `Leaderboard.jsx` component's `useEffect` hook for data fetching and state management.
        3.  Check the rendering logic in `Leaderboard.jsx` to ensure data is correctly displayed.
        4.  Identify and fix any discrepancies between expected and actual data/display.
    *   **Test/Validation:**
        1.  Navigate to the Feed page and select the "Leaderboard" tab.
        2.  Verify that the leaderboard data loads correctly and is displayed as expected (e.g., correct user names, stats, sorting).
        3.  Test filtering by year and statistic if applicable within the `Leaderboard` component.

## Workflow

1.  **Confirm Plan:** User reviews and confirms this plan.
2.  **Execute Task by Task:** I will work through the tasks in the order outlined above, one granular action at a time.
3.  **Verify Each Granular Change:** After each granular action, I will describe the change and the user will perform the specified test/validation.
4.  **User Confirmation:** I will await user confirmation before proceeding to the next granular action or task.
