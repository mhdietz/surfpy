import React from 'react';
import Spinner from './UI/Spinner';
import SessionTile from './SessionTile';

const SessionsList = ({ sessions, loading, error, isOwnJournal, profileUser }) => {
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
        <div className="text-center text-gray-700 p-8 bg-blue-50 rounded-lg shadow-inner">
          {isOwnJournal ? (
            <>
              <p className="text-xl font-semibold mb-2">You're dry mate</p>
              <p className="text-lg">get your ass in the water</p>
            </>
          ) : (
            <>
              <p className="text-xl font-semibold mb-2">{profileUser?.display_name}'s dry</p>
              <p className="text-lg">get that ass in the water</p>
            </>
          )}
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