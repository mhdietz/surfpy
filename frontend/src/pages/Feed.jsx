import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Button from '../components/UI/Button';
import Card from '../components/UI/Card';
import SessionsList from '../components/SessionsList';
import PageTabs from '../components/PageTabs';
import { apiCall } from '../services/api';
import Spinner from '../components/UI/Spinner';
import Leaderboard from '../components/Leaderboard'; // Import Leaderboard

const Feed = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const currentTab = queryParams.get('tab') || 'feed';

  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAllSessions = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiCall('/api/surf-sessions');
        setSessions(response.data);
      } catch (err) {
        console.error('Error fetching all sessions:', err);
        setError(err.message || 'Failed to fetch sessions');
      } finally {
        setLoading(false);
      }
    };

    if (currentTab === 'feed') {
      fetchAllSessions();
    } else {
      // For leaderboard tab, loading is handled by the Leaderboard component itself
      setLoading(false);
    }
  }, [currentTab]);

  const feedTabs = [
    { label: 'Feed', path: '/feed' },
    { label: 'Leaderboard', path: '/feed?tab=leaderboard' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/auth/login');
  };

  return (
    <div className="bg-gray-100 min-h-screen pb-8">
      <main className="max-w-2xl mx-auto">
        <PageTabs tabs={feedTabs} />

        <div className="w-full bg-white rounded-b-lg shadow-md"> 
          {currentTab === 'feed' && (
            <div>
              {/* Removed Community Feed Heading */}
              {loading && <Spinner />}
              {error && <div className="text-red-500 text-center p-4">Error: {error}</div>}
              {!loading && !error && <SessionsList sessions={sessions} />}
            </div>
          )}

          {currentTab === 'leaderboard' && (
            <Leaderboard />
          )}
        </div>
      </main>
    </div>
  );
};

export default Feed;