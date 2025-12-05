import React, { useState, useEffect } from 'react';
import { getCommentsForSession, postComment } from '../services/comments';

const TestComments = () => {
  const [comments, setComments] = useState([]);
  const [newCommentText, setNewCommentText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // NOTE: Replace with an actual session ID from your database for testing.
  // You might also want to make this configurable or pass it as a prop.
  const TEST_SESSION_ID = 3626; 

  const fetchComments = async () => {
    setLoading(true);
    setError(null);
    try {
      const fetchedComments = await getCommentsForSession(TEST_SESSION_ID);
      setComments(fetchedComments);
    } catch (err) {
      setError(err.message || 'Failed to fetch comments');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComments();
  }, []);

  const handlePostComment = async () => {
    if (!newCommentText.trim()) return;

    setLoading(true);
    setError(null);
    try {
      await postComment(TEST_SESSION_ID, newCommentText);
      setNewCommentText('');
      await fetchComments(); // Re-fetch comments after posting
    } catch (err) {
      setError(err.message || 'Failed to post comment');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 border rounded-md shadow-md bg-gray-50 max-w-md mx-auto my-8">
      <h3 className="text-xl font-semibold mb-4">Test Comments for Session {TEST_SESSION_ID}</h3>

      {loading && <p className="text-blue-600">Loading...</p>}
      {error && <p className="text-red-600">Error: {error}</p>}

      <div className="mb-4">
        <h4 className="text-lg font-medium mb-2">Existing Comments:</h4>
        {comments.length > 0 ? (
          <ul>
            {comments.map((comment) => (
              <li key={comment.comment_id} className="mb-2 p-2 bg-white border rounded-md">
                <p className="text-sm font-semibold">{comment.display_name || 'Anonymous'}</p>
                <p className="text-gray-700">{comment.comment_text}</p>
                <span className="text-xs text-gray-500">{new Date(comment.created_at).toLocaleString()}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-600">No comments yet. Post one below!</p>
        )}
      </div>

      <div className="border-t pt-4">
        <h4 className="text-lg font-medium mb-2">Post a New Comment:</h4>
        <textarea
          className="w-full p-2 border rounded-md resize-y focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows="3"
          placeholder="Type your comment here..."
          value={newCommentText}
          onChange={(e) => setNewCommentText(e.target.value)}
          disabled={loading}
        ></textarea>
        <button
          className="mt-2 bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-md disabled:bg-blue-300"
          onClick={handlePostComment}
          disabled={loading || !newCommentText.trim()}
        >
          Post Comment
        </button>
      </div>
    </div>
  );
};

export default TestComments;
