// This file contains mock data for frontend component development.
// It allows for building and testing components in isolation
// without requiring a running backend.

export const mockSession = {
  id: 123,
  session_name: "Fun morning waves",
  location: "Ocean Beach",
  fun_rating: 5,
  session_notes: "A few fun ones on the inside bar. A bit crowded but managed to find a few corners.",
  session_started_at: "2025-08-15T10:00:00Z",
  user_id: "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  display_name: "John Doe",
  participants: [
    { user_id: "b2c3d4e5-f6a7-8901-2345-67890abcdef1", display_name: "Lucia" }
  ],
  shakas: {
    count: 5,
    viewer_has_shakaed: false,
    preview: [
        { user_id: "c3d4e5f6-a7b8-9012-3456-7890abcdef12", display_name: "Sam Jones" }
    ]
  }
};
