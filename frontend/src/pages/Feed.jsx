import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Button from '../components/UI/Button';
import Card from '../components/UI/Card';
import SessionTile from '../components/SessionTile';
import { mockSession } from '../utils/mockData.js';

const Feed = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/auth/login');
  };

  return (
    <div className="bg-gray-100 min-h-screen py-8">
      <main className="max-w-2xl mx-auto space-y-6 px-4">
        <SessionTile session={mockSession} />

        <Card>
        <div className="text-center">
          <h2 className="text-3xl font-bold">Welcome!</h2>
          {user && <p className="mt-2 text-gray-600">You are logged in.</p>}
        </div>
        <Button 
          onClick={handleLogout} 
          variant="destructive"
        >
          Logout
        </Button>
      </Card>
      </main>
    </div>
  );
};

export default Feed;