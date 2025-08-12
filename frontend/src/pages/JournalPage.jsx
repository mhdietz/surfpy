import React, { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { apiCall } from '../services/api';
import { useAuth } from '../context/AuthContext';
import Spinner from '../components/UI/Spinner';
import SessionsList from '../components/SessionsList';
import PageTabs from '../components/PageTabs';

function JournalPage() {
  const { userId } = useParams();
  const { user: currentUser } = useAuth();
  const [profileUser, setProfileUser] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const currentTab = queryParams.get('tab') || 'log'; // Default to 'log'

  const journalTabs = [
    { label: 'Log', path: `/journal/${userId}?tab=log` },
    { label: 'My Stats', path: `/journal/${userId}?tab=stats` },
  ];

  useEffect(() => {
    const fetchData = async () => {
      // If we're on the 'me' page, wait for the currentUser object to be loaded.
      if (userId === 'me' && !currentUser) {
        return; // The effect will re-run when currentUser is available.
      }

      try {
        setLoading(true);
        const effectiveUserId = userId === 'me' ? currentUser.id : userId;

        if (!effectiveUserId) {
          setError("User not found.");
          setLoading(false);
          return;
        }

        // Fetch profile data
        const profileResponse = await apiCall(`/api/users/${effectiveUserId}/profile`);
        setProfileUser(profileResponse.data);

        // Fetch sessions data (only if on the 'log' tab)
        if (currentTab === 'log') {
          const sessionsResponse = await apiCall(`/api/users/${effectiveUserId}/sessions`);
          setSessions(sessionsResponse.data);
        }

        setLoading(false);
      } catch (err) {
        setError('Failed to fetch data.');
        console.error(err);
        setLoading(false);
      }
    };

    fetchData();
  }, [userId, currentUser, currentTab]); // Add currentTab to dependencies

  if (loading && !profileUser) {
    return <Spinner />;
  }

  if (error) {
    return <div className="text-red-500 text-center p-4">Error: {error}</div>;
  }

  return (
    <div className="container mx-auto p-4 pt-16">
      <h1 className="text-2xl font-bold mb-4">
        {profileUser ? `${profileUser.display_name}'s Journal` : 'Journal'}
      </h1>
      
      <PageTabs tabs={journalTabs} />

      {currentTab === 'log' && (
        <div>
          <SessionsList sessions={sessions} loading={loading} error={error} />
        </div>
      )}

      {currentTab === 'stats' && (
        <div className="text-center p-4">
          <p>This is the stats section for {profileUser ? profileUser.display_name : 'this user'}.</p>
          {/* Stats component will go here eventually */}
        </div>
      )}
    </div>
  );
}

export default JournalPage;
