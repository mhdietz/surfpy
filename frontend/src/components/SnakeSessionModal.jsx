import React, { useState, useEffect } from 'react';
import { apiCall } from '../services/api';
import Card from './UI/Card';
import Input from './UI/Input';
import Button from './UI/Button';
import { toast } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { toZonedTime, format } from 'date-fns-tz';

const SnakeSessionModal = ({ originalSession, isOpen, onClose, onSessionSnaked }) => {
  const navigate = useNavigate();
  const [sessionName, setSessionName] = useState('');
  const [funRating, setFunRating] = useState('5');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Initialize form state when originalSession changes
  useEffect(() => {
    if (originalSession) {
      setSessionName(originalSession.session_name || '');
      setFunRating('5'); // Default to 5
      setNotes(''); // Default to empty
    }
  }, [originalSession]);

  if (!isOpen || !originalSession) return null;

  const timeZone = originalSession.location_timezone || 'UTC';
  
  const getFormattedDateTime = () => {
    if (!originalSession.session_started_at) return { date: 'N/A', time: 'N/A' };
    
    try {
        const zonedStart = toZonedTime(new Date(originalSession.session_started_at), timeZone);
        const zonedEnd = originalSession.session_ended_at 
            ? toZonedTime(new Date(originalSession.session_ended_at), timeZone) 
            : null;

        return {
            date: format(zonedStart, 'MMMM d, yyyy', { timeZone }),
            time: `${format(zonedStart, 'h:mm a', { timeZone })} - ${zonedEnd ? format(zonedEnd, 'h:mm a', { timeZone }) : '?'}`
        };
    } catch (e) {
        return { date: 'Error', time: 'Error' };
    }
  };

  const { date, time } = getFormattedDateTime();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);

    try {
      // 1. Call the snake endpoint to create the copy with surf data
      const snakeResponse = await apiCall(`/api/surf-sessions/${originalSession.id}/snake`, {
        method: 'POST'
      });

      if (snakeResponse.status !== 'success') {
        throw new Error(snakeResponse.message || "Failed to snake session.");
      }

      const newSessionId = snakeResponse.data.new_session_id;

      // 2. Call the update endpoint to set the user's specific details
      const updatePayload = {
        session_name: sessionName,
        fun_rating: parseFloat(funRating),
        session_notes: notes
        // Note: We don't send date/time/location/tagged_users, so they remain as copied
      };

      const updateResponse = await apiCall(`/api/surf-sessions/${newSessionId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatePayload),
      });

      if (updateResponse.status === 'success') {
        toast.success("Session snaked successfully!");
        if (onSessionSnaked) onSessionSnaked();
        onClose();
        navigate(`/session/${newSessionId}`);
      } else {
        throw new Error(updateResponse.message || "Failed to update session details.");
      }

    } catch (error) {
      console.error("Error snaking session:", error);
      toast.error(error.message || "An unexpected error occurred.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="p-4 border-b flex justify-between items-center bg-gray-50 rounded-t-lg">
          <h2 className="text-xl font-bold text-gray-900">Snake Session</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-2xl font-bold leading-none">&times;</button>
        </div>
        
        <div className="p-6">
            <div className="mb-6 bg-blue-50 border border-blue-100 p-4 rounded-md text-sm text-blue-800">
                <p>Snaking this session will copy the exact surf conditions (swell, wind, tide) from <strong>{originalSession.location}</strong>.</p>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6 text-sm">
                <div>
                    <span className="block font-medium text-gray-500 uppercase tracking-wide text-xs">Date</span>
                    <span className="block text-gray-900 font-semibold">{date}</span>
                </div>
                <div>
                    <span className="block font-medium text-gray-500 uppercase tracking-wide text-xs">Time</span>
                    <span className="block text-gray-900 font-semibold">{time}</span>
                </div>
                <div className="col-span-2">
                    <span className="block font-medium text-gray-500 uppercase tracking-wide text-xs">Location</span>
                    <span className="block text-gray-900 font-semibold">{originalSession.location}</span>
                </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
            <div>
                <label htmlFor="snake_session_name" className="block text-sm font-medium text-gray-700">Title</label>
                <Input 
                    type="text" 
                    id="snake_session_name" 
                    value={sessionName} 
                    onChange={(e) => setSessionName(e.target.value)} 
                    placeholder={originalSession.session_name} // Placeholder shows original title
                />
            </div>

            <div>
                <label htmlFor="snake_fun_rating" className="block text-sm font-medium text-gray-700">Stoke</label>
                <div className="flex items-center space-x-4">
                <Input 
                    type="range" 
                    id="snake_fun_rating" 
                    min="1" 
                    max="10" 
                    step="0.25" 
                    value={funRating} 
                    onChange={(e) => setFunRating(e.target.value)}
                    className="flex-grow"
                />
                <span className="text-lg font-semibold text-gray-900 w-16 text-right">{parseFloat(funRating).toFixed(2)}</span>
                </div>
            </div>

            <div>
                <label htmlFor="snake_notes" className="block text-sm font-medium text-gray-700">Notes</label>
                <Input 
                    as="textarea" 
                    id="snake_notes" 
                    value={notes} 
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Add your own notes..."
                ></Input>
            </div>

            <div className="flex justify-end space-x-3 pt-4">
                <Button variant="secondary" onClick={onClose} type="button" disabled={isSubmitting}>
                    Cancel
                </Button>
                <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Creating...' : 'Confirm Snake'}
                </Button>
            </div>
            </form>
        </div>
      </div>
    </div>
  );
};

export default SnakeSessionModal;
