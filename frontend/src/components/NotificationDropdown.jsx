import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiCall } from '../services/api';
import { toast } from 'react-hot-toast';
import Button from './UI/Button';

const NotificationDropdown = ({ onMarkAsRead }) => {
  const [notifications, setNotifications] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    setIsLoading(true);
    try {
      const response = await apiCall('/api/notifications');
      if (response.status === 'success') {
        const sortedNotifications = response.data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        setNotifications(sortedNotifications);
      } else {
        toast.error(response.message || 'Failed to fetch notifications.');
      }
    } catch (error) {
      console.error("Error fetching notifications:", error);
      toast.error('An unexpected error occurred while fetching notifications.');
    } finally {
      setIsLoading(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await apiCall(`/api/notifications/${notificationId}/read`, { method: 'POST' });
      // After marking as read, refetch notifications and update parent count
      fetchNotifications();
      onMarkAsRead(); 
    } catch (error) {
      console.error("Error marking notification as read:", error);
      toast.error('Failed to mark notification as read.');
    }
  };

  const handleViewSession = (notification) => {
    if (!notification.read) {
        markAsRead(notification.id);
    }
    navigate(`/session/${notification.session_id}`);
  };

  const handleSnakeIt = async (notification) => {
    try {
      const response = await apiCall(`/api/surf-sessions/${notification.session_id}/snake`, { method: 'POST' });
      if (response.status === 'success') {
        toast.success('Session snaked successfully! Redirecting to edit.');
        if (!notification.read) {
            markAsRead(notification.id);
        }
        navigate(`/session/${response.data.new_session_id}/edit`);
      } else {
        toast.error(response.message || 'Failed to snake session.');
      }
    } catch (error) {
      console.error("Error snaking session:", error);
      toast.error('An unexpected error occurred while snaking session.');
    }
  };

  return (
    <div className="absolute right-0 mt-2 w-80 bg-white rounded-md shadow-lg py-1 z-30 max-h-96 overflow-y-auto">
      <div className="px-4 py-2 text-lg font-bold text-gray-900 border-b">Notifications</div>
      {isLoading ? (
        <div className="px-4 py-2 text-gray-500">Loading...</div>
      ) : notifications.length === 0 ? (
        <div className="px-4 py-2 text-gray-500">No new alerts.</div>
      ) : (
        <div>
          {notifications.map((notification) => (
            <div key={notification.id} className={`px-4 py-3 border-b hover:bg-gray-100 ${notification.read ? 'opacity-60' : ''}`}>
              <p className="text-sm text-gray-800">
                <span className="font-semibold">{notification.sender_display_name}</span> tagged you in their session:
              </p>
              <p className="font-semibold text-blue-600">
                {notification.session_title}
              </p>
              <div className="flex space-x-2 mt-2">
                <Button onClick={() => handleViewSession(notification)} size="sm" className="flex-1">
                  View
                </Button>
                <Button onClick={() => handleSnakeIt(notification)} variant="secondary" size="sm" className="flex-1">
                  Snake It
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default NotificationDropdown;