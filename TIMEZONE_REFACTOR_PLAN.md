# Timezone Handling Refactoring Plan

This document outlines the plan to refactor the application's timezone handling to ensure consistency, eliminate ambiguity, and align with modern API best practices.

## 1. The Goal: Standardization and Unambiguity

The primary goal is to standardize how time-based data is stored, processed, and returned. All session-related timestamps will be handled as absolute points in time, normalized to UTC.

-   **Storage:** All timestamps will be stored in the database in `TIMESTAMP WITH TIME ZONE` columns, which PostgreSQL stores as UTC.
-   **Processing:** All backend logic will operate on UTC timestamps.
-   **API Response:** All API endpoints will return timestamps in the ISO 8601 format with the UTC "Z" designator (e.g., `2025-08-07T00:00:00Z`).

## 2. The Problem

Currently, session times are stored as naive `date` and `time` columns, which is ambiguous. While the backend correctly converts these to UTC for data fetching, the stored values and API responses are inconsistent. This plan will fix that.

## 3. The Refactoring Plan

### Step 1: Refactor the Database Schema

The `surf_sessions_duplicate` table will be modified to store session times unambiguously.

-   **Action:**
    1.  Add two new columns:
        -   `session_started_at` (type: `TIMESTAMP WITH TIME ZONE`)
        -   `session_ended_at` (type: `TIMESTAMP WITH TIME ZONE`)
    2.  Create a migration script to populate these new columns based on the existing `date` and `time` values and the timezone of the corresponding surf spot.
    3.  Remove the old, naive columns: `date`, `time`, and `end_time`.

### Step 2: Update the Backend Logic

The Flask API will be updated to work with the new schema.

-   **On `CREATE` and `UPDATE` (`/api/surf-sessions`):**
    -   The logic will continue to accept the user's naive `date`, `time`, and `end_time` from the request body for backward compatibility.
    -   It will use the `spot_config['timezone']` to convert these inputs into timezone-aware `datetime` objects.
    -   It will save these `datetime` objects into the new `session_started_at` and `session_ended_at` columns.

-   **On `GET` (All session retrieval endpoints):**
    -   In `database_utils.py`, when preparing session data for the response, explicitly format **all** timestamp fields (`session_started_at`, `session_ended_at`, `created_at`, and `next_tide_event_at`) into full ISO 8601 UTC strings.
    -   Ensure the surf spot's `timezone` string (e.g., "America/New_York") is included in the session's JSON response so the client can correctly display the time in the spot's local timezone.

## 4. Expected Outcome

After this refactoring, every time-related field returned by the API for a surf session will be a full, unambiguous UTC timestamp. This will give the frontend maximum flexibility for display and make the entire system more robust and maintainable.
