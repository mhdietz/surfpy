# Feature 2: Expanded Surf Spots with Typeahead - Implementation Plan

## Status: Backend Implementation In Progress

## Phase 1: Data Preparation ✓ COMPLETE

### Completed Tasks:
1. ✓ Created spot curation script (`curate_spots_simple.py`)
2. ✓ Curated 241 surf spots from 5,890 available spots
3. ✓ Created buoy mapping configuration (`buoy_mappings.py`)
4. ✓ Defined coverage areas for 16 US coastal regions
5. ✓ Generated import SQL with 146 spots having buoy data, 95 without
6. ✓ Created comprehensive documentation

### Files Generated:
- `/home/claude/curated_spots.json` - 241 curated spots
- `/home/claude/buoy_mappings.py` - Buoy coverage configuration
- `/home/claude/import_surf_spots.py` - Import script
- `/home/claude/import_surf_spots.sql` - Ready-to-run SQL (241 INSERT statements)
- `/home/claude/import_summary.txt` - Import statistics
- `/home/claude/SPOT_CURATION_SUMMARY.md` - Documentation

## Phase 2: Backend Implementation (In Progress with Gemini)

### 2.1 Database Schema Updates ✓ COMPLETE
**File:** Use Supabase dashboard or migration script
```sql
-- Add new columns to surf_spots table
ALTER TABLE surf_spots_duplicate ADD COLUMN IF NOT EXISTS country TEXT;
ALTER TABLE surf_spots_duplicate ADD COLUMN IF NOT EXISTS region TEXT;
ALTER TABLE surf_spots_duplicate ADD COLUMN IF NOT EXISTS has_surf_data BOOLEAN DEFAULT false;

-- Update existing spots to have has_surf_data = true
UPDATE surf_spots_duplicate SET has_surf_data = true WHERE swell_buoy_id IS NOT NULL;
```
**Note:** User created a new table `surf_spots_duplicate` for this work.

### 2.2 Run Import SQL ✓ COMPLETE
**File:** `import_surf_spots.sql`
- User executed the generated SQL file on Supabase against `surf_spots_duplicate`.
- This imported all 241 new spots.

### 2.3 Update Code to Use New Table ✓ COMPLETE
**File:** `database_utils.py`
- Find and replace all instances of `surf_spots` and `surf_spots_backup` with `surf_spots_duplicate` to ensure the application uses the new, expanded table. (Completed manually by user)

### 2.4 Create GET /api/spots Endpoint ✓ COMPLETE
**File:** `surfdata.py`, `database_utils.py`

**`database_utils.py`**
- Create a new function `get_all_spots_for_typeahead()` that queries `surf_spots_duplicate`.

**`surfdata.py`**
- Add new endpoint `@app.route('/api/spots', methods=['GET'])` that calls the new database function.

```python
# In database_utils.py
def get_all_spots_for_typeahead():
    """ Get all surf spots for the typeahead component. """
    # ... SQL query on surf_spots_duplicate ...

# In surfdata.py
@app.route('/api/spots', methods=['GET'])
def get_spots():
    """
    Get all surf spots for typeahead component.
    Returns all spots with id, name, slug, country, region, has_surf_data.
    """
    # ... implementation ...
```

### 2.5 Update Session Logging to Handle Missing Surf Data (To Do)
**File:** `surfdata.py` - Update `create_surf_session` and `update_surf_session`

In the session creation/update logic, add a check for `has_surf_data` on the `spot_config` object. If `false`, the logic to fetch swell, meteorology, and tide data should be skipped.

### 2.6 Update Session Responses to Include `has_surf_data` (To Do)
**File:** `database_utils.py` - `get_session_detail()` and `get_session_summary_list()`

Ensure session detail responses include the `has_surf_data` flag by joining with the `surf_spots_duplicate` table. This is critical for the frontend to know whether to display surf data components.

## Phase 3: Frontend Implementation (To Do with Gemini)

### 3.1 Create GET /api/spots Integration
**File:** `frontend/src/services/api.js`

Add new API function:
```javascript
export const getSpots = async () => {
  const response = await fetch(`${API_BASE_URL}/api/spots`); // Corrected path
  if (!response.ok) throw new Error('Failed to fetch spots');
  const json = await response.json();
  return json.data; // Assuming data is nested under a 'data' key
};
```

### 3.2 Replace Dropdown with Typeahead
**File:** `frontend/src/pages/CreateSessionPage.jsx` (or wherever spot selection is)

Replace existing dropdown with a typeahead component (e.g., `react-select`).

### 3.3 Update Session Detail View
**File:** `frontend/src/pages/SessionDetailPage.jsx` (or similar)

Add graceful handling for sessions without surf data, conditionally rendering components based on the `has_surf_data` flag from the session object.

## Phase 4: Testing (To Do)

... (testing plan remains the same) ...

## Phase 5: Deployment (To Do)

... (deployment plan remains the same) ...