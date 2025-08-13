import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Card from '../components/UI/Card';
import Spinner from '../components/UI/Spinner';
import { format } from 'date-fns';
import { apiCall } from '../services/api';

import SwellDisplay from '../components/SwellDisplay';
import WindDisplay from '../components/WindDisplay';
import TideDisplay from '../components/TideDisplay';

const SessionDetail = () => {
  const { id } = useParams();
  const { isAuthenticated } = useAuth();

  // State management
  const [session, setSession] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSession = async () => {
      setIsLoading(true);
      try {
        const response = await apiCall(`/api/surf-sessions/${id}`);
        if (response.status === 'success') {
          setSession(response.data);
          setError(null);
        } else {
          throw new Error(response.message || 'Failed to fetch session data.');
        }
      } catch (err) {
        setError(err);
        setSession(null);
        console.error("Failed to fetch session:", err);
      } finally {
        setIsLoading(false);
      }
    };

    if (isAuthenticated && id) {
      fetchSession();
    } else {
      setIsLoading(false);
    }
  }, [id, isAuthenticated]);

  // Helper to format date and time
  const formatSessionTime = (start, end) => {
    const startDate = new Date(start);
    const endDate = new Date(end);
    // Format: Mon, Aug 11, 2025, 10:10 PM - 12:10 AM
    const datePart = format(startDate, "EEE, MMM d, yyyy");
    const startTimePart = format(startDate, "h:mm a");
    const endTimePart = format(endDate, "h:mm a");
    return `${datePart}, ${startTimePart} - ${endTimePart}`;
  };

  if (!isAuthenticated) {
    return (
      <div className="text-center p-4 text-red-500">
        You must be logged in to view session details.
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Spinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-4 text-red-500">
        <p>Error loading session:</p>
        <p>{error.message}</p>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="text-center p-4 text-gray-400">
        Session not found.
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-4">
      <Card>
        <div className="p-4">
          <h1 className="text-3xl font-bold mb-2">{session.session_name}</h1>
          <p className="text-lg text-gray-400 mb-2">{session.location}</p>
          <p className="text-md text-gray-300 mb-4">{formatSessionTime(session.session_started_at, session.session_ended_at)}</p>

          {/* Swell Display Component */}
          {session.raw_swell && <SwellDisplay swellData={session.raw_swell} />}

          {/* Wind Display Component */}
          {session.raw_met && <WindDisplay windData={session.raw_met} />}

          {/* Tide Display Component */}
          {session.tide && <TideDisplay tideData={session.tide} />}

          {session.session_notes && (
            <div className="mt-4 mb-4">
              <h2 className="text-xl font-bold mb-2">Notes</h2>
              <p className="text-gray-300 bg-gray-800 p-3 rounded-lg">{session.session_notes}</p>
            </div>
          )}

          <div className="flex justify-between items-center mb-6">
            <div>
              <span className="text-2xl font-bold text-yellow-400">{session.fun_rating}</span>
              <span className="text-gray-400">/10 Fun Rating</span>
            </div>
            <div>
              <span className="text-2xl">🤙</span>
              <span className="font-bold ml-2">{session.shakas.count} Shakas</span>
            </div>
          </div>

          <div className="mb-4">
            <h2 className="text-xl font-bold mb-2">Surfers</h2>
            <div className="flex flex-wrap gap-2">
              {session.participants.map(p => (
                <span key={p.user_id} className="bg-gray-700 px-3 py-1 rounded-full text-sm">
                  {p.display_name}
                </span>
              ))}
            </div>
          </div>

          {/* Dummy Delete Session Button */}
          <div className="mt-6">
            <button
              className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg focus:outline-none focus:shadow-outline transition duration-150 ease-in-out"
            >
              Delete Session
            </button>
          </div>

        </div>
      </Card>
    </div>
  );
};

export default SessionDetail;