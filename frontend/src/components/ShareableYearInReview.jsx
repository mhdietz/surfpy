import React from 'react';
import { CalendarIcon, MapPinIcon } from '@heroicons/react/24/solid';
import Logo from './UI/Logo';

function ShareableYearInReview({ stats, selectedYear, profileDisplayName }) {
  if (!stats || !stats.top_sessions || !stats.top_sessions.length === 0) {
    return null;
  }

  const formatDate = (isoString) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric' });
  };

  return (
    <div
      id="shareable-card"
      className="fixed -top-[9999px] -left-[9999px] z-[-1] p-10 flex flex-col bg-white text-gray-800 relative"
      style={{
        width: '1080px',
        height: '1080px',
        fontFamily: 'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      }}
    >
      {/* Corner Logo */}
      <div className="absolute top-10 left-10">
        <Logo className="h-12 w-12 text-blue-600" />
      </div>

      {/* Main Title */}
      <div className="text-center mt-4 mb-8"> {/* Adjusted mt for spacing after corner logo */}
        <p className="text-4xl font-semibold text-gray-600 tracking-wide">
          {profileDisplayName}'s {selectedYear} Year In Review
        </p>
      </div>

      {/* Main Stats */}
      <div className="grid grid-cols-3 gap-10 text-center w-full mb-8">
        <div>
          <h3 className="text-3xl font-semibold text-gray-500">Total Sessions</h3>
          <p className="text-7xl font-bold text-gray-900 mt-1">{stats.total_sessions || 0}</p>
        </div>
        <div>
          <h3 className="text-3xl font-semibold text-gray-500">Total Time</h3>
          <p className="text-7xl font-bold text-gray-900 mt-1">{stats.total_hours ? stats.total_hours.toFixed(0) : 0}<span className="text-4xl ml-2">hrs</span></p>
        </div>
        <div>
          <h3 className="text-3xl font-semibold text-gray-500">Average Stoke</h3>
          <p className="text-7xl font-bold text-gray-900 mt-1">{stats.average_stoke ? stats.average_stoke.toFixed(1) : 'N/A'}</p>
        </div>
        </div>

      {/* Top Surf Spots */}
      {stats.top_locations && stats.top_locations.length > 0 && (
        <div className="rounded-3xl p-8 pt-0 mt-8"> {/* Adjusted padding and added mt-8 */}
          <h3 className="text-3xl font-bold text-center mb-6">Top Surf Spots</h3>
          <ul className="space-y-4">
            {stats.top_locations.map((spot, index) => (
              <li key={index}>
                <div className="flex justify-between items-center">
                  <div className="flex-grow flex items-center">
                    <MapPinIcon className="h-7 w-7 text-gray-400 mr-3 flex-shrink-0" /> {/* Larger icon */}
                    <div>
                      <p className="text-2xl font-semibold text-gray-900">{spot.name}</p>
                      {spot.region && <p className="text-xl text-gray-500">{spot.region}</p>}
                    </div>
                  </div>
                  <div className="flex-shrink-0 ml-4 text-right">
                    <span className="text-3xl font-bold text-gray-900">{spot.session_count}</span>
                    <p className="text-xl text-gray-600">Sessions</p>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Top Sessions */}
      <div className="rounded-3xl p-8">
        <h3 className="text-3xl font-bold text-center mb-6">Top Sessions</h3>
        <ul className="space-y-4">
          {stats.top_sessions.map((session) => (
            <li key={session.id} className="border-b border-gray-200 pb-4 last:border-b-0">
              <div className="flex justify-between items-start">
                <div className="flex-grow">
                  <p className="text-2xl font-bold">{session.title}</p>
                  <p className="text-xl text-gray-500 mt-1">{session.spot} - {formatDate(session.date)}</p>
                </div>
                <div className="flex-shrink-0 ml-4 text-center">
                  <p className="text-3xl font-extrabold text-gray-900">{session.stoke.toFixed(1)}</p>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {/* Footer */}
      <div className="text-center text-3xl text-gray-400 font-semibold mt-auto pt-4">
        slappit.vercel.app
      </div>
    </div>
  );
}

export default ShareableYearInReview;
