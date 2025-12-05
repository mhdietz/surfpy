import { apiCall } from './api';

/**
 * Fetches all comments for a specific surf session.
 * @param {number} sessionId - The ID of the surf session.
 * @returns {Promise<Array>} A promise that resolves to an array of comment objects.
 */
export const getCommentsForSession = async (sessionId) => {
  console.log(`💬 Fetching comments for session ${sessionId}`);
  try {
    const response = await apiCall(`/api/surf-sessions/${sessionId}/comments`, {
      method: 'GET',
    });
    console.log(`💬 Comments for session ${sessionId}:`, response);
    return response.data.comments; // Corrected to access comments array from response.data
  } catch (error) {
    console.error(`💬 Failed to fetch comments for session ${sessionId}:`, error);
    throw error;
  }
};

/**
 * Posts a new comment to a specific surf session.
 * @param {number} sessionId - The ID of the surf session.
 * @param {string} commentText - The text content of the comment.
 * @returns {Promise<Object>} A promise that resolves to the newly created comment object.
 */
export const postComment = async (sessionId, commentText) => {
  console.log(`💬 Posting comment to session ${sessionId}: "${commentText}"`);
  try {
    const response = await apiCall(`/api/surf-sessions/${sessionId}/comments`, {
      method: 'POST',
      body: JSON.stringify({ comment_text: commentText }),
    });
    console.log(`💬 Comment posted to session ${sessionId}:`, response);
    return response; // Assuming the API returns the created comment object
  } catch (error) {
    console.error(`💬 Failed to post comment to session ${sessionId}:`, error);
    throw error;
  }
};
