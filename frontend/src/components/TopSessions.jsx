import React from 'react';
import { Link } from 'react-router-dom';

function TopSessions({ sessions }) {
  if (!sessions || sessions.length === 0) {
    return null; // Don't render anything if there are no top sessions
  }

  // Helper to format date
  const formatDate = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  // Helper to format stoke rating
  const formatStokeRating = (stoke) => {
    // Check if it's an integer (e.g., 5.0, 6.0)
    if (stoke % 1 === 0) {
      return Math.floor(stoke).toString(); // Return as integer string "5"
    }
    
    // Otherwise, ensure two decimal places if needed, but remove trailing zero for .50
    const formatted = stoke.toFixed(2); // e.g., "5.25", "5.50", "5.75"
    if (formatted.endsWith('0')) { // If it ends with a zero, like "5.50"
      return formatted.slice(0, -1); // Remove the last '0', resulting in "5.5"
    }
    return formatted; // For "5.25", "5.75"
  };

  return (
    <div className="mt-8">
      <h3 className="text-xl font-bold text-gray-800 mb-4 text-center">Top Sessions</h3>
      <ul className="space-y-3">
        {sessions.map((session) => (
          <li key={session.id} className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
            <Link to={`/session/${session.id}`} className="flex items-center justify-between p-3">
              <div className="flex-grow">
                <p className="font-semibold text-gray-900">{session.title || 'Untitled Session'}</p>
                <p className="text-sm text-gray-500">{session.spot} - {formatDate(session.date)}</p>
                {session.session_notes && (
                  <p className="text-xs text-gray-600 mt-1 line-clamp-1">
                    {session.session_notes}
                  </p>
                )}
              </div>
              <div className="flex items-center space-x-1 text-gray-900">
                <span className="font-bold text-lg">{formatStokeRating(session.stoke)}</span>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default TopSessions;
