import React from 'react';
import Spinner from './UI/Spinner';
import Card from './UI/Card';

function StatsDisplay({ stats, loading, error }) {
  if (loading) {
    return <Spinner />;
  }

  if (error) {
    return <div className="text-red-500 text-center p-4">Error: {error}</div>;
  }

  if (!stats) {
    return <div className="text-center p-4">No stats available.</div>;
  }

  // Convert minutes to hours, rounding to one decimal place
  const hours = stats.total_surf_time_minutes ? (stats.total_surf_time_minutes / 60).toFixed(1) : 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
      <div>
        <h3 className="text-lg font-semibold text-gray-600">Total Sessions</h3>
        <p className="text-4xl font-bold text-gray-800">{stats.total_sessions || 0}</p>
      </div>
      <div>
        <h3 className="text-lg font-semibold text-gray-600">Total Surf Time</h3>
        <p className="text-4xl font-bold text-gray-800">{hours} <span className="text-2xl">hrs</span></p>
      </div>
      <div>
        <h3 className="text-lg font-semibold text-gray-600">Average Fun</h3>
        <p className="text-4xl font-bold text-gray-800">{stats.average_fun_rating || 'N/A'}</p>
      </div>
    </div>
  );
}

export default StatsDisplay;
