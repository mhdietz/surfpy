import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useSearchParams } from 'react-router-dom';
import { apiCall } from '../services/api';
import { useAuth } from '../context/AuthContext';
import Spinner from '../components/UI/Spinner';
import SessionsList from '../components/SessionsList';
import PageTabs from '../components/PageTabs';
import JournalFilter from '../components/JournalFilter';
import StatsDisplay from '../components/StatsDisplay';

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
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear()); // New state for year filter

  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();
  const currentTab = searchParams.get('tab') || 'log';

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
        setError(null);
        const effectiveUserId = userId === 'me' ? currentUser.id : userId;

        if (!effectiveUserId) {
          setError("User not found.");
          setLoading(false);
          return;
        }

        if (!profileUser || profileUser.id !== effectiveUserId) {
          const profileResponse = await apiCall(`/api/users/${effectiveUserId}/profile`);
          setProfileUser(profileResponse.data);
        }

        if (currentTab === 'log') {
          const queryString = new URLSearchParams(filters).toString();
          const sessionsResponse = await apiCall(`/api/users/${effectiveUserId}/sessions?${queryString}`);
          setSessions(sessionsResponse.data);
        } else if (currentTab === 'stats') {
          // Pass selectedYear to the API call for stats
          const statsResponse = await apiCall(`/api/users/${effectiveUserId}/stats?year=${selectedYear}`);
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
  }, [userId, currentUser, currentTab, filters, profileUser, selectedYear]); // Add selectedYear to dependencies

  if (loading && !profileUser) {
    return <Spinner />;
  }

  if (error && !profileUser) {
    return <div className="text-red-500 text-center p-4">Error: {error}</div>;
  }

  let journalOwnerPrefix = 'Surf Log';
  if (profileUser) {
    if (userId === 'me' || (currentUser && profileUser.id === currentUser.id)) {
      journalOwnerPrefix = 'My';
    } else {
      const nameToDisplay = profileUser.first_name || profileUser.display_name;
      journalOwnerPrefix = `${nameToDisplay}'s`;
    }
  }

  const isOwnJournal = userId === 'me' || (currentUser && profileUser && profileUser.id === currentUser.id);
  const isFiltered = Object.values(filters).some(val => val !== '');

  const journalTabs = [
    { label: `${journalOwnerPrefix} Surf Log`, path: `/journal/${userId || 'me'}?tab=log` },
    { label: `${journalOwnerPrefix} Stats`, path: `/journal/${userId || 'me'}?tab=stats` },
  ];

  return (
    <div className="bg-gray-100 min-h-screen pb-8">
      <main className="max-w-2xl mx-auto">
        <PageTabs tabs={journalTabs} />

        {currentTab === 'log' && (
          <div className="w-full bg-white rounded-b-lg shadow-md pb-4">
            <JournalFilter filters={filters} onFilterChange={handleFilterChange} />
            <SessionsList sessions={sessions} loading={loading} error={error} isOwnJournal={isOwnJournal} profileUser={profileUser} isFiltered={isFiltered} />
          </div>
        )}

        {currentTab === 'stats' && (
          <div className="w-full bg-white rounded-b-lg shadow-md pb-4"> 
            <StatsDisplay stats={stats} loading={loading} error={error} selectedYear={selectedYear} setSelectedYear={setSelectedYear} />
          </div>
        )}
      </main>
    </div>
  );
}

export default JournalPage;
