# MVP_1 Engineering Requirements: Comments System - Implementation Plan

## Background
Enable users to comment on surf sessions, creating richer social engagement. Comments should be lightweight, easy to use, and follow existing interaction patterns.

## API Endpoint Requirements

### 1. Get Comments for Session
- **Endpoint**: `GET /api/sessions/{session_id}/comments`
- **Use Case**: Load all comments when user opens comment modal
- **Response Structure**:
  ```json
  {
    "comments": [
      {
        "comment_id": 1,
        "session_id": 123,
        "user_id": "abc-123",
        "display_name": "Frank Kapp",
        "comment_text": "Sick session! What board were you riding?",
        "created_at": "2025-12-01T10:30:00Z"
      }
    ],
    "count": 1
  }
  ```

### 2. Create Comment
- **Endpoint**: `POST /api/sessions/{session_id}/comments`
- **Use Case**: User submits a new comment
- **Request Body**:
  ```json
  {
    "comment_text": "Epic waves today!"
  }
  ```
- **Response Structure**:
  ```json
  {
    "comment_id": 2,
    "session_id": 123,
    "user_id": "def-456",
    "display_name": "Stefano Scotti",
    "comment_text": "Epic waves today!",
    "created_at": "2025-12-01T11:00:00Z"
  }
  ```

### 3. Update Session Tiles Endpoint
- **Modification**: Add `comment_count` to lightweight session views.
- **Affected Endpoints**:
    - `GET /api/surf-sessions?view=feed`
    - `GET /api/users/{user_id}/sessions?view=profile`
    - `GET /api/surf-sessions/{id}` (detail view)
- **Added Response Field**:
  ```json
  {
    "session_id": 123,
    "comment_count": 5,
    // ... existing fields
  }
  ```

## Database Schema Changes

### New Table: `comments`
```sql
CREATE TABLE comments (
  comment_id SERIAL PRIMARY KEY,
  session_id INTEGER REFERENCES surf_sessions(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  comment_text TEXT NOT NULL CHECK (char_length(comment_text) <= 500),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_comments_session_id ON comments(session_id);
CREATE INDEX idx_comments_created_at ON comments(created_at DESC);
```

### Update existing queries
- Add comment count aggregation to session retrieval functions in `database_utils.py`.

## Frontend Components

### New Component: `CommentModal.jsx`
- **Pattern**: Similar to `ShakaModal.jsx`.
- **Contents**:
    - Header: Session title
    - Scrollable comment list with user names, text, timestamps
    - Text input at bottom (500 character limit, show counter)
    - Submit button
    - Close X button

### Update Components
- **`SessionTile.jsx`**: Add comment icon + count (bottom right, next to shakas).
- **`SessionDetail.jsx`**: Add comment icon + count in same section as shakas.
- **Interaction**: Both should open `CommentModal` on click.

## Implementation Notes
- **Permissions**: No restrictions for MVP_1 - any logged-in user can comment on any session.
- **Character Limit**: 500 characters (enforced backend + frontend).
- **Edit/Delete**: Not supported in MVP_1.
- **Real-time**: Standard REST API, no Supabase real-time subscriptions needed.
- **UI Flexibility**: Final positioning of comment count icon can be adjusted during implementation.

## Tasks (Assigned to: stefanoscotti)

### Backend
1.  ✅ Create `comments` table in Supabase.
2.  ✅ Add `POST /api/sessions/{session_id}/comments` endpoint.
3.  ✅ Add `GET /api/sessions/{session_id}/comments` endpoint.
4.  ✅ Update session query functions to include `comment_count`.

### Frontend
5.  Create `CommentModal.jsx` component.
6.  Add comment icon + count to `SessionTile.jsx`.
7.  Add comment icon + count to `SessionDetail.jsx`.
8.  Wire up modal open/close and API calls.

### Test
9.  Comment creation, display, and count accuracy.

## Acceptance Criteria
- Users can click comment icon on any session tile or detail view.
- Comment modal opens showing all existing comments.
- Users can submit new comments (up to 500 chars).
- Comment count displays accurately on tiles and detail views.
- Comments show commenter name and timestamp.
- Character counter shows remaining chars while typing.
