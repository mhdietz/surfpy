import React from 'react';
import html2canvas from 'html2canvas';
import Spinner from './UI/Spinner';
import TopSessions from './TopSessions';
import TopLocations from './TopLocations';
import SessionsByMonthChart from './SessionsByMonthChart';
import StokeByMonthChart from './StokeByMonthChart';
import MostFrequentBuddy from './MostFrequentBuddy';
import ShareableYearInReview from './ShareableYearInReview';
import { useAuth } from '../context/AuthContext';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';

function StatsDisplay({ stats, loading, error, selectedYear, setSelectedYear }) {
  const { user: currentUser } = useAuth();
  const profileDisplayName = currentUser?.display_name || currentUser?.email?.split('@')[0] || 'Surfer';

  const handleShare = () => {
    const card = document.getElementById('shareable-card');
    if (card) {
      html2canvas(card, {
        useCORS: true,
        scale: 2, // Increase scale for better resolution
      }).then(canvas => {
        const link = document.createElement('a');
        link.download = `surfpy-review-${selectedYear}.png`;
        link.href = canvas.toDataURL('image/png');
        link.click();
      });
    }
  };

  if (loading) {
    return <Spinner />;
  }

  if (error) {
    return <div className="text-red-500 text-center p-4">Error: {error}</div>;
  }

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: currentYear - 2023 + 1 }, (_, i) => currentYear - i);

  const hasNoSessions = stats && stats.total_sessions === 0;

  if (hasNoSessions) {
    return (
      <>
        <div className="p-4">
          <div className="flex justify-center space-x-2 mb-6">
            {years.map(year => (
              <button
                key={year}
                onClick={() => setSelectedYear(year)}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${selectedYear === year ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
              >
                {year}
              </button>
            ))}
          </div>
          <div className="text-center p-4 text-gray-600">
            <p className="text-lg mb-2">You haven't logged any sessions in {selectedYear}.</p>
            <p className="mb-4">Start logging to build your stats!</p>
            <a href="/create-session" className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-lg transition duration-200">
              Log Your First Session
            </a>
          </div>
        </div>
        <ShareableYearInReview stats={stats} selectedYear={selectedYear} profileDisplayName={profileDisplayName} />
      </>
    );
  }

  if (!stats) {
    return (
      <div className="p-4">
        <div className="flex justify-center space-x-2 mb-6">
          {years.map(year => (
            <button
              key={year}
              onClick={() => setSelectedYear(year)}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${selectedYear === year ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
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
    <div className="p-4 relative">
      <button
        onClick={handleShare}
        className="absolute top-4 right-4 p-2 text-gray-700 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-300"
        aria-label="Download your year in review image"
      >
        <ArrowDownTrayIcon className="h-6 w-6" />
      </button>

      <div className="flex justify-center space-x-2 mb-6">
        {years.map(year => (
          <button
            key={year}
            onClick={() => setSelectedYear(year)}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${selectedYear === year ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
          >
            {year}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-4 text-center mb-8">
        <div>
          <h3 className="text-sm md:text-lg font-semibold text-gray-600">Total Sessions</h3>
          <p className="text-2xl md:text-4xl font-bold text-gray-800">{stats.total_sessions || 0}</p>
        </div>
        <div>
          <h3 className="text-sm md:text-lg font-semibold text-gray-600">Total Surf Time</h3>
          <p className="text-2xl md:text-4xl font-bold text-gray-800">{stats.total_hours ? stats.total_hours.toFixed(1) : 0} <span className="text-lg md:text-2xl">hrs</span></p>
        </div>
        <div>
          <h3 className="text-sm md:text-lg font-semibold text-gray-600">Average Stoke</h3>
          <p className="text-2xl md:text-4xl font-bold text-gray-800">{stats.average_stoke ? stats.average_stoke.toFixed(2) : 'N/A'}</p>
        </div>
      </div>
      
      {stats.top_locations && stats.top_locations.length > 0 && (
        <TopLocations locations={stats.top_locations} />
      )}

      {stats.top_sessions && stats.top_sessions.length > 0 && (
        <TopSessions sessions={stats.top_sessions} />
      )}

      {stats.sessions_by_month && stats.sessions_by_month.length > 0 && (
        <SessionsByMonthChart data={stats.sessions_by_month} />
      )}

      {stats.stoke_by_month && stats.stoke_by_month.length > 0 && (
        <StokeByMonthChart data={stats.stoke_by_month} />
      )}

      {stats.most_frequent_buddy && (
        <MostFrequentBuddy buddy={stats.most_frequent_buddy} />
      )}

      <ShareableYearInReview stats={stats} selectedYear={selectedYear} profileDisplayName={profileDisplayName} />
    </div>
  );
}

export default StatsDisplay;