import React, { createContext, useState, useContext, useEffect } from 'react';
import * as authService from '../services/auth';

// Helper function to parse JWT
const parseJwt = (token) => {
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch (e) {
    return null;
  }
};

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const verifyUser = async () => {
      const token = authService.getToken();
      if (token) {
        try {
          // Verify token with the backend and get user profile
          const response = await apiCall('/api/users/me/profile');
          setUser(response.data);
          setIsAuthenticated(true);
        } catch (error) {
          // If token is invalid, logout
          console.error("Session validation failed", error);
          authService.logout();
          setUser(null);
          setIsAuthenticated(false);
        }
      }
      setIsLoading(false);
    };

    verifyUser();
  }, []);

  const login = async (email, password) => {
    const userData = await authService.login(email, password);
    setUser(userData);
    setIsAuthenticated(true);
    return userData;
  };

  const signup = async (email, password, firstName, lastName) => {
    const userData = await authService.signup(email, password, firstName, lastName);
    setUser(userData);
    setIsAuthenticated(true);
    return userData;
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  const value = {
    user,
    isAuthenticated,
    isLoading, // Expose isLoading state
    login,
    signup,
    logout,
  };

  // Don't render children until the initial auth check is complete
  return (
    <AuthContext.Provider value={value}>
      {!isLoading && children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => {
  return useContext(AuthContext);
};
