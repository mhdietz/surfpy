## Parent Issue
Part of: [MVP_1] Comments System

## Description
Add comment icon and count to session tiles and detail views, wired up to open CommentModal.

## Components to Update

### 1. SessionTile.jsx
**Location:** Bottom right corner (next to shakas)

**Add:**
- Comment icon (💬 or use icon library)
- Comment count number
- Click handler to open CommentModal

**Layout:**
```
┌─────────────────────────┐
│  Session Title          │
│  Date, Location         │
│  Notes...               │
│                         │
│           🤙 2   💬 5   │ <- Add comment count here
└─────────────────────────┘
```

### 2. SessionDetail.jsx
**Location:** In same section as Shakas/Stoke cards

**Add:**
- Comment section (similar to Shakas section)
- Comment icon + count
- Click handler to open CommentModal

## Tasks
- [ ] Import `CommentModal` component
- [ ] Add comment count to SessionTile component
- [ ] Add comment icon with click handler to open modal
- [ ] Pass `sessionId` and `sessionTitle` to CommentModal
- [ ] Add comment count to SessionDetail component
- [ ] Add comment icon with click handler in detail view
- [ ] Ensure comment count updates after posting (refresh or callback)
- [ ] Style comment icon consistently with shakas
- [ ] Test opening modal from both tile and detail views

## Acceptance Criteria
- [ ] Comment icon and count visible on session tiles
- [ ] Comment icon and count visible on session detail view
- [ ] Clicking icon opens CommentModal with correct session
- [ ] Comment count displays accurately (0, 1, 5, etc.)
- [ ] After posting comment, count updates correctly
- [ ] Icon styling matches existing UI patterns
- [ ] Works on mobile and desktop

## Estimated Effort
1 day