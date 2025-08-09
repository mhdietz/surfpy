# Project Surf App: Gemini Context

This document summarizes the current architecture and key features of the Surf App project. It is intended to be a living document, updated as the project evolves, to provide context for future development sessions.

## 1. System Architecture

The application is a full-stack surf logging and forecasting platform. The backend is a Python Flask application that serves a JSON API consumed by a React frontend client.

### Backend
-   **Backend (`surfdata.py`)**: The core of the application is a **Flask API**. It handles all incoming requests, user authentication, and API routing. It uses `Flask-Caching` for performance on data-intensive endpoints.

-   **Database (`database_utils.py`)**: All persistent data is stored in a **PostgreSQL** database, managed via the `database_utils.py` module. This module uses the `psycopg2` library to interact with the database. Key tables include `surf_sessions_duplicate` for session logs, `auth.users` for user data, `surf_spots` for location configurations, `session_participants` for tagging, and `session_shakas` for reactions.

-   **Data Abstraction Layer (`ocean_data/`)**: This Python package serves as a high-level interface for all external oceanographic data. It abstracts the complexities of fetching and processing data, providing simple functions like `fetch_swell_data` to the main application.

-   **Core Data Engine (`surfpy/`)**: This is a powerful, low-level library that acts as the engine for all data fetching and processing. It interfaces directly with external data sources like NOAA buoys and tide stations.

### Frontend
-   **Frontend (`/frontend`)**: React 19.1.1 + Vite 7.1.1 application with Tailwind CSS v3.4.0 for styling. Mobile-first responsive design optimized for surf logging on mobile devices.

-   **Build System**: Vite development server with hot module replacement. Configured for network access (`host: '0.0.0.0'`) to support mobile testing on local network.

-   **Authentication Flow**: JWT token-based authentication with centralized API service. Stores access tokens for protected endpoint calls using `Authorization: Bearer <token>` header format.

-   **Component Architecture**: Page-based routing structure with three main sections: Session Feed, Create Session, and My Journal. Navigation via bottom nav bar following mobile app conventions.

## 2. Deployment Architecture

### Production Deployments
-   **Backend**: `surfdata.vercel.app` - Flask API deployed from project root
-   **Frontend**: `slapp-frontend.vercel.app` - React app deployed from `/frontend` directory

### Development Workflow
-   **Branch Strategy**: Feature branches with pull request workflow
-   **Preview Deployments**: Vercel automatically creates preview URLs for branch pushes
-   **Local Development**: 
    - Backend: Python Flask server
    - Frontend: Vite dev server on `http://localhost:5173` (network accessible for mobile testing)

## 3. Core Features & Data Flow

### a. User Authentication & Management
-   **Auth**: User signup and login are handled via Supabase's REST API.
-   **Authorization**: API endpoints are protected using a JWT-based `@token_required` decorator.
-   **User Search**: The `/api/users/search` endpoint allows for finding other users on the platform.

### b. Surf Session Logging (CRUD)
-   **Flow**: When a user logs a session, the backend fetches the relevant historical swell, meteorological, and tide data and saves it to the database with the session details.
-   **Relational Session Tagging**: The application uses a relational model for tagging users in a session. Instead of duplicating sessions, a single session record is created, and all participants (the creator and tagged users) are linked to it via records in the `session_participants` table. This approach ensures data integrity, simplifies queries, and is highly scalable.
-   **Shaka Reactions**: Users can give a "shaka" to any surf session. This is handled by a `POST /api/surf-sessions/<session_id>/shaka` endpoint that toggles the reaction. All session retrieval endpoints now include a `shakas` object containing the total count, a preview of users who have reacted, and a `viewer_has_shakaed` boolean flag.

## 4. Key Technical Decisions & Concepts

### Backend Decisions
-   **Database-Driven Configuration**: All surf spot configurations, including names, slugs, data source IDs, and breaking wave parameters, are stored in the `surf_spots` database table. This makes the system scalable and easy to manage.

-   **Relational Data Model**: The session tagging feature was explicitly refactored from a data duplication model to a proper relational model using the `session_participants` table. This was done to ensure data integrity via foreign keys and to allow for efficient, scalable querying.

-   **Timezone Handling**: All session timestamps are now stored in the database as timezone-aware UTC (`TIMESTAMP WITH TIME ZONE`). The API consistently returns these as ISO 8601 UTC strings, with the client responsible for local time display. This ensures unambiguous time representation across the system.

-   **Backward Compatibility**: The use of a `LEGACY_LOCATION_MAP` in `ocean_data/location.py` ensures that older API clients or bookmarks still function even though the location management system has been updated.

### Frontend Decisions
-   **React + Vite**: Modern build tooling for fast development and hot module replacement
-   **Tailwind CSS v3**: Utility-first CSS framework for rapid mobile-first development
-   **Mobile-First Design**: Primary focus on mobile experience with responsive design principles
-   **Component Strategy**: Page-based architecture matching detailed UI mockups for rapid prototyping
-   **Separate Deployment**: Frontend and backend deployed as separate Vercel projects for independent scaling and development

### c. Lightweight Session Endpoints & Filtering
-   **Performance Optimization**: Session list views (main feed, user journals) now utilize lightweight API responses, excluding large `raw_swell`, `raw_met`, and detailed tide data. This significantly improves frontend performance.
-   **Server-Side Filtering**: These lightweight endpoints support server-side filtering by swell height, period, and direction, ensuring only relevant data is transferred. The regional filter is planned for a future iteration.

## 5. Development Setup

### Frontend Setup
-   **Prerequisites**: Node.js 18+, npm
-   **Local Development**: `cd frontend && npm install && npm run dev`
-   **Mobile Testing**: Vite configured for network access at `http://192.168.1.XXX:5173`
-   **Documentation**: See `FRONTEND_SETUP.md` for detailed setup instructions

### Collaboration Workflow
-   **Feature Branches**: Work on separate branches to avoid merge conflicts
-   **Component Development**: Build UI components with mock data first, then integrate APIs
-   **API Integration**: Use Gemini's full-stack visibility for accurate endpoint integration

## 6. Archived Features

This section documents features that were previously implemented but have been removed from the active codebase. The code for these features is preserved in the `archives/` directory for potential future use.

### a. 7-Day Surf Forecast
-   **Status**: Removed from the backend API. The core logic file (`ocean_data/forecast.py`) has been moved to `archives/forecast_logic/ocean_data/`.
-   **Original Implementation**: The feature provided a 7-day, hour-by-hour surf forecast via a cached `/api/forecast/<spot_name>` endpoint. It worked by combining historical "actuals" from buoy readings with future "forecasts" from GFS wave model bulletins. It also calculated the breaking wave height for each spot based on its specific bathymetry.