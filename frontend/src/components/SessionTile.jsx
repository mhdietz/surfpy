import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ShakaModal from './ShakaModal';
import { toggleShaka, getSessionShakas } from '../services/api'; // Add getSessionShakas import
import { useAuth } from '../context/AuthContext';

const SessionTile = ({ session }) => {
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const [isShakaModalOpen, setIsShakaModalOpen] = useState(false);

  const [shakaCount, setShakaCount] = useState(0);
  const [hasViewerShakaed, setHasViewerShakaed] = useState(false);
  const [shakaPreview, setShakaPreview] = useState([]);
  const [shakaAllUsers, setShakaAllUsers] = useState([]); // Add this state
  const [loadingShakaUsers, setLoadingShakaUsers] = useState(false); // Add this state

  const {
    id, user_id, session_name, location, fun_rating,
    session_started_at, display_name, participants, shakas, session_notes,
  } = session || {};

  useEffect(() => {
    if (shakas) {
      setShakaCount(shakas.count || 0);
      setHasViewerShakaed(shakas.viewer_has_shakaed || false);
      setShakaPreview(shakas.preview || []);
    }
  }, [shakas]);

  if (!session) {
    return null;
  }

  const sessionDate = new Date(session_started_at).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric',
  });

  const handleNavigateToSession = () => navigate(`/session/${id}`);

  const handleNavigateToJournal = (e, userId) => {
    e.stopPropagation();
    navigate(`/journal/${userId}`);
  };

  // Updated handleOpenShakaModal function
  const handleOpenShakaModal = async (e) => {
    e.stopPropagation();
    if (shakaCount > 0) {
      setIsShakaModalOpen(true);
      setLoadingShakaUsers(true);
      
      try {
        const allUsers = await getSessionShakas(id);
        setShakaAllUsers(allUsers);
      } catch (error) {
        console.error('🤙 Failed to load shaka users:', error);
        // Fallback to preview data if API call fails
        setShakaAllUsers(shakaPreview);
      } finally {
        setLoadingShakaUsers(false);
      }
    }
  };

  const handleToggleShaka = async (e) => {
    e.stopPropagation();
    
    // Optimistic update - change UI immediately
    const wasShaked = hasViewerShakaed;
    setHasViewerShakaed(!wasShaked);
    setShakaCount(prev => wasShaked ? prev - 1 : prev + 1);
    
    try {
      const response = await toggleShaka(id);
      console.log('🤙 Shaka API response:', response);
      
      // Update count with server response
      setShakaCount(response.data.shaka_count || 0);
      
      // Update preview array (keep existing logic for tile display)
      if (currentUser) {
        const currentUserPreview = {
          user_id: currentUser.id,
          display_name: currentUser.display_name || currentUser.email
        };
        
        if (!wasShaked) {
          setShakaPreview(prev => [
            currentUserPreview,
            ...prev.filter(user => user.user_id !== currentUser.id)
          ].slice(0, 2));
        } else {
          setShakaPreview(prev => prev.filter(user => user.user_id !== currentUser.id));
        }
      }
    } catch (error) {
      console.error('🤙 Failed to toggle shaka:', error);
      
      // Rollback optimistic update on error
      setHasViewerShakaed(wasShaked);
      setShakaCount(prev => wasShaked ? prev + 1 : prev - 1);
    }
  };

  return (
    <>
      <div onClick={handleNavigateToSession} className="bg-white p-4 sm:p-6 rounded-lg shadow border border-gray-200 space-y-4 cursor-pointer hover:shadow-lg transition-shadow">
        {/* Header */}
        <div className="flex justify-between items-center">
          <p onClick={(e) => handleNavigateToJournal(e, user_id)} className="font-bold text-lg text-gray-800 hover:underline">
            {display_name}
          </p>
          <p className="text-sm text-gray-500">{sessionDate}</p>
        </div>

        {/* Body */}
        <div className="space-y-2">
          <h3 className="text-2xl font-bold text-gray-900">{session_name || 'Untitled Session'}</h3>
          <p className="text-md font-semibold text-gray-700">{location}</p>
          
          {session_notes && <p className="text-gray-600 bg-gray-50 p-3 rounded-md">{session_notes}</p>}

          {participants && participants.length > 0 && (
            <div className="pt-2">
              <p className="font-semibold text-gray-700">With:</p>
              <div className="flex flex-wrap gap-2 mt-1">
                {participants
                  .filter(p => p.user_id !== user_id) // Filter out the session creator
                  .map(p => (
                  <span 
                    key={p.user_id} 
                    onClick={(e) => handleNavigateToJournal(e, p.user_id)}
                    className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm font-medium hover:bg-blue-200 hover:text-blue-900"
                  >
                    {p.display_name}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-3 border-t border-gray-200">
          {/* Fun Rating */}
          <div className="flex items-center gap-2">
            <span className="font-bold text-gray-800">Fun Rating:</span>
            <span className="font-bold text-blue-600 text-lg">{fun_rating} / 10</span>
          </div>

          {/* Shaka Count & Toggle */}
          <div className="flex items-center gap-2">
            <span 
              onClick={handleToggleShaka} 
              className={`text-xl cursor-pointer transition-all ${hasViewerShakaed ? 'grayscale-0' : 'grayscale'}`}
            >
              🤙
            </span>
            <div onClick={handleOpenShakaModal} className="cursor-pointer">
              <span className="font-bold text-blue-600 text-lg">{shakaCount}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Updated Shaka Modal */}
      {isShakaModalOpen && (
        <ShakaModal 
          users={shakaAllUsers} // Changed from shakaPreview to shakaAllUsers
          onClose={() => {
            setIsShakaModalOpen(false);
            setShakaAllUsers([]); // Clear data when modal closes
          }}
          loading={loadingShakaUsers} // Add loading prop if ShakaModal supports it
        />
      )}
    </>
  );
};

export default SessionTile;