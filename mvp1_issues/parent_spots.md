## Background
Expand supported surf spots from ~20 to ~100-150 locations to support international travel. Replace dropdown with typeahead search for better UX as spot list grows.

## Overview
This parent issue tracks the complete Surf Spots expansion and typeahead implementation. See sub-issues for specific backend and frontend tasks.

## Sub-Issues
- Backend: Schema updates and import script
- Backend: Curate spots and run import
- Frontend: Typeahead component
- Frontend: Handle missing surf data

## Key Requirements
- Import ~100-150 curated spots from `surfspots.json`
- US spots assigned buoy IDs where applicable
- International spots imported without buoys (`has_surf_data = false`)
- Typeahead search replaces dropdown
- Display format: "Name - Region, Country"

## Acceptance Criteria
- [ ] All sub-issues completed and closed
- [ ] ~100-150 spots imported to database
- [ ] Typeahead search works smoothly
- [ ] Sessions at international spots handle gracefully
- [ ] Existing ~20 spots still work correctly

## Estimated Effort
4-5 days total