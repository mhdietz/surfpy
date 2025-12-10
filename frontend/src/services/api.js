import { API_BASE_URL } from '../config/api';
import { getToken, logout } from './auth'; // Import logout

/**
 * A centralized API call function.
 * @param {string} endpoint - The API endpoint to call (e.g., '/api/surf-sessions').
 * @param {object} [options={}] - The options for the fetch call (e.g., method, body, headers).
 * @returns {Promise<any>} The JSON response from the API.
 * @throws {Error} Throws an error if the API response is not ok.
 */
export const apiCall = async (endpoint, options = {}) => {
  const token = getToken();

  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  // Check for 401 Unauthorized specifically
  if (response.status === 401) {
    logout(); // Clear the token
    window.location.assign('/auth/login'); // Redirect to login
    throw new Error('Session expired. Please log in again.');
  }

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message || `API Error: ${response.status}`);
  }

  return data;
};

/**
 * Toggle shaka reaction for a surf session
 * @param {number} sessionId - The ID of the session to toggle shaka for
 * @returns {Promise<object>} Response containing updated shaka count
 */
export const toggleShaka = async (sessionId) => {
  console.log(`🤙 Toggling shaka for session ${sessionId}`);
  
  try {
    const response = await apiCall(`/api/surf-sessions/${sessionId}/shaka`, {
      method: 'POST'
    });
    
    console.log(`🤙 Shaka toggle response:`, response);
    return response;
  } catch (error) {
    console.error(`🤙 Shaka toggle error for session ${sessionId}:`, error);
    throw error;
  }
};

/**
 * Get all users who have reacted with shakas for a specific session
 * @param {number} sessionId - The ID of the session
 * @returns {Promise<array>} Array of users who have reacted
 */
export const getSessionShakas = async (sessionId) => {
  console.log(`🤙 Fetching all shakas for session ${sessionId}`);
  
  try {
    const response = await apiCall(`/api/surf-sessions/${sessionId}/shakas`, {
      method: 'GET'
    });
    
    console.log(`🤙 Session shakas response:`, response);
    return response.data; // Return the array directly
  } catch (error) {
    console.error(`🤙 Failed to fetch session shakas for session ${sessionId}:`, error);
    throw error;
  }
};

/**
 * Delete a surf session
 * @param {number} sessionId - The ID of the session to delete
 * @returns {Promise<object>} Response from the API
 */
export const deleteSession = async (sessionId) => {
  console.log(`🗑️ Deleting session ${sessionId}`);
  
  try {
    const response = await apiCall(`/api/surf-sessions/${sessionId}`, {
      method: 'DELETE'
    });
    
    console.log(`🗑️ Delete session response:`, response);
    return response;
  } catch (error) {
    console.error(`🗑️ Failed to delete session ${sessionId}:`, error);
    throw error;
  }
};

/**
 * Get all surf spots for the typeahead component.
 * @returns {Promise<array>} Array of surf spot objects.
 */
export const getSpots = async () => {
  console.log('Fetching all surf spots...');
  try {
    const response = await apiCall('/api/spots', {
      method: 'GET'
    });
    console.log('Surf spots response:', response);
    return response.data; // Return the array directly
  } catch (error) {
    console.error('Failed to fetch surf spots:', error);
    throw error;
  }
};
