# GEMINI Frontend Development Plan

## Overview
This document provides a systematic plan for building the SLAPP frontend using Gemini, designed for collaborative development with feature-based separation to minimize merge conflicts.

**Reference**: See `GEMINI_CONTEXT.md` for complete system architecture and backend API details.

## Development Philosophy
- **Component Library Approach**: Reusable components with Tailwind CSS for consistent, flexible design
- **Feature-Based Collaboration**: Complete user flows owned by individual developers
- **Authentication-First**: Address token management complexity early
- **API Centralization**: Single point of configuration for backend URL updates

## Collaborative Structure

### **Developer A (Primary)**: Authentication & Session Management
- Authentication system (login, signup, token management)
- Session creation and editing (single page form)
- Session detail views with user navigation
- Journal pages (works for any user - self or friends)
- User profile management

### **Developer B (Secondary)**: Social Features & Discovery  
- Session feed with social interactions
- User search overlay/modal system
- Shaka reactions and community features
- Leaderboards and community statistics

### **Shared Responsibility**: Core Component Library
- SessionTile, SessionsList, Navigation components
- Shared styling patterns and design system
- API service architecture

## Technical Foundation

### Project Structure
```
/frontend/src/
├── components/          # Shared component library
│   ├── ProtectedRoute.jsx  # Route guard for authenticated pages
│   ├── SessionTile.jsx     # Used across all session views
│   ├── SessionsList.jsx    # Used in feed, journals
│   ├── Navigation.jsx      # App navigation with bottom nav
│   ├── UserSearch.jsx      # Search overlay/modal
│   ├── ShakaModal.jsx      # Users who reacted modal
│   └── UI/                 # Basic UI components (buttons, inputs, filters)
├── pages/              # Main application pages
│   ├── Auth.jsx           # Login/signup page
│   ├── Feed.jsx           # Main feed after login
│   ├── Journal.jsx        # Session journal (any user) (Developer A)
│   ├── SessionDetail.jsx  # Individual session view (Developer A)
│   └── CreateSession.jsx  # Session creation form (Developer A)
├── services/           # API integration
│   ├── api.js             # Centralized API service
│   └── auth.js            # Token management (login, signup, logout)
├── context/            # Global React Context providers
│   └── AuthContext.jsx    # Manages global auth state and user data
├── config/             # Configuration
│   └── api.js             # Single API URL definition
└── utils/              # Helpers and mock data
    └── mockData.js
```

### **Navigation Structure & URLs**
```
Main Pages:
/auth/login              → Login page
/auth/signup            → Signup page
/feed                   → Session Feed (Feed tab active)
/feed?tab=leaderboard   → Session Feed (Leaderboard tab active)
/journal                → My Journal (current user, Log tab)
/journal?tab=stats      → My Journal (Stats tab active)
/journal/:userId        → Friend's Journal (Log tab)
/journal/:userId?tab=stats → Friend's Journal (Stats tab)
/session/:id            → Session Detail view
/create-session         → Session Creation form

Overlays/Modals:
- User Search Modal (triggered from header search icon or session creation)
- Shaka Users Modal (triggered from shaka count clicks)

Filtering Support:
- All list views (feed, journals) support backend filtering via URL parameters
- Filter options include swell conditions, regions, and other surf criteria
```

### **Navigation Patterns**
- **Bottom Navigation**: Session Feed | Create Session | My Journal
- **To Friend's Journal**: Click username in feed → `/journal/:userId`
- **User Search**: Header search icon → User Search Modal → Select user → Navigate to their journal
- **Session Detail**: Click any session tile → `/session/:id`
- **User Profile Links**: Available in session detail view for session participants

### API Configuration
```javascript
// src/config/api.js - Single source of truth for backend URL
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
// The VITE_API_URL is read from the .env file in the frontend directory.
// Example: VITE_API_URL=https://your-deployed-backend.vercel.app
```

---

## Phase 0: Foundational Improvements (Immediate Priority) - Complete ✅

The following foundational tasks have been completed, ensuring consistency, reusability, and maintainability for future development.

### 1. Centralize API Service ✅
- **Task**: Implemented the generic `apiCall` function in `services/api.js`.
- **Outcome**: All API requests now go through a centralized function that automatically includes the `Authorization` header. `login` and `signup` functions in `services/auth.js` have been refactored to use `apiCall`.

### 2. Build Reusable UI Components ✅
- **Task**: Created a set of basic, reusable UI components in the `frontend/src/components/UI/` directory.
- **Outcome**: `Button.jsx`, `Input.jsx`, `Card.jsx`, and `Spinner.jsx` components are available and have been integrated into `Auth.jsx` and `Feed.jsx`.

### 3. Standardize User Feedback ✅
- **Task**: Implemented a standard pattern for notifying the user of loading states and errors.
- **Outcome**: `Spinner.jsx` component is available for loading states. `react-hot-toast` has been integrated for non-blocking error and success notifications, used in `Auth.jsx`.

### 4. Use Environment Variables for API URL ✅
- **Task**: Moved the `API_BASE_URL` to an environment variable.
- **Outcome**: A `.env` file has been created in the `frontend` directory (`VITE_API_URL`). `config/api.js` now reads the API URL from this environment variable, allowing for easy switching between development and production environments.

---

## Phase 1: Authentication System (Developer A) - In Progress

### Objectives
- Solve token management complexity from v0 experience
- Create reliable auth flow foundation
- Establish secure API communication patterns

### Components Built
- **`pages/Auth.jsx`**: A mobile-first component containing the login and signup forms, styled with Tailwind CSS.
- **`services/auth.js`**: A service that handles API calls to `/login` and `/signup`, and manages the JWT in `localStorage`.
- **`context/AuthContext.jsx`**: A React Context provider that manages global authentication state (`isAuthenticated`, `user`) and exposes auth functions (`login`, `signup`, `logout`) to the entire app.
- **`components/ProtectedRoute.jsx`**: A route guard component that redirects unauthenticated users to the login page.

### Key Challenges to Address
- Token persistence across browser sessions
- Automatic token refresh or re-authentication
- Secure storage of authentication state
- Error handling for expired/invalid tokens

### API Integration
- `POST /api/auth/login` - User authentication
- `POST /api/auth/signup` - User registration
- Token format verification with backend team

### Success Criteria
- Users can signup/login reliably
- Authentication state persists across browser refresh
- Token management handles edge cases gracefully
- Foundation ready for protected route integration

---

## Phase 2: Core Component Library (Both Developers)

### Objectives
- Build flexible, reusable components for session data
- Establish consistent design patterns with Tailwind
- Create foundation for all session-related features

### Component Status

- **SessionTile**: ✅ **Complete for this phase**
  - **Completed**:
    - Displays all required session data (notes, rating, participants, etc.).
    - The entire tile is a clickable link to the session detail page.
    - The creator's name and participant names are clickable links to their journal pages.
  - **Deferred for Later**:
    - **Shaka API Integration**: The shaka button is not yet connected to the backend API. This will be handled as part of the "Shaka Reactions System" in Phase 4.
    - **UI Polish**: Advanced styling and the use of icons are deferred.

- **SessionsList**: ✅ **Complete**
  - Fetches and displays a list of surf sessions from the backend API.
  - Implements conditional rendering for loading, error, and empty states.
  - Integrated into the `Feed` page to display real session data.

- **Navigation**: ⏳ **Pending**
  - App shell and routing.

- **UserSearch**: ⏳ **Pending**
  - Search overlay/modal.

- **ShakaModal**: ⏳ **Pending**
  - Modal to show users who have reacted.

### Design System Foundations
- Tailwind CSS configuration and theme
- Component styling patterns
- Dark theme implementation
- Mobile-first responsive patterns

### Success Criteria
- Components render consistently across contexts
- Design easily modifiable in centralized locations
- Mobile experience optimized
- Ready for integration into feature pages

---

## Phase 3: Session Management Features (Developer A)

### Objectives
- Build complete session creation and editing flow
- Integrate with oceanographic data from backend
- Handle user tagging and participant management

### Features to Build
- **Session Creation**: 
  - Single page form with all fields visible
  - Location selection with regional grouping
  - User search and tagging via UserSearch modal
  - Form validation and error handling
  - Integration with backend surf spot data

- **Session Detail Views**:
  - Complete session information display
  - Surf conditions display (swell, wind, tide, temperature)
  - Clickable participant profiles → navigate to their journals
  - Edit/delete functionality for session owners
  - Shaka reactions with modal integration

- **Journal Pages**:
  - Flexible component works for any user (self or friends)
  - Log/Stats tab switching within same page
  - Filtering controls for surf conditions and regions
  - User context handling (me vs others)
  - URL parameter support for filters

### API Integration
- Backend surf spot data with regional organization
- User search and discovery endpoints
- Complete session CRUD operations
- User session history with filtering capabilities
- Individual session details with full surf data

### Success Criteria
- Complete session CRUD functionality
- User tagging works reliably
- Surf data integration displays correctly
- Mobile form experience optimized

---

## Phase 4: Social Features & Discovery (Developer B)

### Objectives
- Build social interaction features using established components
- Create community discovery and engagement tools
- Implement reaction and leaderboard systems

### Features to Build
- **Session Feed**:
  - Community session display using SessionsList
  - Feed/Leaderboard tab switching within same page
  - Pull-to-refresh and infinite scroll
  - Social context and user attribution
  - Clickable usernames navigate to their journals

- **User Search Integration**:
  - UserSearch modal integration across app
  - Header search icon triggers global user search
  - Session creation user tagging workflow
  - Search results with navigation to user journals

- **Shaka Reactions System**:
  - Reaction toggle functionality across all session views
  - ShakaModal showing users who reacted
  - User profile links from reaction modal
  - Real-time count updates

- **Leaderboards**:
  - Community rankings by sessions, surf time, fun rating
  - Tab switching within Feed page
  - Year selection and filtering capabilities
  - Current user highlighting in rankings

### API Integration
- Community session feeds with filtering support
- Shaka reaction toggle and user lists
- User search and discovery functionality
- User session history across all users
- Community statistics and leaderboard data

### Success Criteria
- Social features encourage community engagement
- Performance good with large datasets
- User discovery intuitive and functional
- Leaderboards motivate participation

---

## Phase 5: Integration & Polish (Both Developers)

### Objectives
- Complete API integration across all features
- Comprehensive testing and optimization
- Final polish for friends & family launch

### Integration Tasks
- **Complete API Integration**:
  - Replace all mock data with real API calls
  - Unified error handling patterns
  - Loading state standardization
  - Authentication guard implementation

- **Mobile Testing & Optimization**:
  - All features tested on mobile devices
  - Touch interaction optimization
  - Performance validation
  - Cross-browser compatibility

- **End-to-End Testing**:
  - Complete user journey validation
  - Edge case handling
  - Integration issue resolution
  - User feedback incorporation

### Success Criteria
- All P0 features work together seamlessly
- Mobile experience feels native
- Performance meets standards for friends & family launch
- No blocking bugs remain

---

## Development Guidelines

### Branch Strategy
```
feature/auth-system          # Developer A - Authentication
feature/session-management   # Developer A - Session CRUD
feature/social-features      # Developer B - Feed and reactions
feature/component-library    # Both - Shared components
feature/mobile-optimization  # Both - Final polish
```

### Component Library Standards
- **Single Responsibility**: Each component has one clear purpose
- **Prop Interface**: Well-documented props with TypeScript or PropTypes
- **Responsive Design**: Mobile-first with Tailwind utilities
- **Accessibility**: Proper ARIA labels and keyboard navigation
- **Testing**: Component works with various data scenarios

### Styling and Design
- **Mobile-First with Tailwind CSS**: All new components MUST be built mobile-first using Tailwind CSS utility classes.
- **No Inline Styles**: Avoid using inline `style` attributes. All styling should be handled by Tailwind classes to ensure consistency and maintainability.
- **Reference Components**: Use `pages/Auth.jsx` and `pages/Feed.jsx` as examples of the expected coding and styling standard.

### API Integration Pattern
```javascript
// Consistent pattern across all API calls
import { API_BASE_URL } from '../config/api.js';
import { getAuthToken } from '../services/auth.js';

const apiCall = async (endpoint, options = {}) => {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers
    },
    ...options
  });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  
  return response.json();
};
```

### Mobile Testing Protocol
1. Start dev server: `npm run dev`
2. Access via network: `http://192.168.1.XXX:5173`
3. Test on actual mobile device
4. Verify touch interactions and responsive design
5. Test form inputs and navigation

---

## Progress Tracking

### Authentication System ✅
- [x] Auth pages and forms (`pages/Auth.jsx`)
- [x] Token management service (`services/auth.js`)
- [x] Global auth state (`context/AuthContext.jsx`)
- [x] Route protection (`components/ProtectedRoute.jsx`)

### Core Component Library ✅
- [x] SessionTile component
- [x] SessionsList component
- [ ] Navigation and layout
- [ ] Design system foundation

### Session Management ✅
- [ ] Session creation flow
- [ ] Session detail views
- [ ] Session editing functionality
- [ ] API integration complete

### Social Features ✅  
- [ ] Session feed and community view
- [ ] Shaka reactions system
- [ ] User discovery and profiles
- [ ] Leaderboards and statistics

### Integration & Polish ✅
- [ ] Complete API integration
- [ ] Mobile testing and optimization
- [ ] End-to-end testing
- [ ] Launch preparation

---

## Launch Readiness

**Target**: Friends & Family Launch  
**Success Criteria**: All P0 features working end-to-end + deployed/accessible

### Definition of Ready
- Authentication flow bulletproof
- Core session logging and viewing functional
- Social features encourage engagement
- Mobile experience optimized
- Performance suitable for real usage

---

*Reference `GEMINI_CONTEXT.md` for complete technical context and backend API specifications.*