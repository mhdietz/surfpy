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
      <nav className="fixed bottom-0 left-0 w-full bg-white shadow-lg py-2 px-4 z-10">
        <div className="container mx-auto flex justify-around items-center">
          {/* My Journal */}
          <Link to="/journal" className={getLinkClasses("/journal")}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v11.494m-5.25-8.494v11.494l5.25-2.625 5.25 2.625V6.253l-5.25-2.625-5.25 2.625z" />
            </svg>
            <span className="text-xs">Surf Log</span>
          </Link>
          {/* Create Session */}
          <Link to="/create-session" className={getLinkClasses("/create-session")}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-xs">Create</span>
          </Link>
          {/* Feed */}
          <Link to="/feed" className={getLinkClasses("/feed")}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <span className="text-xs">Feed</span>
          </Link>
        </div>
      </nav>

      {/* User Search Modal */}
      {isSearchOpen && <UserSearch onClose={() => setIsSearchOpen(false)} />}
    </>
  );
};

export default Navigation;