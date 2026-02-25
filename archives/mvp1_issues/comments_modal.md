## Parent Issue
Part of: [MVP_1] Comments System

## Description
Create the CommentModal component for displaying and posting comments.

## Component Specification

**Component:** `CommentModal.jsx`

**Props:**
- `isOpen` (boolean)
- `onClose` (function)
- `sessionId` (number)
- `sessionTitle` (string)

**Layout:**
```
┌─────────────────────────────┐
│  Session Title         [X]  │
├─────────────────────────────┤
│                             │
│  Comment List (scrollable)  │
│  - User Name                │
│  - Comment Text             │
│  - Timestamp                │
│                             │
├─────────────────────────────┤
│  [Text Input Area]          │
│  Characters: 45/500         │
│  [Submit Button]            │
└─────────────────────────────┘
```

**Behavior:**
- Opens as modal overlay (similar to `ShakaModal.jsx`)
- Loads comments on open via `GET /api/sessions/{id}/comments`
- Shows loading state while fetching
- Displays comments chronologically (oldest first or newest first - your choice)
- Text input with 500 character counter
- Submit button disabled if empty or over 500 chars
- After successful post, refreshes comment list
- Close X button in top right

## Tasks
- [ ] Create `CommentModal.jsx` component file
- [ ] Implement modal layout and styling (reuse ShakaModal patterns)
- [ ] Add API call to fetch comments on modal open
- [ ] Display comment list with user names and timestamps
- [ ] Implement text input with character counter (500 max)
- [ ] Add submit button with disabled state logic
- [ ] Implement POST comment API call
- [ ] Refresh comment list after successful post
- [ ] Add loading states and error handling
- [ ] Test on mobile and desktop

## Acceptance Criteria
- [ ] Modal opens and closes correctly
- [ ] Comments load and display with names and timestamps
- [ ] Can type and submit new comments
- [ ] Character counter shows remaining chars (updates live)
- [ ] Submit disabled when empty or >500 chars
- [ ] New comment appears in list after posting
- [ ] Works smoothly on mobile
- [ ] Loading and error states handled gracefully

## Estimated Effort
1.5 days