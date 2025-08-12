import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiCall } from '../services/api';
import { useAuth } from '../context/AuthContext';
import Spinner from '../components/UI/Spinner';
import SessionsList from '../components/SessionsList';

function JournalPage() {
  const { userId } = useParams();
  const { user: currentUser } = useAuth();
  const [profileUser, setProfileUser] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

        // Fetch sessions data
        const sessionsResponse = await apiCall(`/api/users/${effectiveUserId}/sessions`);
        setSessions(sessionsResponse.data);

        setLoading(false);
      } catch (err) {
        setError('Failed to fetch data.');
        console.error(err);
        setLoading(false);
      }
    };

    fetchData();
  }, [userId, currentUser]);

  if (loading && !profileUser) {
    return <Spinner />;
  }

  if (error) {
    return <div className="text-red-500 text-center p-4">Error: {error}</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">
        {profileUser ? `${profileUser.display_name}'s Journal` : 'Journal'}
      </h1>
      <div>
        <SessionsList sessions={sessions} loading={loading} error={error} />
      </div>
    </div>
  );
}

export default JournalPage;
