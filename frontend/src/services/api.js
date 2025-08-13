import { API_BASE_URL } from '../config/api';
import { getToken } from './auth';

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
