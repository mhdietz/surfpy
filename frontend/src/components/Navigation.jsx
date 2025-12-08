import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiCall } from '../services/api';
import UserSearch from './UserSearch';
import Logo from './UI/Logo';
import AddToHomeScreenPrompt from './UI/AddToHomeScreenPrompt';
import NotificationDropdown from './NotificationDropdown';

const Navigation = () => {
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchCount = async () => {
    if (!isAuthenticated) {
      setUnreadCount(0);
      return;
    }
    try {
      const response = await apiCall('/api/notifications/count');
      if (response.status === 'success') {
        setUnreadCount(response.data.unread_count);
      }
    } catch (error) {
      console.error("Failed to fetch notification count:", error);
    }
  };

  useEffect(() => {
    let intervalId;
    fetchCount(); 
    if (isAuthenticated) {
      intervalId = setInterval(fetchCount, 60000); 
    }
    return () => clearInterval(intervalId);
  }, [isAuthenticated]);

  useEffect(() => {
    // Close dropdowns when navigating
    setIsNotificationsOpen(false);
    setIsProfileOpen(false);
  }, [location.pathname]);

  const getLinkClasses = (path) => {
    const baseClasses = "flex flex-col items-center hover:text-blue-600";
    const isActive = location.pathname.startsWith(path);
    const activeClasses = "text-blue-600 font-bold";
    const inactiveClasses = "text-gray-600";
    return `${baseClasses} ${isActive ? activeClasses : inactiveClasses}`;
  };

  const handleLogout = () => {
    logout();
    setIsProfileOpen(false);
  };

  return (
    <>
      <header className="fixed top-0 left-0 w-full bg-white shadow-md p-4 z-20">
        <div className="container mx-auto flex justify-between items-center">
          <Link to="/feed" className="flex items-center space-x-2 text-blue-600">
            <Logo className="h-8 w-8" />
            <h1 className="text-2xl font-bold">slapp</h1>
          </Link>

          {isAuthenticated && (
            <div className="flex items-center space-x-4">
              <button onClick={() => setIsSearchOpen(true)} className="text-gray-600 hover:text-blue-600">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>

              <div className="relative">
                <button onClick={() => setIsNotificationsOpen(!isNotificationsOpen)} className="text-gray-600 hover:text-blue-600 relative">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                  {unreadCount > 0 && (
                    <span className="absolute -top-2 -right-2 block h-5 w-5 rounded-full bg-red-600 text-white text-xs flex items-center justify-center">
                      {unreadCount}
                    </span>
                  )}
                </button>
                {isNotificationsOpen && <NotificationDropdown onMarkAsRead={fetchCount} />}
              </div>

              <div className="relative">
                <button onClick={() => setIsProfileOpen(!isProfileOpen)} className="text-gray-600 hover:text-blue-600">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={4}>
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
            </div>
          )}
          {!isAuthenticated && <Link to="/auth/login" className="text-gray-600 hover:text-blue-600">Login</Link>}
        </div>
      </header>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 w-full bg-white shadow-lg py-2 px-4 z-10">
        <div className="container mx-auto flex justify-around items-center">
          <Link to="/feed" className={getLinkClasses("/feed")}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <span className="text-sm">Feed</span>
          </Link>
          <Link to="/create-session" className={getLinkClasses("/create-session")}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm">Create</span>
          </Link>
          <Link to="/journal/me" className={getLinkClasses("/journal")}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v11.494m-5.25-8.494v11.494l5.25-2.625 5.25 2.625V6.253l-5.25-2.625-5.25 2.625z" />
            </svg>
            <span className="text-sm">Surf Log</span>
          </Link>
        </div>
      </nav>

      {isSearchOpen && <UserSearch onClose={() => setIsSearchOpen(false)} />}
      <AddToHomeScreenPrompt />
    </>
  );
};

export default Navigation;