import React from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Card from '../components/UI/Card';
import { format } from 'date-fns';

// Mock data based on the more detailed "Rockaways" example
const mockSession = {
  "id": 3669,
  "session_name": "Making a session with this new thang",
  "location": "Rockaways",
  "fun_rating": "3",
  "session_started_at": "2025-08-11T22:10:00+00:00",
  "session_ended_at": "2025-08-12T00:10:00+00:00",
  "display_name": "Stefano Scotti",
  "participants": [
    { "display_name": "Stefano Scotti", "user_id": "5e6e32b1-3059-4ac4-b819-02f175c32ed3" },
    { "display_name": "Martin Dietz", "user_id": "81cdb75c-559b-413e-8672-8856ca435373" }
  ],
  "shakas": {
    "count": 5,
    "preview": [
        { "display_name": "Martin Dietz" },
        { "display_name": "John Doe" }
    ],
    "viewer_has_shakaed": true
  },
  "session_notes": "Extra tasty"
};

const SessionDetail = () => {
  const { id } = useParams();
  const { isAuthenticated } = useAuth();

  // For now, we'll just use the mock data.
  // In later steps, we'll introduce loading and error states.
  const session = mockSession;

  if (!isAuthenticated) {
    return (
      <div className="text-center p-4 text-red-500">
        You must be logged in to view session details.
      </div>
    );
  }

  // Helper to format date and time
  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return format(date, "EEE, MMM d, yyyy 'at' h:mm a");
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <Card>
        <div className="p-4">
          <h1 className="text-3xl font-bold mb-2">{session.session_name}</h1>
          <p className="text-lg text-gray-400 mb-4">{session.location}</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4 text-center">
            <div className="bg-gray-800 p-3 rounded-lg">
              <p className="text-sm text-gray-400">Started</p>
              <p className="font-semibold">{formatDateTime(session.session_started_at)}</p>
            </div>
            <div className="bg-gray-800 p-3 rounded-lg">
              <p className="text-sm text-gray-400">Ended</p>
              <p className="font-semibold">{formatDateTime(session.session_ended_at)}</p>
            </div>
          </div>

          <div className="flex justify-between items-center mb-6">
            <div>
              <span className="text-2xl font-bold text-yellow-400">{session.fun_rating}</span>
              <span className="text-gray-400">/10 Fun Rating</span>
            </div>
            <div>
              <span className="text-2xl">🤙</span>
              <span className="font-bold ml-2">{session.shakas.count} Shakas</span>
            </div>
          </div>

          <div className="mb-4">
            <h2 className="text-xl font-bold mb-2">Surfers</h2>
            <div className="flex flex-wrap gap-2">
              {session.participants.map(p => (
                <span key={p.user_id} className="bg-gray-700 px-3 py-1 rounded-full text-sm">
                  {p.display_name}
                </span>
              ))}
            </div>
          </div>
          
          {session.session_notes && (
            <div>
              <h2 className="text-xl font-bold mb-2">Notes</h2>
              <p className="text-gray-300 bg-gray-800 p-3 rounded-lg">{session.session_notes}</p>
            </div>
          )}

        </div>
      </Card>
    </div>
  );
};

export default SessionDetail;