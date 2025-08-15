import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom'; // Import useNavigate
import { useAuth } from '../context/AuthContext';
import Card from '../components/UI/Card';
import Spinner from '../components/UI/Spinner';
import { format } from 'date-fns';
import { apiCall, deleteSession, toggleShaka, getSessionShakas } from '../services/api'; // Import deleteSession
import toast from 'react-hot-toast'; // Import toast

import SwellDisplay from '../components/SwellDisplay';
import WindDisplay from '../components/WindDisplay';
import TideDisplay from '../components/TideDisplay';
import ShakaModal from '../components/ShakaModal';

const SessionDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate(); // Initialize useNavigate
  const location = useLocation();
  const { isAuthenticated, user } = useAuth(); // Get user from AuthContext

  // State management
  const [session, setSession] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isShakaModalOpen, setIsShakaModalOpen] = useState(false);
  const [shakaData, setShakaData] = useState({
    shakaCount: 0,
    hasViewerShakaed: false,
    shakaPreview: [],
  });
  const [shakaAllUsers, setShakaAllUsers] = useState([]);
  const [loadingShakaUsers, setLoadingShakaUsers] = useState(false);

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
  }, [id, isAuthenticated, location.key]);

  useEffect(() => {
    if (session?.shakas) {
      setShakaData({
        shakaCount: session.shakas.count || 0,
        hasViewerShakaed: session.shakas.viewer_has_shakaed || false,
        shakaPreview: session.shakas.preview || [],
      });
    }
  }, [session?.shakas]);

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

  const handleDeleteSession = async () => {
    if (window.confirm('Are you sure you want to delete this session? This action cannot be undone.')) {
      try {
        await toast.promise(deleteSession(id), {
          loading: 'Deleting session...', 
          success: 'Session deleted successfully!',
          error: 'Failed to delete session.',
        });
        navigate('/journal'); // Redirect to journal page after successful deletion
      } catch (err) {
        console.error("Error deleting session:", err);
        // toast.error is handled by toast.promise
      }
    }
  };

  const openShakaModal = () => setIsShakaModalOpen(true);
  const closeShakaModal = () => setIsShakaModalOpen(false);

  const handleToggleShaka = async () => {
    const wasShaked = shakaData.hasViewerShakaed;
    setShakaData(prev => ({ ...prev, hasViewerShakaed: !wasShaked, shakaCount: wasShaked ? prev.shakaCount - 1 : prev.shakaCount + 1 }));
    
    try {
      const response = await toggleShaka(id);
      setShakaData(prev => ({ ...prev, shakaCount: response.data.shaka_count || 0 }));
    } catch (error) {
      console.error('🤙 Failed to toggle shaka:', error);
      setShakaData(prev => ({ ...prev, hasViewerShakaed: wasShaked, shakaCount: wasShaked ? prev.shakaCount + 1 : prev.shakaCount - 1 }));
    }
  };

  const handleOpenShakaModal = async () => {
    if (shakaData.shakaCount > 0) {
      setIsShakaModalOpen(true);
      setLoadingShakaUsers(true);
      try {
        const allUsers = await getSessionShakas(id);
        setShakaAllUsers(allUsers);
      } catch (error) {
        console.error('🤙 Failed to load shaka users:', error);
        setShakaAllUsers(shakaData.shakaPreview); // Fallback to preview if full list fails
      } finally {
        setLoadingShakaUsers(false);
      }
    }
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
              <div className="text-gray-800 bg-white p-3 rounded-lg border border-black">
                <h2 className="text-xl font-bold mb-2">Notes</h2>
                <p>{session.session_notes}</p>
              </div>
            </div>
          )}

          <div className="flex items-center gap-4 mb-6"> {/* New flex container for Shaka Group and Stoke Tile */}
            {/* Shaka Group */}
            <div className="flex flex-col gap-2 flex-shrink-0 border border-black p-3 rounded-lg flex-1"> {/* Added flex-1 */}
              <h2 className="text-xl font-bold">Shakas</h2>
              <div className="flex items-center gap-2"> {/* This div keeps icon and count side-by-side */}
                <span onClick={handleToggleShaka} className={`text-xl cursor-pointer transition-all ${shakaData.hasViewerShakaed ? 'grayscale-0' : 'grayscale'}`}>🤙</span>
                <div onClick={handleOpenShakaModal} className="cursor-pointer">
                  <span className="font-bold text-blue-600 text-sm">{shakaData.shakaCount}</span>
                </div>
              </div>
            </div>

            {/* Stoke Tile */}
            <div className="flex flex-col gap-2 text-gray-800 bg-white p-3 rounded-lg border border-black flex-1"> {/* Match Shaka structure */}
              <h2 className="text-xl font-bold">Stoke</h2>
              <p className="text-xl">{session.fun_rating}<span className="text-sm text-gray-800">/10</span></p>
            </div>
          </div>

          <div className="mb-4">
            <h2 className="text-xl font-bold mb-2">Surfers</h2>
            <div className="flex flex-wrap gap-2">
              {session.participants
                .filter(p => p.user_id !== session.user_id) // Filter out the session creator
                .map(p => (
                <span key={p.user_id} className="bg-gray-700 px-3 py-1 rounded-full text-sm">
                  {p.display_name}
                </span>
              ))}
            </div>
          </div>

          {/* Action Buttons - Only visible to session creator */}
          {user && session.user_id === user.id && (
            <div className="mt-6 space-y-2">
              {/* Edit Button */}
              <button
                onClick={() => navigate(`/session/${id}/edit`)}
                className="w-full bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-lg focus:outline-none focus:shadow-outline transition duration-150 ease-in-out"
              >
                Edit Session
              </button>

              {/* Delete Session Button */}
              <button
                onClick={handleDeleteSession}
                className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg focus:outline-none focus:shadow-outline transition duration-150 ease-in-out"
              >
                Delete Session
              </button>
            </div>
          )}

        </div>
      </Card>

      {isShakaModalOpen && (
        <ShakaModal 
          users={shakaAllUsers}
          onClose={() => {
            setIsShakaModalOpen(false);
            setShakaAllUsers([]);
          }}
          loading={loadingShakaUsers}
        />
      )}
    </div>
  );
};

export default SessionDetail;
