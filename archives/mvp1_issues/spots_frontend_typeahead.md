## Parent Issue
Part of: [MVP_1] Expanded Surf Spots with Typeahead

## Description
Replace spot dropdown with typeahead search component in session creation.

## Component to Update

**File:** `CreateSessionPage.jsx` (or wherever spot selection lives)

**Replace:** Dropdown `<select>` element

**With:** Typeahead/Combobox component

## Typeahead Specifications

**Library:** Use React Select, Downshift, or similar combobox library

**Behavior:**
- Loads all spots from `GET /api/spots` on component mount
- Client-side filtering as user types
- Search matches spot name (case-insensitive, substring match)
- Display format: `"{name} - {region}, {country}"`
  - Example: "Bells Beach - Victoria, Australia"
- If `has_surf_data = false`, show indicator: "(No surf data)" in gray text
- No results state: "Can't find your spot? Email us at hello@slapp.com"

**Example Display:**
```
Type to search...
──────────────────
Bells Beach - Victoria, Australia
Steamer Lane - California, USA
13th Beach - Victoria, Australia (No surf data)
Ocean Beach (north) - California, USA
```

## Tasks
- [ ] Install/import typeahead library (if not already available)
- [ ] Load spots from `GET /api/spots` on page load
- [ ] Replace dropdown with typeahead component
- [ ] Implement client-side filtering by spot name
- [ ] Format display: "Name - Region, Country"
- [ ] Add "(No surf data)" indicator for spots without buoys
- [ ] Implement "no results" state with contact message
- [ ] Ensure selected spot passes correct ID to session creation
- [ ] Test typeahead search and selection
- [ ] Test on mobile (ensure keyboard doesn't obscure results)
- [ ] Add loading state while fetching spots

## Acceptance Criteria
- [ ] Typeahead replaces old dropdown
- [ ] Can search spots by typing (filters as you type)
- [ ] Display shows name, region, country
- [ ] Spots without surf data show indicator
- [ ] Selecting spot populates form correctly
- [ ] "No results" message shows appropriate contact info
- [ ] Works smoothly with 100+ spots (no lag)
- [ ] Mobile experience is usable
- [ ] Can still select existing ~20 spots

## Estimated Effort
1.5 days