import React, { useState } from 'react'; // Import useState
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext'; // Import useAuth
import UserSearch from './UserSearch'; // Import UserSearch

const Navigation = () => {
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth(); // Get auth state
  const [isSearchOpen, setIsSearchOpen] = useState(false); // State for search modal

  const getLinkClasses = (path) => {
    const baseClasses = "flex flex-col items-center text-gray-600 hover:text-blue-600";
    const activeClasses = "text-blue-600 font-bold";
    return `${baseClasses} ${location.pathname === path ? activeClasses : ""}`;
  };

  const handleLogout = () => {
    logout();
    // Optionally navigate to login page after logout
  };

  return (
    <>
      {/* Top Header */}
      <header className="fixed top-0 left-0 w-full bg-white shadow-md p-4 z-20">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold text-blue-600">Surf App</h1>
          {/* User Search and Profile Dropdown */}
          <div className="flex items-center space-x-4">
            {/* User Search Icon */}
            <span onClick={() => setIsSearchOpen(true)} className="text-gray-600 cursor-pointer hover:text-blue-600">🔍 Search</span>

            {/* Profile Dropdown Placeholder */}
            {isAuthenticated ? (
              <div className="relative group pb-2">
                <span className="text-gray-600 cursor-pointer hover:text-blue-600">
                  Hello, {user?.email?.split('@')[0] || 'User'} ▼
                </span>
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 hidden group-hover:block">
                  <Link to="/profile" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Profile</Link>
                  <button onClick={handleLogout} className="w-full text-left block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Logout</button>
                </div>
              </div>
            ) : (
              <Link to="/auth/login" className="text-gray-600 hover:text-blue-600">Login</Link>
            )}
          </div>
        </div>
      </header>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 w-full bg-white shadow-lg p-4 z-10">
        <div className="container mx-auto flex justify-around items-center">
          {/* My Journal */}
          <Link to="/journal" className={getLinkClasses("/journal")}>
            <span>Surf Log</span>
          </Link>
          {/* Create Session */}
          <Link to="/create-session" className={getLinkClasses("/create-session")}>
            <span>Create</span>
          </Link>
          {/* Feed */}
          <Link to="/feed" className={getLinkClasses("/feed")}>
            <span>Feed</span>
          </Link>
        </div>
      </nav>

      {/* User Search Modal */}
      {isSearchOpen && <UserSearch onClose={() => setIsSearchOpen(false)} />}
    </>
  );
};

export default Navigation;