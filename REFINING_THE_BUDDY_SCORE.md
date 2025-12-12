# Plan: Refining the "Most Frequent Buddy" Logic

This document outlines the challenges and a proposed future solution for creating a more accurate and intuitive "Most Frequent Buddy" statistic for the Year in Review feature.

## The Goal

The "Most Frequent Buddy" calculation should be symmetrical and reflect real-world events. If I surf with someone 5 times, they should also see that they surfed with me 5 times, regardless of who created the session log. The calculation should count unique, real-world surf sessions, not just individual database records.

## The Core Challenges

Based on our analysis, there are two primary challenges to achieving this goal with the current system:

### 1. The "Snaked Session" Problem
A single real-world surf session can exist as multiple records in the database.

*   **Scenario**: Frank logs a session and tags Stefano. Stefano then "snakes" that session.
*   **Result**: Two separate session records now exist in the database for the same real-world event.
*   **Impact**: A simple query would incorrectly count this as two sessions surfed together, leading to inflated buddy scores.

### 2. The "Fuzzy Time" Problem
Participants in the same real-world session might log their sessions with slightly different start and end times.

*   **Scenario**: Frank logs his session from 9:00 AM - 11:00 AM. Stefano, who surfed with him, logs his from 9:15 AM - 10:45 AM.
*   **Result**: Even though they surfed together, their session records have different timestamps.
*   **Impact**: We cannot reliably group these sessions together automatically by looking for records with the exact same location and start time.

### Analysis of `session_group_id`
The existing `session_group_id` field initially seemed like a potential solution. However, investigation revealed it is a remnant of a deprecated system. Currently, it is not used to link original and "snaked" sessions, with each record receiving a new, unique ID. Therefore, it cannot be used in its current state to solve this problem.

## Proposed Future Solution: A Hybrid Approach

To properly solve this, we need a robust way to link session records that belong to the same real-world event. The ideal solution involves a combination of backend refactoring and a new user-facing feature.

### Step 1: Repurpose `session_group_id`
The backend logic should be updated to use `session_group_id` as the definitive link for a single real-world event.

*   **On Session Creation**: When a user creates a brand new session, it should be assigned a new, unique `session_group_id`.
*   **On Session "Snake"**: When a session is "snaked," the newly created copy **must inherit the exact same `session_group_id`** from the original session record. This explicitly links the two records to the same event.

### Step 2: Implement a "Merge Sessions" Feature
To solve the "Fuzzy Time" problem, we can empower users to link sessions manually.

*   **UI/UX**: In the main feed, if the system detects two sessions from different users at the same location around the same time, it could display a "Did you surf together?" prompt.
*   **Functionality**: A user could select multiple session cards in their feed (e.g., their 9:00 AM session and their buddy's 9:15 AM session) and click a "Merge" or "Link Sessions" button.
*   **Backend Action**: This action would trigger an API call that assigns the same `session_group_id` to all the selected session records, effectively grouping them as a single real-world event.

### Step 3: Update the "Most Frequent Buddy" Query
Once a reliable `session_group_id` is in place, the SQL query for the buddy calculation becomes both simple and accurate.

*   **New Logic**:
    1.  Find all `session_group_id`s that the user participated in during the target year.
    2.  For each unique `session_group_id`, get a list of all unique participants.
    3.  Count the occurrences of each buddy across these groups.
    4.  The user with the highest count is the "Most Frequent Buddy."

This new query correctly counts the single event from the "Snaked Session" problem as one, and the "Merge Sessions" feature provides a path to resolve the "Fuzzy Time" problem.

## Summary

This plan provides a robust, long-term solution for delivering an accurate buddy score. It requires significant backend work (refactoring the use of `session_group_id`) and a new frontend feature ("Merge Sessions"). Due to this complexity, it is documented here for future implementation.
