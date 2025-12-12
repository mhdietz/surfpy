import React from 'react';
import { Link } from 'react-router-dom';
import { StarIcon } from '@heroicons/react/20/solid'; // Using Heroicons for a nice touch

function TopSessions({ sessions }) {
  if (!sessions || sessions.length === 0) {
    return null; // Don't render anything if there are no top sessions
  }

  // Helper to format date
  const formatDate = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="mt-8">
      <h3 className="text-xl font-bold text-gray-800 mb-4 text-center">Top Stoke Sessions</h3>
      <ul className="space-y-3">
        {sessions.map((session) => (
          <li key={session.id} className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
            <Link to={`/session/${session.id}`} className="flex items-center justify-between p-3">
              <div className="flex-grow">
                <p className="font-semibold text-gray-900">{session.title || 'Untitled Session'}</p>
                <p className="text-sm text-gray-500">{session.spot} - {formatDate(session.date)}</p>
              </div>
              <div className="flex items-center space-x-1 text-yellow-500">
                <StarIcon className="h-5 w-5" />
                <span className="font-bold text-lg">{session.stoke.toFixed(1)}</span>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default TopSessions;
