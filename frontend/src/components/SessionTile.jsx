import React from 'react';
import Button from './UI/Button';

// Final minimal version of SessionTile
const SessionTile = ({ session }) => {
  if (!session) {
    return null;
  }

  const {
    session_name,
    location,
    fun_rating,
    session_started_at,
    display_name,
    participants,
    shakas,
    session_notes, // Added session_notes
  } = session;

  const sessionDate = new Date(session_started_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="space-y-4 p-1">
      {/* Header */}
      <div className="flex justify-between items-center">
        <p className="font-bold text-lg text-gray-800">{display_name}</p>
        <p className="text-sm text-gray-500">{sessionDate}</p>
      </div>

      {/* Body */}
      <div className="space-y-2">
        <h3 className="text-2xl font-bold text-gray-900">{session_name || 'Untitled Session'}</h3>
        <p className="text-md font-semibold text-gray-700">{location}</p>
        
        {/* Session Notes */}
        {session_notes && (
          <p className="text-gray-600 bg-gray-50 p-3 rounded-md">{session_notes}</p>
        )}

        {/* Participant Names */}
        {participants && participants.length > 0 && (
          <div className="pt-2">
            <p className="font-semibold text-gray-700">With:</p>
            <div className="flex flex-wrap gap-2 mt-1">
              {participants.map(p => (
                <span key={p.user_id} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm font-medium">
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
          <span className="font-bold text-blue-600 text-lg">{fun_rating} / 5</span>
        </div>

        {/* Shaka Count */}
        <div className="flex items-center gap-2">
            <span className="font-bold text-gray-800">Shakas:</span>
            <span className="font-bold text-blue-600 text-lg">{shakas?.count || 0}</span>
        </div>
      </div>
    </div>
  );
};

export default SessionTile;
