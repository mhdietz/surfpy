import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ShakaModal from './ShakaModal';
import { toggleShaka, getSessionShakas } from '../services/api';
import { useAuth } from '../context/AuthContext';

// Helper function for date formatting
const formatSessionDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric',
  });
};

// Journal-style Tile
const JournalTile = ({ session, onNavigate, onUserClick, onShaka, onOpenShakaModal, shakaData }) => {
  const { id, user_id, session_name, location, fun_rating, session_started_at, display_name, participants, session_notes } = session;
  const { shakaCount, hasViewerShakaed } = shakaData;

  const date = new Date(session_started_at);
  const month = date.toLocaleString('en-US', { month: 'short' }).toUpperCase();
  const day = date.getDate();
  const year = date.getFullYear();

  const generateParticipantsString = () => {
    const others = participants.filter(p => p.user_id !== user_id);
    if (others.length === 0) return '';

    const firstName = others[0].display_name;
    if (others.length === 1) {
      return `with ${firstName}`;
    }

    const othersCount = others.length - 1;
    return `with ${firstName} and ${othersCount} other${othersCount > 1 ? 's' : ''}`;
  };

  return (
    <div onClick={onNavigate} className="bg-white rounded-lg shadow border border-gray-200 flex cursor-pointer hover:shadow-lg transition-shadow overflow-hidden">
      {/* Date Column (LHS) */}
      <div className="flex flex-col justify-center items-center w-20 flex-shrink-0 bg-gray-50 p-2 border-r border-gray-200">
        <p className="text-sm font-semibold text-red-500 tracking-wider">{month}</p>
        <p className="text-4xl font-bold text-gray-800">{day}</p>
        <p className="text-xs text-gray-400">{year}</p>
      </div>

      {/* Content Column (RHS) */}
      <div className="flex-grow flex flex-col p-4">
        {/* Header */}
        <div className="flex justify-between items-start gap-4">
          {/* Title and Creator */}
          <div>
            <h3 className="text-xl font-bold text-gray-900">{session_name || 'Untitled Session'}</h3>
            <p onClick={(e) => onUserClick(e, user_id)} className="text-sm font-medium text-gray-500 hover:underline">
              by {display_name}
            </p>
          </div>
          {/* Rating */}
          <div className="flex-shrink-0">
            <p className="text-3xl font-bold text-blue-600">{fun_rating}</p>
          </div>
        </div>

        {/* Body */}
        <div className="flex-grow space-y-3 mt-2">
                    {session_notes && 
            <div className="bg-gray-50 p-3 rounded-md">
              <p className="text-sm text-gray-600 line-clamp-3">
                {session_notes}
              </p>
            </div>
          }
        </div>

        {/* Footer */}
        <div className="pt-3 mt-auto border-t border-gray-100 space-y-2">
          {/* Location and Participants */}
          <div className="text-sm space-y-1">
            <p className="font-semibold text-gray-800 truncate">{location}</p>
            {participants && participants.length > 1 && (
              <p className="font-normal text-gray-500 truncate">{generateParticipantsString()}</p>
            )}
          </div>

          {/* Shaka Controls */}
          <div className="flex justify-end items-center">
            <div className="flex items-center gap-2 flex-shrink-0">
              <span onClick={onShaka} className={`text-xl cursor-pointer transition-all ${hasViewerShakaed ? 'grayscale-0' : 'grayscale'}`}>🤙</span>
              <div onClick={onOpenShakaModal} className="cursor-pointer">
                <span className="font-bold text-blue-600">{shakaCount}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};



// Main Component Router
const SessionTile = ({ session, variant = 'journal' }) => {
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const [isShakaModalOpen, setIsShakaModalOpen] = useState(false);

  const [shakaData, setShakaData] = useState({
    shakaCount: 0,
    hasViewerShakaed: false,
    shakaPreview: [],
  });
  const [shakaAllUsers, setShakaAllUsers] = useState([]);
  const [loadingShakaUsers, setLoadingShakaUsers] = useState(false);

  useEffect(() => {
    if (session?.shakas) {
      setShakaData({
        shakaCount: session.shakas.count || 0,
        hasViewerShakaed: session.shakas.viewer_has_shakaed || false,
        shakaPreview: session.shakas.preview || [],
      });
    }
  }, [session?.shakas]);

  if (!session) {
    return null;
  }

  const handleNavigateToSession = () => navigate(`/session/${session.id}`);

  const handleNavigateToJournal = (e, userId) => {
    e.stopPropagation();
    navigate(`/journal/${userId}`);
  };

  const handleOpenShakaModal = async (e) => {
    e.stopPropagation();
    if (shakaData.shakaCount > 0) {
      setIsShakaModalOpen(true);
      setLoadingShakaUsers(true);
      try {
        const allUsers = await getSessionShakas(session.id);
        setShakaAllUsers(allUsers);
      } catch (error) {
        console.error('🤙 Failed to load shaka users:', error);
        setShakaAllUsers(shakaData.shakaPreview);
      } finally {
        setLoadingShakaUsers(false);
      }
    }
  };

  const handleToggleShaka = async (e) => {
    e.stopPropagation();
    const wasShaked = shakaData.hasViewerShakaed;
    setShakaData(prev => ({ ...prev, hasViewerShakaed: !wasShaked, shakaCount: wasShaked ? prev.shakaCount - 1 : prev.shakaCount + 1 }));
    
    try {
      const response = await toggleShaka(session.id);
      setShakaData(prev => ({ ...prev, shakaCount: response.data.shaka_count || 0 }));
    } catch (error) {
      console.error('🤙 Failed to toggle shaka:', error);
      setShakaData(prev => ({ ...prev, hasViewerShakaed: wasShaked, shakaCount: wasShaked ? prev.shakaCount + 1 : prev.shakaCount - 1 }));
    }
  };

  const tileProps = {
    session,
    onNavigate: handleNavigateToSession,
    onUserClick: handleNavigateToJournal,
    onShaka: handleToggleShaka,
    onOpenShakaModal: handleOpenShakaModal,
    shakaData,
  };

  return (
    <>
      {variant === 'strava' ? <StravaTile {...tileProps} /> : <JournalTile {...tileProps} />}
      
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
    </>
  );
};

export default SessionTile;
