# GEMINI Frontend Development Plan

## Overview
This document provides a systematic plan for building the SLAPP frontend using Gemini, designed for collaborative development where two developers can work simultaneously on different features while maintaining integration compatibility.

## Development Principles
- **Component-First**: Build reusable components with mock data, then integrate APIs
- **Mobile-First**: Test every component on mobile using local network access
- **API-Aware**: Use Gemini's visibility into `surfdata.py` for accurate integration
- **Branch-Safe**: Each task creates isolated features to avoid merge conflicts

## Project Structure
```
/frontend/src/
├── components/          # Reusable components
│   ├── SessionTile.jsx
│   ├── SessionsList.jsx
│   ├── Navigation.jsx
│   └── ShakaModal.jsx
├── pages/              # Page components
│   ├── SessionFeed.jsx
│   ├── Journal.jsx
│   ├── SessionDetail.jsx
│   ├── SessionCreate.jsx
│   └── Auth.jsx
├── services/           # API integration
│   └── api.js
└── utils/              # Helpers and mock data
    └── mockData.js
```

---

## Phase 1: Foundation Components (Days 1-4)

### Task 1.1: SessionTile Component ⏳ IN PROGRESS
**Branch**: `feature/session-tile-component`  
**Developer**: Primary  
**Duration**: 1 day  

**Objectives**:
- Create reusable session display component
- Match mockup design (dark theme, mobile-first)
- Handle different states (own vs others, loading)
- Prepare for shaka integration

**Mock Data Format** (based on API response):
```javascript
const mockSession = {
  session_id: 1,
  session_name: "The worst day of stefano's life",
  location: "Sidewalks",
  date: "2025-07-25",
  fun_rating: 8.5,
  session_notes: "Rough paddle out to the main peak...",
  participants: [
    { display_name: "Lucia Scotti", user_id: 2 }
  ],
  shakas: {
    total_count: 7,
    viewer_has_shakaed: false,
    preview_users: [
      { display_name: "Martin Dietz", user_id: 1 }
    ]
  }
}
```

**Deliverables**:
- [ ] SessionTile component with props interface
- [ ] Responsive styling (dark theme)
- [ ] Click handler preparation for shaka button
- [ ] Loading and error states
- [ ] Mobile testing confirmed

**Definition of Done**:
- Component renders correctly with mock data
- Styling matches mockups on mobile and desktop
- Props interface documented
- Ready for SessionsList integration

---

### Task 1.2: Navigation & Layout System
**Branch**: `feature/navigation-layout`  
**Developer**: Secondary (Parallel to 1.1)  
**Duration**: 1 day  

**Objectives**:
- Create app shell with bottom navigation
- Implement routing structure
- Add header with user profile dropdown
- Dark theme layout foundation

**Components to Build**:
- `Navigation.jsx` - Bottom nav bar
- `Layout.jsx` - App shell wrapper  
- `Header.jsx` - Top header with profile

**Routes Structure**:
```javascript
/session-feed     → SessionFeed page
/create-session   → SessionCreate page  
/my-journal       → Journal page (current user)
/journal/:userId  → Journal page (any user)
/session/:id      → SessionDetail page
/login           → Auth page
/signup          → Auth page
```

**Deliverables**:
- [ ] Bottom navigation component
- [ ] React Router setup with all routes
- [ ] Layout wrapper component
- [ ] Header with profile dropdown
- [ ] Dark theme CSS variables
- [ ] Mobile navigation testing

**Definition of Done**:
- Navigation works between all main sections
- Layout responsive on mobile
- Routing structure complete
- Ready for page components

---

### Task 1.3: SessionsList Component
**Branch**: `feature/sessions-list-component`  
**Developer**: Primary (After 1.1)  
**Duration**: 1 day  

**Objectives**:
- Create reusable list component using SessionTile
- Group sessions by month (per mockups)
- Handle loading and empty states
- Prepare for filtering integration

**Mock Data Format**:
```javascript
const mockSessionsList = [
  {
    month: "August 2025",
    sessions: [mockSession1, mockSession2, ...]
  },
  {
    month: "July 2025", 
    sessions: [mockSession3, mockSession4, ...]
  }
]
```

**Deliverables**:
- [ ] SessionsList component using SessionTile
- [ ] Month grouping logic
- [ ] Loading skeleton UI
- [ ] Empty state handling
- [ ] Infinite scroll preparation
- [ ] Filter integration hooks

**Definition of Done**:
- Component renders grouped sessions correctly
- Integrates seamlessly with SessionTile
- Loading and empty states work
- Ready for page integration

---

### Task 1.4: API Service Foundation
**Branch**: `feature/api-service`  
**Developer**: Secondary (After 1.2)  
**Duration**: 1 day  

**Objectives**:
- Create centralized API service
- Implement authentication token management
- Set up error handling patterns
- Verify endpoints against surfdata.py

**API Service Structure**:
```javascript
// services/api.js
class ApiService {
  constructor() {
    this.baseURL = 'https://surfdata-k6is0yvy7-martins-projects-383d438b.vercel.app'
    this.token = localStorage.getItem('access_token')
  }
  
  // Auth methods
  async login(email, password)
  async signup(firstName, lastName, email, password)
  
  // Session methods  
  async getSessions(view = 'feed')
  async getUserSessions(userId, view = 'profile')
  async createSession(sessionData)
  async updateSession(sessionId, sessionData)
  async deleteSession(sessionId)
  
  // Social methods
  async toggleShaka(sessionId)
  async searchUsers(query)
  
  // Data methods
  async getSpotsByRegion()
  async getDashboard()
}
```

**Deliverables**:
- [ ] Complete API service class
- [ ] Token management (store, refresh, clear)
- [ ] Error handling wrapper
- [ ] Response format validation
- [ ] Environment configuration

**Definition of Done**:
- API service handles all required endpoints
- Authentication flow working
- Error handling consistent
- Ready for component integration

---

## Phase 2: Core Pages (Days 5-8)

### Task 2.1: Authentication Pages
**Branch**: `feature/auth-pages`  
**Developer**: Primary  
**Duration**: 1 day  

**Objectives**:
- Build login/signup pages matching mockups
- Integrate with API service
- Implement form validation
- Handle authentication flow

**Components**:
- Login form (email, password)
- Signup form (first_name, last_name, email, password)
- Form validation and error display
- Loading states during auth

**Deliverables**:
- [ ] Login page component
- [ ] Signup page component  
- [ ] Form validation logic
- [ ] API integration with error handling
- [ ] Token persistence
- [ ] Redirect after auth

**Definition of Done**:
- Users can signup/login successfully
- Tokens persist across sessions
- Form validation working
- Error states handled gracefully

---

### Task 2.2: Session Feed Page
**Branch**: `feature/session-feed-page`  
**Developer**: Secondary (Parallel to 2.1)  
**Duration**: 1 day  

**Objectives**:
- Build main session feed using SessionsList
- Add Feed/Leaderboard toggle
- Integrate with sessions API
- Handle loading and error states

**Features**:
- Feed tab: All friends' sessions grouped by month
- Leaderboard tab: Community stats and rankings  
- Pull-to-refresh functionality
- Infinite scroll for older sessions

**API Integration**:
- `GET /api/surf-sessions?view=feed` for lightweight session data
- `GET /api/dashboard` for leaderboard data

**Deliverables**:
- [ ] SessionFeed page component
- [ ] Feed/Leaderboard tab switching
- [ ] API integration with loading states
- [ ] Pull-to-refresh functionality
- [ ] Error handling and retry logic

**Definition of Done**:
- Feed displays all friends' sessions
- Leaderboard shows community stats
- Performance good on mobile
- Error states handled

---

### Task 2.3: Journal Page
**Branch**: `feature/journal-page`  
**Developer**: Primary (After 2.1)  
**Duration**: 1 day  

**Objectives**:
- Build flexible journal page for any user
- Add Log/My Stats tab switching
- Integrate filtering functionality
- Handle current user vs other user contexts

**Features**:
- Log tab: User's sessions with SessionsList
- My Stats tab: User statistics cards
- Filter by region, swell height, period, direction
- Support for viewing any user's journal

**API Integration**:
- `GET /api/users/{userId}/sessions?view=profile` for session data
- `GET /api/dashboard` for user stats

**Deliverables**:
- [ ] Journal page component
- [ ] Log/My Stats tab functionality
- [ ] Filter controls and logic
- [ ] User context handling (me vs others)
- [ ] Stats cards display
- [ ] API integration with caching

**Definition of Done**:
- Journal works for any user
- Filtering functions correctly
- Stats display accurately
- Good performance with large session lists

---

### Task 2.4: Session Detail Page
**Branch**: `feature/session-detail-page`  
**Developer**: Secondary (After 2.2)  
**Duration**: 1 day  

**Objectives**:
- Build detailed session view
- Display complete surf conditions
- Integrate shaka reactions
- Add edit/delete for session owners

**Features**:
- Full session information display
- Surf conditions (swell, wind, tide, temperature)
- Participant list with user links
- Shaka reactions with user modal
- Edit/delete buttons for owners
- Back navigation

**API Integration**:
- `GET /api/surf-sessions/{id}` for full session data
- `POST /api/surf-sessions/{id}/shaka` for reactions
- `PUT /api/surf-sessions/{id}` for edits
- `DELETE /api/surf-sessions/{id}` for deletion

**Deliverables**:
- [ ] SessionDetail page component
- [ ] Surf conditions display
- [ ] Shaka reactions integration
- [ ] Edit/delete functionality
- [ ] User permissions handling
- [ ] Navigation and routing

**Definition of Done**:
- Complete session information displayed
- Shaka reactions working
- Edit/delete works for owners
- Mobile layout optimized

---

## Phase 3: Advanced Features (Days 9-12)

### Task 3.1: Session Creation Page
**Branch**: `feature/session-create-page`  
**Developer**: Primary  
**Duration**: 1 day  

**Objectives**:
- Build session creation form
- Integrate location selection by region
- Add user tagging functionality
- Handle form validation and submission

**Features**:
- All form fields (date, location, title, times, rating, notes)
- Regional location dropdown
- User search and tagging
- Form validation
- Preview before submission

**API Integration**:
- `GET /api/surf-spots-by-region` for locations
- `GET /api/users/search` for user tagging
- `POST /api/surf-sessions` for session creation

**Deliverables**:
- [ ] SessionCreate page component
- [ ] Location selection with regional grouping
- [ ] User search and tagging interface
- [ ] Form validation logic
- [ ] API integration and error handling
- [ ] Success feedback and navigation

**Definition of Done**:
- Form creates sessions successfully
- User tagging works correctly
- Location selection intuitive
- Validation prevents invalid submissions

---

### Task 3.2: Shaka Reactions Modal
**Branch**: `feature/shaka-modal`  
**Developer**: Secondary (Parallel to 3.1)  
**Duration**: 1 day  

**Objectives**:
- Build modal showing users who reacted
- Integrate with existing shaka data
- Handle loading and error states
- Style to match app theme

**Features**:
- Modal triggered by shaka count click
- List of users who gave shakas
- User profile links
- Loading states while fetching
- Close/dismiss functionality

**API Integration**:
- Use existing shaka data from session responses
- Potential `GET /api/surf-sessions/{id}/shakas` for full list

**Deliverables**:
- [ ] ShakaModal component
- [ ] User list display
- [ ] Loading and error states
- [ ] Modal open/close logic
- [ ] Integration with SessionTile
- [ ] Responsive design

**Definition of Done**:
- Modal shows complete user list
- Integrates with all session views
- Performance good on mobile
- Accessible modal behavior

---

### Task 3.3: Session Edit Functionality
**Branch**: `feature/session-edit`  
**Developer**: Primary (After 3.1)  
**Duration**: 1 day  

**Objectives**:
- Build session editing capability
- Reuse session creation components
- Handle data pre-population
- Manage participant updates

**Features**:
- Edit form with pre-populated data
- Participant modification
- Validation and error handling
- Save changes functionality
- Cancel/discard changes

**API Integration**:
- `GET /api/surf-sessions/{id}` for current data
- `PUT /api/surf-sessions/{id}` for updates

**Deliverables**:
- [ ] SessionEdit page component
- [ ] Form pre-population logic
- [ ] Participant management
- [ ] Change tracking and validation
- [ ] API integration
- [ ] Navigation and confirmation

**Definition of Done**:
- Session owners can edit successfully
- Participant changes handled correctly
- Validation prevents invalid updates
- Good UX for editing flow

---

### Task 3.4: Leaderboard Component
**Branch**: `feature/leaderboard`  
**Developer**: Secondary (After 3.2)  
**Duration**: 1 day  

**Objectives**:
- Build leaderboard display
- Add tab switching (Sessions, Surf Time, Fun Rating)
- Handle year selection
- Style as rankings table

**Features**:
- Three leaderboard types with tab switching
- Year selector functionality
- Rankings with user profiles
- Current user highlighting
- Responsive table design

**API Integration**:
- `GET /api/dashboard` for community stats and rankings

**Deliverables**:
- [ ] Leaderboard page component
- [ ] Tab switching functionality
- [ ] Year selection logic
- [ ] Rankings table display
- [ ] User highlighting
- [ ] Mobile responsive design

**Definition of Done**:
- All three leaderboard types working
- Year selection updates data
- Current user highlighted
- Mobile table layout optimized

---

## Phase 4: Integration & Polish (Days 13-16)

### Task 4.1: Complete API Integration
**Branch**: `feature/api-integration-completion`  
**Developer**: Both (Code Review Focus)  
**Duration**: 2 days  

**Objectives**:
- Ensure all components use real API data
- Implement comprehensive error handling
- Add loading states throughout
- Test authentication guards

**Integration Points**:
- Replace all mock data with API calls
- Unified error handling strategy
- Loading state standardization
- Authentication flow testing
- API response validation

**Deliverables**:
- [ ] All mock data replaced with API calls
- [ ] Consistent error handling patterns
- [ ] Loading states on all async operations
- [ ] Authentication guards on protected routes
- [ ] API response validation
- [ ] Error boundary components

**Definition of Done**:
- No mock data remaining in production
- All API errors handled gracefully
- Loading states provide good UX
- Authentication flow bulletproof

---

### Task 4.2: Mobile Testing & Optimization
**Branch**: `feature/mobile-optimization`  
**Developer**: Both  
**Duration**: 1 day  

**Objectives**:
- Test all features on mobile devices
- Optimize touch interactions
- Ensure responsive design works
- Performance optimization

**Testing Areas**:
- Navigation and routing on mobile
- Form interactions and validation
- Modal behavior and sizing
- Touch targets and gestures
- Performance on slower connections

**Deliverables**:
- [ ] All features tested on mobile
- [ ] Touch interactions optimized
- [ ] Responsive design validated
- [ ] Performance issues addressed
- [ ] Cross-browser mobile testing
- [ ] Accessibility improvements

**Definition of Done**:
- App fully functional on mobile
- Good performance on mobile devices
- Touch interactions feel native
- Accessibility standards met

---

### Task 4.3: End-to-End Testing
**Branch**: `feature/e2e-testing`  
**Developer**: Both  
**Duration**: 1 day  

**Objectives**:
- Test complete user journeys
- Verify all integrations work together
- Load testing with real data
- Edge case handling

**User Journeys to Test**:
1. Signup → Session creation → Feed viewing
2. Login → Journal viewing → Session detail
3. Session creation with tagging → Reactions
4. User search → Friend journal viewing
5. Leaderboard viewing → Profile navigation

**Deliverables**:
- [ ] All user journeys tested
- [ ] Integration issues resolved
- [ ] Edge cases handled
- [ ] Performance validated
- [ ] Bug fixes implemented
- [ ] User feedback incorporated

**Definition of Done**:
- All P0 features work together
- No blocking bugs remain
- Performance meets standards
- Ready for friends & family launch

---

## Development Guidelines

### Branch Naming Convention
```
feature/component-name      # For reusable components
feature/page-name          # For page components  
feature/integration-name   # For API/service work
bugfix/issue-description   # For bug fixes
```

### Testing Checklist (Each Task)
- [ ] Component renders without errors
- [ ] Props interface documented
- [ ] Mobile responsive design confirmed
- [ ] Loading and error states handled
- [ ] API integration tested (if applicable)
- [ ] Code reviewed by partner
- [ ] Branch merged without conflicts

### Mobile Testing Protocol
1. Start local dev server: `npm run dev`
2. Access via network URL: `http://192.168.1.XXX:5173`
3. Test on actual mobile device
4. Verify touch interactions
5. Check responsive breakpoints
6. Test form interactions

### API Integration Pattern
```javascript
// Standard pattern for API integration
const [data, setData] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);

useEffect(() => {
  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await apiService.getData();
      setData(response.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  fetchData();
}, []);
```

---

## Progress Tracking

### Completed Tasks ✅
- [ ] 1.1: SessionTile Component
- [ ] 1.2: Navigation & Layout System  
- [ ] 1.3: SessionsList Component
- [ ] 1.4: API Service Foundation
- [ ] 2.1: Authentication Pages
- [ ] 2.2: Session Feed Page
- [ ] 2.3: Journal Page
- [ ] 2.4: Session Detail Page
- [ ] 3.1: Session Creation Page
- [ ] 3.2: Shaka Reactions Modal
- [ ] 3.3: Session Edit Functionality
- [ ] 3.4: Leaderboard Component
- [ ] 4.1: Complete API Integration
- [ ] 4.2: Mobile Testing & Optimization
- [ ] 4.3: End-to-End Testing

### Current Focus
**Active Task**: 1.1 SessionTile Component  
**Next Up**: 1.2 Navigation & Layout System (Parallel)  
**Blocking Issues**: None  

### Launch Readiness
**Target Date**: August 9, 2025  
**P0 Features Complete**: 0/16  
**Deployment Ready**: ❌  

---

## Notes & Decisions

### Architecture Decisions
- **State Management**: Using React built-in state (useState, useContext) for MVP
- **Routing**: React Router for navigation
- **Styling**: Tailwind CSS for consistent design
- **API**: Centralized service class for backend communication

### Known Challenges
- **Authentication Flow**: Using Gemini's visibility into surfdata.py to avoid v0 auth issues
- **Real-time Updates**: Not implemented in MVP, future consideration
- **Offline Support**: Not implemented in MVP, future consideration

### Future Considerations
- Progressive Web App (PWA) features
- Push notifications for new sessions/reactions
- Advanced filtering and search
- Photo uploads for sessions
- Real-time collaboration features

---

*Last Updated: [Current Date] - Task 1.1 Ready to Begin*