# "Shaka" Reacts Feature Implementation Plan

This document outlines the implementation plan for adding a "shaka" reaction feature to surf sessions. It details the database schema that will be created manually and the backend logic that will be implemented to support the feature.

---

## Part 1: Database Schema (Manual Creation)

This section provides the required schema for the new `session_shakas` table. **This table will be created manually in the Supabase UI.** The backend logic will be written with the expectation that this exact schema is in place.

**Table Name:** `session_shakas`

**Columns:**

| Column Name  | Data Type     | Constraints & Default Value                                  | Notes                                                                                             |
| :----------- | :------------ | :----------------------------------------------------------- | :------------------------------------------------------------------------------------------------ |
| `session_id` | `int8`        | `NOT NULL`                                                   | This will be a Foreign Key referencing `surf_sessions_duplicate(id)`. Set `ON DELETE` to **Cascade**. |
| `user_id`    | `uuid`        | `NOT NULL`                                                   | This will be a Foreign Key referencing `auth.users(id)`. Set `ON DELETE` to **Cascade**.          |
| `created_at` | `timestamptz` | `NOT NULL`, Default: `now()`                                 | Records when the shaka was given.                                                                 |

**Primary Key:**

-   The primary key must be a **composite key** consisting of both the `session_id` and `user_id` columns. This is critical as it prevents a user from liking the same session more than once.

**Row Level Security (RLS):**

-   It is highly recommended that you **enable Row Level Security (RLS)** on this new table. You can start with permissive policies (e.g., allowing logged-in users to `INSERT` and `DELETE` their own shakas) and refine them later as needed.

---

## Part 2: Backend API Implementation

1.  **Create "Toggle Shaka" Endpoint:**
    -   **Endpoint:** `POST /api/surf-sessions/<int:session_id>/shaka`
    -   **Logic:** A new function will be created in `database_utils.py` to handle the "toggle" logic. It will attempt to `INSERT` a new shaka record. If the database returns a primary key violation error (because the record already exists), it will then `DELETE` the record instead.
    -   **Response:** The endpoint will return the new total shaka count for the session.

2.  **Update Data Retrieval Queries:**
    -   **File to Modify:** `database_utils.py`
    -   **Action:** The SQL queries in `get_all_sessions`, `get_user_sessions`, and `get_session` will be modified to include a subquery or a `LEFT JOIN` to accomplish the following for each session:
        a.  Calculates the total count of shakas (`shaka_count`).
        b.  Aggregates a JSON array of a preview of users who have given a shaka (`shakas_preview`).
        c.  Includes a boolean flag (`viewer_has_shakaed`) that is `true` if the `user_id` of the person making the request is in the list of shakas for that session.

---

## Part 3: API Response Structure

The JSON object for each session returned by the API will be enhanced to include a new `shakas` object, structured as follows:

```json
{
  "id": 123,
  "location": "Lido Beach",
  // ... other session data
  "shakas": {
    "count": 5,
    "viewer_has_shakaed": true,
    "preview": [
      { "user_id": "uuid-stefano", "display_name": "Stefano" },
      { "user_id": "uuid-friend1", "display_name": "Friend A" }
    ]
  }
}
```
