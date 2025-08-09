import { API_BASE_URL } from '../config/api';

/**
 * Logs a user in by sending their credentials to the backend.
 * @param {string} email - The user's email.
 * @param {string} password - The user's password.
 * @returns {Promise<object>} The user data from the backend.
 */
export const login = async (email, password) => {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message || 'Failed to login');
  }

  if (data.data.access_token) {
    localStorage.setItem('access_token', data.data.access_token);
  }

  return data.data.user;
};

/**
 * Signs a new user up and automatically logs them in.
 * @param {string} email - The new user's email.
 * @param {string} password - The new user's password.
 * @param {string} firstName - The new user's first name.
 * @param {string} lastName - The new user's last name.
 * @returns {Promise<object>} The user data from the backend after login.
 */
export const signup = async (email, password, firstName, lastName) => {
  const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ 
      email, 
      password, 
      first_name: firstName, 
      last_name: lastName 
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message || 'Failed to sign up');
  }

  // Automatically log the user in after successful signup
  return await login(email, password);
};

/**
 * Logs the user out by removing the token from local storage.
 */
export const logout = () => {
  localStorage.removeItem('access_token');
};

/**
 * Retrieves the authentication token from local storage.
 * @returns {string|null} The access token or null if it doesn't exist.
 */
export const getToken = () => {
  return localStorage.getItem('access_token');
};
