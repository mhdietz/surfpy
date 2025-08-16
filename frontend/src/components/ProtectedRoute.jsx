import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Spinner from './UI/Spinner'; // Import the Spinner

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth(); // Destructure isLoading

  // While the auth state is loading, show a spinner
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Spinner />
      </div>
    );
  }

  // After loading, if the user is not authenticated, redirect to login
  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }

  // If authenticated, render the children components
  return children;
};


export default ProtectedRoute;
