# My Stats Enhancement - Year in Review Feature

## Overview
Enhance the existing "My Stats" page to provide comprehensive annual summaries with year filtering and shareable image generation. Position as "Year in Review" through marketing (email + notification) without creating a separate "Wrapped" feature.

## Product Requirements

### Core Functionality
- Extend existing My Stats page at `/journal/me?tab=stats`
- Add year filter dropdown (defaults to current year: 2025)
- Add detailed annual statistics and visualizations
- Generate shareable 1080x1080px image for social media
- Send in-app notification in December to announce feature

### Key Principles
- Show full stats for ANY number of sessions (no empty state variations)
- Only exception: 0 sessions gets encouragement message with CTA to log first session
- Stats are always available year-round (not a temporary December feature)
- Marketing (email + notification) creates the "Year in Review" moment

## Current State

### Existing My Stats Page
- Location: `/journal/me?tab=stats`
- Has tabs: [My Surf Log] [My Stats]
- Currently shows 3 stats:
  - Total Sessions
  - Total Surf Time (hours)
  - Average Fun (stoke rating)

### What to Add
Below the existing 3-stat cards:
1. Year Filter Dropdown
2. Top 3 Sessions
3. Sessions by Month Chart (bar chart)
4. Average Stoke by Month Chart (line chart)
5. Most Frequent Surf Buddy
6. Share Button (generates image)

## Enhanced Layout
```
[My Surf Log]  [My Stats] ← active tab

Year: [2025 ▾] [2024] [2023]

┌─────────┐  ┌─────────┐  ┌─────────┐
│   27    │  │  39.8   │  │  7.59   │
│sessions │  │  hours  │  │avg stoke│
└─────────┘  └─────────┘  └─────────┘

🏆 Your Top Sessions
┌─────────────────────────────────┐
│ #1  9.5/10                      │
│ "Epic Dawn Patrol"              │
│ Steamer Lane • Aug 15           │
└─────────────────────────────────┘
[Session #2]
[Session #3]

📅 Sessions by Month
[Bar chart: X-axis = Jan-Dec, Y-axis = session count]

🤙 Average Stoke by Month  
[Line chart: X-axis = months with sessions, Y-axis = 0-10 stoke]

👥 Most Frequent Surf Buddy
Frank Kapp (15 sessions together)

[📸 Share My 2025 Year in Review]
```

## API Specification

### Endpoint
```
GET /api/users/me/stats?year=2025
```

### Response
```json
{
  "year": 2025,
  "total_sessions": 27,
  "total_hours": 39.8,
  "average_stoke": 7.59,
  "top_sessions": [
    {
      "id": 123,
      "title": "Epic Dawn Patrol",
      "spot": "Steamer Lane",
      "date": "2025-08-15",
      "stoke": 9.5
    },
    // 2 more sessions
  ],
  "sessions_by_month": [
    {"month": "Jan", "count": 2},
    {"month": "Feb", "count": 4},
    // All 12 months, 0 for empty months
  ],
  "stoke_by_month": [
    {"month": "Jan", "avg_stoke": 6.5},
    {"month": "Feb", "avg_stoke": 7.0},
    // Only months with sessions
  ],
  "most_frequent_buddy": {
    "name": "Frank Kapp",
    "count": 15
  }
}
```

### Backend Logic
- Query surf_sessions table filtered by user_id and year date range
- Calculate totals, averages, and aggregations
- Top 3 sessions: ORDER BY fun_rating DESC, date DESC LIMIT 3
- Sessions by month: Fill all 12 months, set count=0 for empty months
- Stoke by month: Only include months with sessions
- Most frequent buddy: JOIN session_participants, GROUP BY display_name, ORDER BY count DESC LIMIT 1

## Frontend Implementation

### Component Structure
- Extend existing StatsDisplay component (or equivalent)
- Add year filter buttons at top (2025, 2024, 2023)
- Fetch data on mount and when year changes
- Use Recharts for bar and line charts
- Use html2canvas for image generation

### Dependencies
```bash
npm install html2canvas
```

### Shareable Image Specifications
- Size: 1080x1080px (Instagram square)
- Format: PNG
- Background: Gradient (blue to purple, ocean vibes)
- Content includes:
  - Slapp logo and branding
  - User's name + year
  - Total sessions
  - Total hours
  - Average stoke
  - Best session (title + stoke)
  - Most frequent surf buddy (if exists)
  - "slappit.vercel.app" footer

### Image Generation
- Hidden div positioned off-screen (left: -9999px)
- Styled as 1080x1080px card
- Button triggers html2canvas conversion
- Downloads as PNG file

## Notification Implementation

### Notification Type
New type: `'year_in_review'`

### When to Create
December 1st, 2025 - create notification for all users who have 2025 sessions

### Notification Content
- Message: "🎉 Your 2025 Year in Review is Ready!"
- Subtext: "See your year of surfing in My Stats"
- Action: Click navigates to `/journal/me?tab=stats`
- Mark as read when clicked

### Backend Function
Create `create_year_in_review_notifications()` function:
- Query all users with sessions in 2025
- Insert notification row for each user
- Type: 'year_in_review', session_id: NULL, actor_id: NULL

### Frontend Display
In NotificationsPage component:
- Handle 'year_in_review' type
- Display special card with blue background
- Button: "View My Stats" → navigates to stats page

## Year Filter Behavior

### Available Years
Show buttons for: 2025, 2024, 2023 (adjust based on app age)

### Default Year
Current year (2025)

### No "All Time" Option
Not included in MVP - can add later

### URL Parameters
Support `?year=2025` query parameter for direct linking

## Empty State (0 Sessions)

When user has 0 sessions in selected year:
```
You haven't logged any sessions in 2025.

Start logging to build your stats!

[Log Your First Session] → /sessions/create
```

## Testing Checklist

### Backend
- [ ] Endpoint returns correct data structure
- [ ] Year filtering works correctly
- [ ] Handles 0 sessions gracefully
- [ ] Sessions by month includes all 12 months
- [ ] Stoke by month only includes months with data
- [ ] Top sessions ordered correctly
- [ ] Buddy calculation is accurate

### Frontend
- [ ] Year filter buttons work
- [ ] Data updates when year changes
- [ ] Charts render correctly
- [ ] Top sessions clickable to detail page
- [ ] Share button generates 1080x1080 image
- [ ] Image includes all required content
- [ ] Mobile responsive
- [ ] Empty state displays for 0 sessions

### Notification
- [ ] Notification created for eligible users
- [ ] Displays in notifications page
- [ ] Clicking navigates to stats
- [ ] Marks as read after clicking

## Production Details

- URL: https://slappit.vercel.app/journal/me?tab=stats
- Backend: Flask API (surfdata.py, database_utils.py)
- Frontend: React (extend existing StatsDisplay component)
- Database: PostgreSQL (Supabase) - no schema changes needed
- Tables: surf_sessions, session_participants, auth.users, notifications

## Estimated Effort
- Backend: 1 day
- Frontend: 2 days  
- Notification: 0.5 day
- Testing: 0.5 day
- **Total: 4 days**