import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import UserSearch from './UserSearch';
import Logo from './UI/Logo'; // Import the Logo component
import AddToHomeScreenPrompt from './UI/AddToHomeScreenPrompt';

const Navigation = () => {
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  const getLinkClasses = (path) => {
    const baseClasses = "flex flex-col items-center hover:text-blue-600"; // Base styles without color
    const isActive = location.pathname.startsWith(path);

    const activeClasses = "text-blue-600 font-bold";   // Active state: blue and bold
    const inactiveClasses = "text-gray-600"; // Inactive state: gray

    return `${baseClasses} ${isActive ? activeClasses : inactiveClasses}`;
  };

  const handleLogout = () => {
    logout();
    setIsProfileOpen(false);
  };

  return (
    <>
      {/* Top Header */}
      <header className="fixed top-0 left-0 w-full bg-white shadow-md p-4 z-20">
        <div className="container mx-auto flex justify-between items-center">
          {/* Left: Logo and Title */}
          <Link to="/journal/me" className="flex items-center space-x-2 text-blue-600">
            <Logo className="h-8 w-8" />
            <h1 className="text-2xl font-bold">slapp</h1>
          </Link>

          {/* Right: Search and Profile */}
          <div className="flex items-center space-x-4">
            <button onClick={() => setIsSearchOpen(true)} className="text-gray-600 hover:text-blue-600">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>

            {isAuthenticated ? (
              <div className="relative">
                <button onClick={() => setIsProfileOpen(!isProfileOpen)} className="text-gray-600 hover:text-blue-600">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h.01M12 12h.01M19 12h.01" />
                  </svg>
                </button>
                <div className={`absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 ${isProfileOpen ? 'block' : 'hidden'}`}>
                  <Link to="/about" className="w-full text-left block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                    About
                  </Link>
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
          {/* Feed */}
          <Link to="/feed" className={getLinkClasses("/feed")}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <span className="text-sm">Feed</span>
          </Link>
          {/* Create Session */}
          <Link to="/create-session" className={getLinkClasses("/create-session")}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm">Create</span>
          </Link>
          {/* My Journal */}
          <Link to="/journal" className={getLinkClasses("/journal")}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v11.494m-5.25-8.494v11.494l5.25-2.625 5.25 2.625V6.253l-5.25-2.625-5.25 2.625z" />
            </svg>
            <span className="text-sm">Surf Log</span>
          </Link>
        </div>
      </nav>

      {/* User Search Modal */}
      {isSearchOpen && <UserSearch onClose={() => setIsSearchOpen(false)} />}

      {/* Add to Home Screen Prompt */}
      <AddToHomeScreenPrompt />
    </>
  );
};

export default Navigation;