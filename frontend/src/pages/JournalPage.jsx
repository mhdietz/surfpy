import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useSearchParams } from 'react-router-dom';
import { apiCall } from '../services/api';
import { useAuth } from '../context/AuthContext';
import Spinner from '../components/UI/Spinner';
import SessionsList from '../components/SessionsList';
import PageTabs from '../components/PageTabs';
import JournalFilter from '../components/JournalFilter';
import StatsDisplay from '../components/StatsDisplay'; // Import the new component

// Helper function to parse URL search params into filter state
const parseSearchParams = (params) => {
  const newFilters = {};
  const filterKeys = [
    'min_swell_height', 'max_swell_height',
    'min_swell_period', 'max_swell_period',
    'swell_direction', 'region'
  ];
  filterKeys.forEach(key => {
    newFilters[key] = params.get(key) || '';
  });
  return newFilters;
};

function JournalPage() {
  const { userId } = useParams();
  const { user: currentUser } = useAuth();
  const [profileUser, setProfileUser] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [stats, setStats] = useState(null); // State for stats data
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();
  const currentTab = searchParams.get('tab') || 'log'; // Default to 'log'

  // Initialize filters from URL search params
  const [filters, setFilters] = useState(() => parseSearchParams(searchParams));

  // Effect to update filters state when searchParams change (e.g., browser back/forward)
  useEffect(() => {
    setFilters(parseSearchParams(searchParams));
  }, [searchParams]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    const newSearchParams = new URLSearchParams(searchParams);
    if (value) {
      newSearchParams.set(name, value);
    } else {
      newSearchParams.delete(name);
    }
    setSearchParams(newSearchParams);
  };

  useEffect(() => {
    const fetchData = async () => {
      if (userId === 'me' && !currentUser) {
        return; 
      }

      try {
        setLoading(true);
        setError(null); // Reset error state
        const effectiveUserId = userId === 'me' ? currentUser.id : userId;

        if (!effectiveUserId) {
          setError("User not found.");
          setLoading(false);
          return;
        }

        // Fetch profile data if not already fetched
        if (!profileUser || profileUser.id !== effectiveUserId) {
          const profileResponse = await apiCall(`/api/users/${effectiveUserId}/profile`);
          setProfileUser(profileResponse.data);
        }

        // Fetch data based on the active tab
        if (currentTab === 'log') {
          const queryString = new URLSearchParams(filters).toString();
          const sessionsResponse = await apiCall(`/api/users/${effectiveUserId}/sessions?${queryString}`);
          setSessions(sessionsResponse.data);
        } else if (currentTab === 'stats') {
          const statsResponse = await apiCall(`/api/users/${effectiveUserId}/stats`);
          setStats(statsResponse.data);
        }

        setLoading(false);
      } catch (err) {
        setError('Failed to fetch data.');
        console.error(err);
        setLoading(false);
      }
    };

    fetchData();
  }, [userId, currentUser, currentTab, filters, profileUser]); // Add profileUser to dependencies

  if (loading && !profileUser) {
    return <Spinner />;
  }

  if (error && !profileUser) { // Only show full-page error if profile hasn't loaded
    return <div className="text-red-500 text-center p-4">Error: {error}</div>;
  }

  // Determine the prefix for tab labels dynamically
  let journalOwnerPrefix = 'Surf Log'; // Default fallback   
  if (profileUser) {
    if (userId === 'me' || (currentUser && profileUser.id === currentUser.id)) {
      journalOwnerPrefix = 'My';
    } else {
      journalOwnerPrefix = `${profileUser.display_name}'s`;
    }
  }

  const isOwnJournal = userId === 'me' || (currentUser && profileUser && profileUser.id === currentUser.id);

  const journalTabs = [
    { label: `${journalOwnerPrefix} Surf Log`, path: `/journal/${userId || 'me'}?tab=log` },
    { label: `${journalOwnerPrefix} Stats`, path: `/journal/${userId || 'me'}?tab=stats` },
  ];

  return (
    <div className="bg-gray-100 min-h-screen py-8">
      <main className="max-w-2xl mx-auto px-2 sm:px-4 pt-4 sm:pt-8">
        <h1 className="text-2xl font-bold mb-6">
          {/* {profileUser 
            ? `${profileUser.display_name}'s ${currentTab === 'stats' ? 'Stats' : 'Surf Log'}` 
            : (currentTab === 'stats' ? 'Stats' : 'Surf Log')} */}
        </h1>
        
        <PageTabs tabs={journalTabs} />

        {currentTab === 'log' && (
          <div className="w-full bg-white p-6 rounded-lg shadow-md">
            <JournalFilter filters={filters} onFilterChange={handleFilterChange} />
            <SessionsList sessions={sessions} loading={loading} error={error} isOwnJournal={isOwnJournal} profileUser={profileUser} />
          </div>
        )}

        {currentTab === 'stats' && (
          <div className="w-full bg-white p-4 rounded-lg shadow-md"> 
            <StatsDisplay stats={stats} loading={loading} error={error} />
          </div>
        )}
      </main>
    </div>
  );
}

export default JournalPage;
