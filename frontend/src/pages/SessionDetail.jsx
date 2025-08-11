import React from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext'; // Corrected import
import Spinner from '../components/UI/Spinner';

const SessionDetail = () => {
  const { id } = useParams();
  const { isAuthenticated } = useAuth(); // Use the useAuth hook

  if (!isAuthenticated) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <p className="text-red-500">You must be logged in to view session details.</p>
      </div>
    );
  }

  return (
    <div className="flex justify-center items-center min-h-screen">
      <p className="text-gray-700 text-lg">Loading session details for ID: {id}...</p>
      <Spinner />
    </div>
  );
};

export default SessionDetail;
