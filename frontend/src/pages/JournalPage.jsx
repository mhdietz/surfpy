import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { apiCall } from '../services/api';

function JournalPage() {
  const { userId } = useParams();
  const [profileUser, setProfileUser] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetching logic will be added in later steps
    setLoading(false);
  }, [userId]);

  if (loading) {
    // A spinner component could be used here
    return <div>Loading journal...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center p-4">Error: {error}</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">
        Journal
      </h1>
      <div>
        <p>Sessions will be displayed here soon.</p>
      </div>
    </div>
  );
}

export default JournalPage;
