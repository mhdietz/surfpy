import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Spinner from './UI/Spinner';
import SessionTile from './SessionTile';

const SessionsList = ({ sessions, loading, error, isOwnJournal, profileUser }) => {
  return (
    <div className="space-y-6 p-4">
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
              <p className="text-lg mb-4">get your ass in the water</p>
              <Link to="/create-session" className="inline-block bg-blue-600 text-white font-bold py-2 px-4 rounded hover:bg-blue-700 transition-colors">
                Log a Session
              </Link>
            </>
          ) : (
            <>
              <p className="text-xl font-semibold mb-2">{profileUser?.display_name}'s dry</p>
              <p className="text-lg">get that ass in the water</p>
            </>)}
        </div>
      )}

      {!loading && !error && sessions.length > 0 && (
        <div className="grid grid-cols-1 gap-4">
          {sessions.map((session) => (
            <SessionTile key={session.id} session={session} />
          ))}
        </div>
      )}
    </div>
  );
};

export default SessionsList;