import React from 'react';
import { CalendarIcon, MapPinIcon } from '@heroicons/react/24/solid';
import Logo from './UI/Logo';

function ShareableYearInReview({ stats, selectedYear, profileDisplayName }) {
  if (!stats || !stats.top_sessions || !stats.top_sessions.length === 0) {
    return null;
  }

  const topSession = stats.top_sessions[0];

  const formatDate = (isoString) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric' });
  };

  return (
    <div
      id="shareable-card"
      className="fixed -top-[9999px] -left-[9999px] z-[-1] p-14 flex flex-col bg-white text-gray-800"
      style={{
        width: '1080px',
        height: '1080px',
        fontFamily: 'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      }}
    >
      {/* Header */}
      <div className="text-center">
        <div className="flex flex-col items-center">
          <Logo className="h-20 w-20 text-blue-600" />
          <h1 className="text-6xl font-bold text-blue-600 tracking-tighter -mt-2">slapp</h1>
        </div>
        <p className="text-3xl font-semibold text-gray-600 mt-8">
          {profileDisplayName}'s {selectedYear} Year In Review
        </p>
      </div>

      {/* Main Stats */}
      <div className="grid grid-cols-3 gap-10 text-center w-full my-auto">
        <div>
          <h3 className="text-3xl font-semibold text-gray-500">Total Sessions</h3>
          <p className="text-7xl font-bold text-blue-500 mt-1">{stats.total_sessions || 0}</p>
        </div>
        <div>
          <h3 className="text-3xl font-semibold text-gray-500">Total Time</h3>
          <p className="text-7xl font-bold text-green-500 mt-1">{stats.total_hours ? stats.total_hours.toFixed(0) : 0}<span className="text-4xl ml-2">hrs</span></p>
        </div>
        <div>
          <h3 className="text-3xl font-semibold text-gray-500">Average Stoke</h3>
          <p className="text-7xl font-bold text-yellow-500 mt-1">{stats.average_stoke ? stats.average_stoke.toFixed(1) : 'N/A'}</p>
        </div>
        </div>

      {/* Top Session */}
      <div className="bg-gray-50 rounded-3xl p-8 border border-gray-200">
        <h3 className="text-3xl font-bold text-center mb-6">Top Session</h3>
        <div className="flex flex-col space-y-5"> {/* Increased spacing */}
          <div className="flex justify-between items-center"> {/* Use items-center */}
            <p className="text-4xl font-bold leading-tight">{topSession.title}</p> {/* Add leading-tight */}
            <div className="flex flex-col items-center flex-shrink-0 ml-4">
              <p className="text-5xl font-extrabold text-yellow-500">{topSession.stoke.toFixed(1)}</p>
              <p className="text-2xl font-semibold text-gray-600 -mt-1">Stoke</p>
            </div>
          </div>
          <div className="flex flex-col space-y-3 text-2xl text-gray-500 pt-2"> {/* Stack location/date */}
            <div className="flex items-center">
              <MapPinIcon className="h-7 w-7 mr-3 text-gray-400 flex-shrink-0" />
              <span>{topSession.spot}</span>
            </div>
            <div className="flex items-center">
              <CalendarIcon className="h-7 w-7 mr-3 text-gray-400 flex-shrink-0" />
              <span>{formatDate(topSession.date)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center text-3xl text-gray-400 font-semibold mt-auto pt-4">
        slappit.vercel.app
      </div>
    </div>
  );
}

export default ShareableYearInReview;
