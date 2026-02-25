## Parent Issue
Part of: [MVP_1] Expanded Surf Spots with Typeahead

## Description
Update database schema and create Python import script for bulk spot import.

## Database Schema Updates
```sql
ALTER TABLE surf_spots ADD COLUMN country TEXT;
ALTER TABLE surf_spots ADD COLUMN region TEXT;
ALTER TABLE surf_spots ADD COLUMN has_surf_data BOOLEAN DEFAULT false;

-- Update existing spots
UPDATE surf_spots SET has_surf_data = true WHERE swell_buoy_id IS NOT NULL;
```

**Updated Fields:**
- `id`, `name`, `slug`, `latitude`, `longitude` (existing)
- `swell_buoy_id`, `tide_station_id`, `met_buoy_id` (existing, nullable)
- `country` (new) - e.g., "Australia"
- `region` (new) - e.g., "VIC, Melbourne West"
- `has_surf_data` (new) - boolean flag

## Import Script

**Create:** `import_surf_spots.py`

**Functionality:**
- Reads `surfspots.json`
- Filters to specified spot list
- Maps buoys based on coverage areas (or manual mappings)
- Validates no duplicates with existing spots
- Inserts new spots with proper fields
- Logs import summary

**Inputs:**
- `surfspots.json` (5,980 spots)
- `curated_spots.json` (your filtered ~100-150 list)
- `buoy_mappings.json` (coverage areas or spot-to-buoy mappings)

**Output:**
- Inserted spots count
- Spots with/without surf data breakdown
- Any errors or duplicates

## Buoy Mapping Structure

**Option A: Coverage Areas**
```json
{
  "buoys": [
    {
      "swell_buoy_id": "46221",
      "met_buoy_id": "46221",
      "tide_station_id": "9414290",
      "coverage_area": {
        "min_lat": 37.5,
        "max_lat": 38.0,
        "min_lng": -122.8,
        "max_lng": -122.2
      },
      "name": "SF Bay Area coverage"
    }
  ]
}
```

**Option B: Manual Spot Mappings (CSV)**
```csv
spot_name,swell_buoy_id,met_buoy_id,tide_station_id
Steamer Lane,46221,46221,9414290
Pleasure Point,46221,46221,9414290
```

## Tasks
- [ ] Run SQL to update `surf_spots` schema
- [ ] Create `import_surf_spots.py` script
- [ ] Implement spot filtering logic
- [ ] Implement buoy assignment logic (coverage areas or manual)
- [ ] Add duplicate detection
- [ ] Add validation and error handling
- [ ] Test script with small sample (5-10 spots)
- [ ] Document script usage in README or comments

## Acceptance Criteria
- [ ] Database schema updated successfully
- [ ] Import script runs without errors
- [ ] Script correctly assigns buoys to US spots
- [ ] Script handles international spots (no buoys)
- [ ] Script detects and skips duplicate spots
- [ ] Test import of 5-10 sample spots successful
- [ ] Script is reusable for future spot additions

## Estimated Effort
2 days