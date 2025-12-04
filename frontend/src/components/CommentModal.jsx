import React, { useState, useEffect } from 'react';
import { apiCall } from '../services/api';
import { Spinner } from './UI/Spinner';

// Helper to format date
const formatDate = (isoString) => {
  if (!isoString) return '';
  const date = new Date(isoString);
  // Example format: "Dec 4, 10:30 AM"
  return date.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
};

const CommentModal = ({ session_id, onClose }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const MAX_COMMENT_LENGTH = 500;

  useEffect(() => {
    const fetchComments = async () => {
      try {
        setIsLoading(true);
        const res = await apiCall(`/surf-sessions/${session_id}/comments`);
        setComments(res.data.comments || []);
      } catch (err) {
        setError('Failed to load comments.');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchComments();
  }, [session_id]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newComment.trim() || isSubmitting) return;

    try {
      setIsSubmitting(true);
      const res = await apiCall(`/surf-sessions/${session_id}/comments`, {
        method: 'POST',
        body: JSON.stringify({ comment_text: newComment.trim() }),
      });
      // Add new comment to the top of the list for immediate feedback
      setComments(prev => [...prev, res.data]);
      setNewComment('');
    } catch (err) {
      setError('Failed to post comment.');
      console.error(err);
      // In a real app, you'd use a toast notification here
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 z-40 flex justify-center items-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-lg flex flex-col" style={{maxHeight: '80vh'}}>
        {/* Header */}
        <div className="p-4 border-b flex justify-between items-center flex-shrink-0">
          <h2 className="text-lg font-semibold">Comments</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-800 text-2xl font-bold">&times;</button>
        </div>

        {/* Body - Comments List */}
        <div className="p-4 flex-grow overflow-y-auto">
          {isLoading ? (
            <div className="flex justify-center p-8">
              <Spinner />
            </div>
          ) : error ? (
            <p className="text-red-500 text-center">{error}</p>
          ) : comments.length > 0 ? (
            <ul className="space-y-4">
              {comments.map(comment => (
                <li key={comment.comment_id} className="flex items-start space-x-3">
                   <div className="flex-shrink-0 w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                     <span className="text-lg font-bold text-gray-500">{comment.display_name.charAt(0)}</span>
                   </div>
                   <div className="flex-1">
                     <div className="bg-gray-100 rounded-lg p-3">
                        <p className="text-sm text-gray-800">{comment.comment_text}</p>
                     </div>
                     <div className="pl-3 mt-1 flex items-center space-x-2 text-xs text-gray-500">
                        <span className="font-semibold">{comment.display_name}</span>
                        <span>&middot;</span>
                        <span>{formatDate(comment.created_at)}</span>
                     </div>
                   </div>
                </li>
              ))}
            </ul>
          ) : (
             <p className="text-gray-500 text-center py-8">No comments yet. Be the first!</p>
          )}
        </div>

        {/* Footer - Comment Form */}
        <div className="p-4 border-t flex-shrink-0">
          <form onSubmit={handleSubmit}>
            <div className="relative">
                <textarea
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Write a comment..."
                    className="w-full p-2 pr-16 border rounded-lg focus:ring-blue-500 focus:border-blue-500 transition"
                    rows="3"
                    maxLength={MAX_COMMENT_LENGTH}
                    disabled={isSubmitting}
                />
                <div className="absolute bottom-2 right-2 text-xs text-gray-400">
                    {newComment.length}/{MAX_COMMENT_LENGTH}
                </div>
            </div>
            <button 
                type="submit" 
                className="mt-2 w-full bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 disabled:bg-blue-300"
                disabled={!newComment.trim() || isSubmitting}
            >
              {isSubmitting ? 'Posting...' : 'Post Comment'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CommentModal;
