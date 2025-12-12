import React from 'react';
import Spinner from './UI/Spinner';
// import Card from './UI/Card'; // Card is imported but not used, will remove it

// Accept new props: selectedYear, setSelectedYear
function StatsDisplay({ stats, loading, error, selectedYear, setSelectedYear }) {
  if (loading) {
    return <Spinner />;
  }

  if (error) {
    return <div className="text-red-500 text-center p-4">Error: {error}</div>;
  }

  // Generate years for filter (e.g., from 2023 to current year)
  const currentYear = new Date().getFullYear();
  const years = [];
  for (let y = 2023; y <= currentYear; y++) {
    years.push(y);
  }
  years.sort((a, b) => b - a); // Sort descending

  // Check if stats are available AND if they indicate no sessions for the selected year
  // The backend now returns { total_sessions: 0, ... } for no sessions
  const hasNoSessions = stats && stats.total_sessions === 0;

  // Render a specific message if no sessions for the selected year
  if (hasNoSessions) {
    return (
      <div className="p-4">
        {/* Year Filter UI */}
        <div className="flex justify-center space-x-2 mb-6">
          {years.map((year) => (
            <button
              key={year}
              onClick={() => setSelectedYear(year)}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                selectedYear === year
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {year}
            </button>
          ))}
        </div>
        <div className="text-center p-4 text-gray-600">
          <p className="text-lg mb-2">You haven't logged any sessions in {selectedYear}.</p>
          <p className="mb-4">Start logging to build your stats!</p>
          <a href="/sessions/create" className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-lg transition duration-200">
            Log Your First Session
          </a>
        </div>
      </div>
    );
  }

  // If no stats at all (e.g., first load and nothing came back, or API error handled above),
  // but not necessarily `total_sessions: 0`. This is a fallback if `stats` is null/undefined
  if (!stats) {
    return (
      <div className="p-4">
        {/* Year Filter UI */}
        <div className="flex justify-center space-x-2 mb-6">
          {years.map((year) => (
            <button
              key={year}
              onClick={() => setSelectedYear(year)}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                selectedYear === year
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {year}
            </button>
          ))}
        </div>
        <div className="text-center p-4">No stats available for the selected year.</div>
      </div>
    );
  }

  return (
    <div className="p-4">
      {/* Year Filter UI */}
      <div className="flex justify-center space-x-2 mb-6">
        {years.map((year) => (
          <button
            key={year}
            onClick={() => setSelectedYear(year)}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              selectedYear === year
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {year}
          </button>
        ))}
      </div>

      {/* Existing basic stats display, adapted for new stats object structure */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center mb-8">
        <div>
          <h3 className="text-lg font-semibold text-gray-600">Total Sessions</h3>
          <p className="text-4xl font-bold text-gray-800">{stats.total_sessions || 0}</p>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-600">Total Surf Time</h3>
          <p className="text-4xl font-bold text-gray-800">{stats.total_hours ? stats.total_hours.toFixed(1) : 0} <span className="text-2xl">hrs</span></p>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-600">Average Stoke</h3>
          <p className="text-4xl font-bold text-gray-800">{stats.average_stoke ? stats.average_stoke.toFixed(2) : 'N/A'}</p>
        </div>
      </div>
      {/* Additional stats will go here in later steps */}
    </div>
  );
}

export default StatsDisplay;