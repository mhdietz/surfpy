## Parent Issue
Part of: [MVP_1] Comments System

## Description
Create database schema and API endpoints for comments functionality.

## Database Schema

**New Table: `comments`**
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

## API Endpoints

### 1. Get Comments
**GET** `/api/sessions/{session_id}/comments`

**Response:**
```json
{
  "comments": [
    {
      "comment_id": 1,
      "session_id": 123,
      "user_id": "abc-123",
      "display_name": "Frank Kapp",
      "comment_text": "Sick session!",
      "created_at": "2025-12-01T10:30:00Z"
    }
  ],
  "count": 1
}
```

### 2. Create Comment
**POST** `/api/sessions/{session_id}/comments`

**Request:**
```json
{
  "comment_text": "Epic waves today!"
}
```

### 3. Update Session Endpoints
Add `comment_count` to:
- `GET /api/surf-sessions?view=feed`
- `GET /api/users/{user_id}/sessions?view=profile`
- `GET /api/surf-sessions/{id}`

## Tasks
- [ ] Create `comments` table in Supabase
- [ ] Add helper functions to `database_utils.py`:
  - `get_comments_for_session(session_id)`
  - `create_comment(session_id, user_id, comment_text)`
  - `get_comment_count(session_id)`
- [ ] Add `POST /api/sessions/{session_id}/comments` endpoint in `surfdata.py`
- [ ] Add `GET /api/sessions/{session_id}/comments` endpoint
- [ ] Update session query functions to include `comment_count`
- [ ] Enforce 500 character limit in backend validation
- [ ] Test all endpoints in Postman

## Acceptance Criteria
- [ ] Comments table created with proper indexes and constraints
- [ ] Can create comments via POST endpoint
- [ ] Can retrieve comments via GET endpoint
- [ ] Comment counts appear in session responses
- [ ] 500 char limit enforced (returns error if exceeded)
- [ ] All Postman tests pass

## Estimated Effort
2 days