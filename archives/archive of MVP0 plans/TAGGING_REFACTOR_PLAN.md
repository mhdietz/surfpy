# Session Tagging Refactor Plan

This document outlines the implementation plan to refactor the session tagging system. The goal is to move from a "duplicated session" model to a more efficient relational model where a single session record is associated with multiple participants.

## Guiding Principles

1.  **Single Source of Truth**: A surf session will be a single record in the database. The concept of creating duplicate sessions for each participant will be eliminated.
2.  **Relational Participants**: Tagged users will be associated with a session via a direct foreign key relationship in the `session_participants` table.
3.  **Creator-Centric Logic**: All edit/delete permissions and primary visibility will be based on the `user_id` of the session creator.
4.  **No Data Migration**: This refactor applies only to new sessions. Existing data and database schema will not be migrated or altered.

---

## Database Strategy: The `session_group_id` Column

-   **No Schema Change**: The database schema will **not** be altered. The `session_participants` table already exists and will be used as the primary source for participant data.
-   **Handling `session_group_id`**: The `session_group_id` column in the `surf_sessions_duplicate` table is now obsolete for new sessions. However, it will be left in the database to maintain the integrity of existing data. For all sessions created after this refactor, the `session_group_id` will be `NULL`.

---

## Implementation Tasks

### Part 1: Database Logic Simplification (`database_utils.py`)

This phase focuses on changing how session and participant data is written to the database.

-   **Task 1.1: Refactor `create_session_with_participants`**
    -   **File to Modify**: `database_utils.py`
    -   **Action**: The function will be rewritten to perform the following steps in a single transaction:
        1.  Remove the logic that generates a `session_group_id`.
        2.  Call the standard `create_session` function to insert a single record into `surf_sessions_duplicate` for the creator. The `session_group_id` will not be included.
        3.  Using the `id` returned from the newly created session, insert one row into the `session_participants` table for the creator.
        4.  Iterate through the `tagged_user_ids` array and insert one row into `session_participants` for each tagged user, linking them to the same session `id`.

-   **Task 1.2: Remove Redundant Code**
    -   **File to Modify**: `database_utils.py`
    -   **Action**: Delete the `create_duplicate_session` function, as it is no longer needed.
    -   **Action**: Remove any logic for manually calculating `next_id` within the participant creation flow.

### Part 2: API and Data Retrieval Adjustments

This phase ensures the API endpoints and data retrieval queries align with the new, simplified data structure.

-   **Task 2.1: Simplify `create_surf_session` Endpoint**
    -   **File to Modify**: `surfdata.py`
    -   **Action**: The JSON response for a successful session creation with participants will be simplified. It will now return the `session_id` of the single session created and a simple list of the user IDs that were successfully tagged.

-   **Task 2.2: Refactor Data Retrieval Queries**
    -   **File to Modify**: `database_utils.py`
    -   **Action**: The SQL queries within `get_all_sessions`, `get_user_sessions`, and `get_session` will be modified. The current complex self-join on `session_group_id` will be replaced with a more efficient `LEFT JOIN` on the `session_participants` table, grouping by the session ID to aggregate the list of participants.

---

## Summary of File Modifications

-   **MODIFIED**: `database_utils.py` (Core logic change, function removal, query updates)
-   **MODIFIED**: `surfdata.py` (Simplified API response)

---

## Success Criteria & Verification

The refactor will be considered successful when the following conditions are met:

1.  **Session Creation**: A `POST` request to `/api/surf-sessions` with a `tagged_users` array results in:
    -   Only **one** new row being created in the `surf_sessions_duplicate` table.
    -   The `session_participants` table containing a row for the creator and each tagged user, all linked to the single new session ID.

2.  **Session Retrieval**: A `GET` request to `/api/surf-sessions/<session_id>` for the newly created session returns a JSON object where:
    -   The `participants` array is correctly populated with the creator and all tagged users, based on the data in the `session_participants` table.

3.  **Application Stability**: The application runs without errors, and all other API endpoints function as expected.
