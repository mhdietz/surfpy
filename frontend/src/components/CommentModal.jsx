import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { postComment } from '../services/comments'; // Import postComment
import Spinner from './UI/Spinner'; // Assuming you have a Spinner component

const CommentModal = ({ sessionId, sessionTitle, comments = [], onClose, onCommentPosted, loading }) => {
  const [commentText, setCommentText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const maxCharLimit = 500;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!commentText.trim()) return;

    setIsSubmitting(true);
    setSubmitError(null);
    try {
      await postComment(sessionId, commentText);
      setCommentText(''); // Clear input after submission
      onCommentPosted(); // Callback to refresh comments in parent
    } catch (error) {
      console.error('Error posting comment:', error);
      setSubmitError(error.message || 'Failed to post comment.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-40 flex justify-center items-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
        <div className="p-4 border-b flex justify-between items-center">
          <h2 className="text-lg font-semibold">{sessionTitle || "Session Comments"}</h2>
          <button onClick={onClose} className="text-2xl font-bold">&times;</button>
        </div>

        <div className="p-4 max-h-80 overflow-y-auto">
          {loading ? (
            <div className="flex justify-center items-center h-full">
              <Spinner />
            </div>
          ) : comments.length > 0 ? (
            <ul>
              {comments.map((comment) => (
                <li key={comment.comment_id} className="mb-4 pb-2 border-b last:mb-0 last:pb-0 last:border-b-0">
                  <div className="flex items-center text-sm mb-1">
                    <Link to={`/journal/${comment.user_id}`} className="font-semibold text-blue-600 hover:underline">
                      {comment.display_name || 'Anonymous'}
                    </Link>
                    <span className="text-gray-500 ml-2 text-xs">
                      {new Date(comment.created_at).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-gray-700 text-sm">{comment.comment_text}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 text-center">No comments yet. Be the first to comment!</p>
          )}
          {submitError && <p className="text-red-500 text-sm mt-2">{submitError}</p>}
        </div>

        <form onSubmit={handleSubmit} className="p-4 border-t">
          <textarea
            className="w-full p-2 border rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows="3"
            placeholder="Add a comment..."
            value={commentText}
            onChange={(e) => setCommentText(e.target.value)}
            maxLength={maxCharLimit}
            disabled={isSubmitting}
          ></textarea>
          <div className="flex justify-between items-center mt-2">
            <span className={`text-sm ${commentText.length > maxCharLimit - 50 ? 'text-red-600' : 'text-gray-500'}`}>
              {commentText.length}/{maxCharLimit}
            </span>
            <button
              type="submit"
              className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-md disabled:bg-blue-300"
              disabled={!commentText.trim() || commentText.length > maxCharLimit || isSubmitting}
            >
              {isSubmitting ? 'Posting...' : 'Post Comment'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CommentModal;
