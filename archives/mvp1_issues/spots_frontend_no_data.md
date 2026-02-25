## Parent Issue
Part of: [MVP_1] Expanded Surf Spots with Typeahead

## Description
Update session detail view to gracefully handle sessions at spots without surf data.

## Component to Update

**File:** `SessionDetail.jsx`

## Current Behavior
Session detail view displays:
- Swell data
- Wind & Weather data
- Tide data

**Problem:** If spot has `has_surf_data = false`, these fields will be null/empty

## Proposed Solutions

**Option A: Hide surf data sections**
- If `spot.has_surf_data === false`, don't render Swell/Wind/Tide cards at all
- Cleaner UI, less confusing

**Option B: Show placeholder message**
- Render empty cards with message: "Surf data not available for this location"
- More informative

**Recommendation:** Option A (hide sections) - cleaner UX

## Tasks
- [ ] Add `has_surf_data` field to session detail API response (if not already included)
- [ ] Update `SessionDetail.jsx` to check `has_surf_data` flag
- [ ] Conditionally render surf data sections based on flag
- [ ] Test with session at spot without surf data
- [ ] Test with session at spot with surf data (should work as before)
- [ ] Ensure no errors or broken UI for either case
- [ ] Update any other views that show surf data (if applicable)

## Example Code Structure
```jsx
{session.spot.has_surf_data ? (
  <>
    <SwellCard data={session.swell} />
    <WindCard data={session.wind} />
    <TideCard data={session.tide} />
  </>
) : (
  // Option: Show message
  <div>Surf data not available for this location</div>
  // Or just don't render anything (Option A)
)}
```

## Acceptance Criteria
- [ ] Sessions at spots without surf data display correctly (no errors)
- [ ] Surf data sections hidden or show appropriate message
- [ ] Sessions at spots WITH surf data still show all data
- [ ] No console errors for either case
- [ ] UI looks clean and intentional (not broken)

## Estimated Effort
0.5 days