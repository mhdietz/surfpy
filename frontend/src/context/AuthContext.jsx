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
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = authService.getToken();
    if (token) {
      const decoded = parseJwt(token);
      // Check if token is expired
      if (decoded && decoded.exp * 1000 > Date.now()) {
        // In a real app, you'd fetch the user profile here
        // For now, we'll just use the decoded token data
        setUser({ id: decoded.sub }); 
        setIsAuthenticated(true);
      } else {
        // Token is expired, remove it
        authService.logout();
      }
    }
    setLoading(false);
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
    login,
    signup,
    logout,
  };

  // Don't render children until the initial auth check is complete
  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => {
  return useContext(AuthContext);
};
