import React, { useState, useEffect } from 'react';
import { apiCall } from '../services/api';
import Spinner from './UI/Spinner'; // Import Spinner
import SessionTile from './SessionTile'; // Import SessionTile

const SessionsList = () => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiCall('/api/surf-sessions');
        console.log('Fetched sessions:', response.data);
        setSessions(response.data);
      } catch (err) {
        console.error('Error fetching sessions:', err);
        setError(err.message || 'Failed to fetch sessions');
      } finally {
        setLoading(false);
      }
    };

    fetchSessions();
  }, []);

  return (
    <div className="space-y-6">
      {loading && (
        <div className="flex justify-center items-center h-32">
          <Spinner />
        </div>
      )}

      {error && (
        <div className="text-red-500 text-center p-4 border border-red-300 rounded-md">
          <p>Error: {error}</p>
          <p>Please try again later.</p>
        </div>
      )}

      {!loading && !error && sessions.length === 0 && (
        <div className="text-center text-gray-600 p-4">
          <p>No sessions found.</p>
          <p>Be the first to log a session!</p>
        </div>
      )}

      {!loading && !error && sessions.length > 0 && (
        <div className="grid grid-cols-1 gap-6">
          {sessions.map((session) => (
            <SessionTile key={session.id} session={session} />
          ))}
        </div>
      )}
    </div>
  );
};

export default SessionsList;