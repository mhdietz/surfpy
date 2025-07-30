# Forecast Feature Removal Plan (Backend Only)

This document outlines the plan to remove the backend functionality for the surf forecasting feature. The primary goal is to cleanly disable the feature while archiving the existing code for potential future use.

## Guiding Principles

1.  **Archive, Don't Delete**: All code related to the forecast feature will be moved to a dedicated, isolated archive directory. This makes it easy to re-integrate later and keeps the main codebase clean.
2.  **Minimal Intrusion**: We will only modify the necessary files to disable the feature. The `surfpy` library will not be modified.

---

## Implementation Tasks

### Task 1: Create Archive Directory

A new top-level directory will be created to house the archived code.

- **Action**: Create the following directory structure:
  - `archives/forecast_logic/ocean_data/`

### Task 2: Remove the Forecast Endpoint from the Flask App

This step disables the public-facing API for the forecast feature.

- **File to Modify**: `surfdata.py`
- **Action**:
  1.  Locate and delete the entire `/api/forecast/<string:spot_name>` route handler function (`get_forecast_endpoint`).
  2.  Remove the corresponding import statement at the top of the file: `from ocean_data.forecast import get_surf_forecast`.

### Task 3: Archive the Core Forecast Logic

The main file responsible for generating the forecast will be moved to the archive.

- **File to Move**: `ocean_data/forecast.py`
- **Action**: Move the file to its new location: `archives/forecast_logic/ocean_data/forecast.py`.

---

## Summary of File Modifications

- **CREATED**: `archives/forecast_logic/ocean_data/`
- **MODIFIED**: `surfdata.py` (Endpoint and import removed)
- **MOVED**: `ocean_data/forecast.py` -> `archives/forecast_logic/ocean_data/forecast.py`
- **UNCHANGED**: The `surfpy` directory and all its contents, including `surfpy/wavemodel.py`, will be left untouched.

---

## Success Criteria

The operation will be considered successful when the following conditions are met:

1.  **File Archived**: The `forecast.py` file is successfully moved to the new `archives/` directory structure.
2.  **Endpoint Disabled**: The `/api/forecast/...` endpoint is no longer present in the `surfdata.py` codebase and returns a 404 Not Found error if a request is made to it.
3.  **Application Stability**: The Flask application can be built and run without any import errors, exceptions, or other issues related to the removed forecast code.
4.  **No Regressions**: All other existing API endpoints (e.g., session logging, authentication, user search) continue to function as expected.