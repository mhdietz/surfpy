## Background
When users click into a session from feed or journal, then return, they lose their scroll position and must scroll back down. Persist scroll position to improve UX.

## Problem

**Current behavior:**
1. User scrolls down feed to session #25
2. User clicks session #25 → navigates to detail view
3. User clicks back button
4. **Bug:** Returns to top of feed (user must scroll down again)

**Expected behavior:**
User returns to feed with session #25 visible (same scroll position)

## Technical Approach

**Recommended:** React State + Session Storage

**Implementation:**
- Track scroll position in Feed and Journal components using React state
- Persist to `sessionStorage` as backup (survives page refresh within session)
- Restore scroll position when returning from session detail view
- Use `useEffect` to set scroll position on component mount

**Alternative:** React Router state (pass scroll position through navigation)

**Choice:** Developer discretion - use approach that feels most natural

## Affected Views

- **Feed page** (`Feed.jsx`)
- **Journal page** (`JournalPage.jsx`) - both "My Journal" and friend journals

**Not affected:**
- Leaderboard
- Create/Edit session pages

## User Flows to Support

### Basic Flow
1. User scrolls in feed
2. User clicks session → session detail
3. User clicks back → **returns to same position**

### Complex Flow  
1. User scrolls in feed
2. User clicks session → session detail
3. User clicks edit → edit session
4. User saves/cancels → back to feed → **returns to original position**

## Edge Cases
- If session list updates (new sessions added): Best effort to maintain position
- If user navigates away from feed entirely (e.g., to leaderboard), position can reset
- Position should persist within browser session (use sessionStorage, not localStorage)

## Tasks

**Feed Component:**
- [ ] Add scroll position tracking to `Feed.jsx`
- [ ] Store scroll Y position in React state
- [ ] Save to `sessionStorage` on navigation away
- [ ] Restore scroll position from sessionStorage on mount (if returning from detail)
- [ ] Test: feed → detail → back

**Journal Component:**
- [ ] Add scroll position tracking to `JournalPage.jsx`
- [ ] Store scroll Y position in React state
- [ ] Save to `sessionStorage` on navigation away
- [ ] Restore scroll position from sessionStorage on mount
- [ ] Test: journal → detail → back

**Edge Cases:**
- [ ] Test: feed → detail → edit → back (should return to original position)
- [ ] Test: Multiple back/forward navigations
- [ ] Test: New sessions added to feed while viewing detail
- [ ] Clear position from sessionStorage when navigating away from feed entirely

**Performance:**
- [ ] Verify no scroll jank or flashing on position restore
- [ ] Verify no performance issues from scroll tracking

## Acceptance Criteria
- [ ] User returns to same scroll position in feed after viewing session
- [ ] User returns to same scroll position in journal after viewing session
- [ ] Works with browser back button
- [ ] Works with in-app navigation
- [ ] Complex flow works: feed → detail → edit → back
- [ ] No visual jank or scroll flashing
- [ ] No performance degradation
- [ ] Position persists through page refresh (within session)

## Estimated Effort
1-2 days