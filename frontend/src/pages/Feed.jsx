import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Button from '../components/UI/Button';
import Card from '../components/UI/Card';
import SessionsList from '../components/SessionsList';
import PageTabs from '../components/PageTabs'; // Import PageTabs

const Feed = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation(); // For tab handling
  const queryParams = new URLSearchParams(location.search);
  const currentTab = queryParams.get('tab') || 'feed'; // Default to 'feed'

  const feedTabs = [
    { label: 'Feed', path: '/feed' },
    { label: 'Leaderboard', path: '/feed?tab=leaderboard' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/auth/login');
  };

  return (
    <div className="bg-gray-100 min-h-screen py-8"> {/* Adjusted root div */} 
      <main className="max-w-2xl mx-auto space-y-6 px-4 pt-16"> {/* Main content wrapper with pt-16 */} 
        {/* Page Header / Sub-Navigation */}
        <PageTabs tabs={feedTabs} />

        {/* Conditional Content */}
        <div className="w-full bg-white p-6 rounded-lg shadow-md"> {/* Main content card */} 
          {currentTab === 'feed' && (
            <div>
              <h3 className="text-xl font-semibold mb-2">Community Feed</h3>
              <SessionsList /> {/* Render SessionsList for the feed tab */}
            </div>
          )}

          {currentTab === 'leaderboard' && (
            <div>
              <h3 className="text-xl font-semibold mb-2">Community Leaderboard</h3>
              <p>This is a placeholder for the community leaderboard.</p>
              {/* Leaderboard component will go here eventually */}
            </div>
          )}
        </div>

        {/* Original Welcome Card - kept for now, will be removed later */}
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
