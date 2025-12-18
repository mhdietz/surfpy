import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiCall } from '../services/api';
import { toast } from 'react-hot-toast';
import Button from './UI/Button';
import SnakeSessionModal from './SnakeSessionModal';

const NotificationDropdown = ({ onMarkAsRead }) => {
  const [notifications, setNotifications] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSnakeModalOpen, setIsSnakeModalOpen] = useState(false);
  const [selectedSession, setSelectedSession] = useState(null);
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
      // Fetch the full session details to pass to the modal
      const response = await apiCall(`/api/surf-sessions/${notification.session_id}`);
      
      if (response.status === 'success') {
        setSelectedSession(response.data);
        setIsSnakeModalOpen(true);

        // Mark notification as read immediately (optional, or wait for confirm)
        if (!notification.read) {
            markAsRead(notification.id);
        }
      } else {
        toast.error(response.message || 'Failed to load session details.');
      }
    } catch (error) {
      console.error("Error preparing snake session:", error);
      toast.error('An unexpected error occurred while loading session.');
    }
  };

  return (
    <>
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

      <SnakeSessionModal 
        isOpen={isSnakeModalOpen}
        onClose={() => {
            setIsSnakeModalOpen(false);
            setSelectedSession(null);
        }}
        originalSession={selectedSession}
      />
    </>
  );
};

export default NotificationDropdown;