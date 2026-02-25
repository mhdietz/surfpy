## Parent Issue
Part of: [MVP_1] Expanded Surf Spots with Typeahead

## Description
Curate final spot list, define buoy mappings, and run full import to production database.

## Tasks

### 1. Curate Spot List (~100-150 spots)

**Priority Regions:**
- **Australia:** Major VIC, NSW, QLD, WA spots (for your trip)
- **Mexico:** Baja California, Oaxaca, Nayarit spots (for Frank)
- **USA - California:** All major spots (SF, Santa Cruz, LA, SD)
- **USA - Hawaii:** North Shore, South Shore spots
- **USA - East Coast:** NY, NJ, NC, SC, FL spots
- **Other:** Top international destinations (Costa Rica, Indonesia, Portugal)

**Preserve:** All existing ~20 spots currently in database

**Output:** `curated_spots.json` (filtered list from `surfspots.json`)

### 2. Define Buoy Mappings

**Research and document:**
- Which NOAA buoys cover major US surf regions
- Coverage areas (lat/lng bounds) for each buoy
- Or manual spot-to-buoy assignments

**Output:** `buoy_mappings.json` or `buoy_mappings.csv`

### 3. Run Import
```bash
python import_surf_spots.py \
  --spots curated_spots.json \
  --buoys buoy_mappings.json \
  --dry-run  # Test first

# If successful:
python import_surf_spots.py \
  --spots curated_spots.json \
  --buoys buoy_mappings.json
```

### 4. Create API Endpoint

**Add to `surfdata.py`:**

**GET** `/api/spots`

**Response:**
```json
{
  "spots": [
    {
      "id": 1,
      "name": "Bells Beach",
      "country": "Australia",
      "region": "Victoria",
      "has_surf_data": false
    }
  ]
}
```

## Tasks
- [ ] Filter `surfspots.json` to ~100-150 priority spots
- [ ] Save as `curated_spots.json`
- [ ] Research NOAA buoys and define coverage areas
- [ ] Create `buoy_mappings.json`
- [ ] Run import script with `--dry-run` flag
- [ ] Review dry-run output for errors
- [ ] Run full import to database
- [ ] Verify spot count in database (~120-170 total including existing)
- [ ] Create `GET /api/spots` endpoint in `surfdata.py`
- [ ] Test endpoint returns all spots with proper fields
- [ ] Verify existing ~20 spots still work in session creation

## Acceptance Criteria
- [ ] ~100-150 new spots imported successfully
- [ ] US spots have buoy IDs assigned where applicable
- [ ] International spots marked `has_surf_data = false`
- [ ] Existing spots unchanged and still functional
- [ ] `GET /api/spots` endpoint returns all spots
- [ ] No duplicate spots in database
- [ ] Can create sessions at new spots successfully

## Estimated Effort
2 days (includes research time for buoy mappings)