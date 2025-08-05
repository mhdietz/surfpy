# Wind Data Implementation Plan (Revised - Single Station Test)

**Objective:** Test weather station approach with one surf spot (Steamer Lane) before full migration. Validate data quality and availability of NOAA weather stations vs NDBC buoys for improved wind accuracy.

**Owner:** Gemini
**Date:** 2025-08-04
**Target Completion Date:** 2025-08-05

---

## ✅ 1. Research & Station Mapping (2 hours) - COMPLETE

Initial research completed using automated Python script to identify potential weather stations. However, **approach revised** to single-station test due to data quality concerns and inland station proximity issues.

**Key Findings:**
- **Santa Cruz spots**: Current buoy 71.2 miles away
- **Potential improvement**: Weather stations 2.5-3.6 miles (AP803, C9585)
- **Concern identified**: AP803 is inland, may not capture coastal wind patterns
- **Target station for test**: **F2595** (suspected to be more coastal than algorithmic results)

**Decision:** Test single station (F2595) with Steamer Lane before broader implementation.

---

## ✅ 2. Single Station Implementation & Testing (3 hours) - COMPLETE

### **✅ Phase 1: Extend `surfpy/weatherapi.py` (1 hour) - COMPLETE**
-   ✅ **Task 1: Create `fetch_station_observations` function.**
    -   Signature: `fetch_station_observations(station_id, target_datetime, window_hours=1)`.
    -   Construct URL: `https://api.weather.gov/stations/{station_id}/observations?start={start_iso}&end={end_iso}`.
    -   Make HTTP request with error handling (404, 500, timeout).
    -   Return raw JSON response.

-   ✅ **Task 2: Create `parse_station_observations` function.**
    -   Parse JSON response from NOAA weather station API.
    -   Extract `windDirection.value` and `windSpeed.value` from `features` array.
    -   **Unit conversion**: Wind speed from km/h to knots.
    -   Create and return `BuoyData` objects (maintain existing interface).
    -   Handle missing/null wind data gracefully.

### **✅ Phase 2: Add Weather Station Detection Logic (0.5 hours) - COMPLETE**
-   ✅ **File:** `ocean_data/meteorology.py`
-   ✅ **Task 1: Modify `fetch_meteorological_data`.**
    -   Add station type detection: `is_weather_station(station_id)` 
    -   Route to weather station logic for F2595, buoy logic for others:
    ```python
    def fetch_meteorological_data(station_id, target_datetime):
        if is_weather_station(station_id):
            return fetch_weather_station_data(station_id, target_datetime)
        else:
            return fetch_buoy_data(station_id, target_datetime)  # Existing
    ```
    -   Use existing `find_closest_data` utility for time matching.

### **✅ Phase 3: Create Test Script (0.5 hours) - COMPLETE**
-   ✅ **File:** `test_weather_station.py` (standalone)
-   ✅ **Validate F2595 data availability and quality:**
    -   Test recent timestamps (last 24-48 hours) ✅ **PASSED**
    -   Check data frequency and consistency ✅ **PASSED**
    -   Compare wind data format vs buoy data ✅ **PASSED**
    -   Verify unit conversions work correctly ✅ **PASSED**
    -   Test edge cases (missing data, old timestamps) ✅ **PASSED**

### **✅ Phase 4: Database Update & Integration Test (1 hour) - IN PROGRESS**
-   ✅ **Single spot migration:**
    ```sql
    -- Backup current setting
    SELECT met_buoy_id FROM surf_spots WHERE slug = 'steamer-lane';
    
    -- Test with weather station
    UPDATE surf_spots SET met_buoy_id = 'F2595' WHERE slug = 'steamer-lane';
    ```
    **Status: COMPLETE** - Manual database update completed via Supabase dashboard

-   ⏳ **Integration testing:**
    -   Test session creation API with Steamer Lane using Postman
    -   Verify wind data appears in `raw_met` field with F2595 data
    -   Compare data quality vs previous buoy data
    -   Test system behavior and performance

---

## 3. Validation & Decision (1 hour)

**Success Criteria for F2595:**
- ✅ Consistent wind data availability (last 7 days) - **PASSED** (standalone test)
- ✅ Update frequency better than buoys (>6 hours) - **PASSED** (standalone test)
- ✅ Reasonable wind speed/direction values for coastal location - **PASSED** (standalone test)
- ✅ Data format integrates cleanly with existing BuoyData interface - **PASSED** (standalone test)
- ⏳ No significant performance impact on session creation - **TESTING IN PROGRESS**

**Decision Points:**
- **If successful**: Consider expanding to other spots with similar station approach
- **If data quality poor**: Revert to buoy and explore hybrid approach
- **If inconsistent**: Keep as fallback option only

**Rollback Plan:**
```sql
-- Revert to original buoy if needed
UPDATE surf_spots SET met_buoy_id = '46012' WHERE slug = 'steamer-lane';
```

---

## 4. Future Expansion Strategy (if test succeeds)

**Incremental Rollout:**
1. **Phase 1**: Steamer Lane (F2595) - **TESTING IN PROGRESS**
2. **Phase 2**: Add 2-3 more coastal spots with verified stations
3. **Phase 3**: Inland spots where weather stations show clear improvement
4. **Phase 4**: Full migration with hybrid buoy/station fallback system

**Architecture for Expansion:**
- Maintain `met_buoy_id` field (supports both buoys and weather stations)
- Weather station detection by ID format/prefix
- Dual-source fallback logic (station → buoy → fail)

---

## Implementation Files:

**✅ Completed Files:**
- ✅ `test_weather_station.py` - Standalone validation script
- ✅ Updates to `surfpy/weatherapi.py` - Weather station API functions
- ✅ Updates to `ocean_data/meteorology.py` - Routing logic

**Generated Research Files (can be deleted after test):**
- `weather_station_mapper.py` - Research script
- `surf_spot_weather_stations.csv` - Station mapping results  
- `weather_station_migration.sql` - Full migration (not used for single test)

---

## Current Status:
✅ **Code implementation complete**  
✅ **Database updated (F2595 active for steamer-lane)**  
⏳ **Integration testing with Postman in progress**  
⏳ **Final validation pending**