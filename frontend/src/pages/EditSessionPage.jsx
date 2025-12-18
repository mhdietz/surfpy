import React, { useState, useEffect } from 'react';
import { formatInTimeZone } from 'date-fns-tz';
import { apiCall, getSpots } from '../services/api'; // Import getSpots
import Card from '../components/UI/Card';
import Input from '../components/UI/Input';
import Button from '../components/UI/Button';
import { toast } from 'react-hot-toast';
import { useNavigate, useParams } from 'react-router-dom';
import Select from 'react-select'; // Import react-select

function EditSessionPage() {
  const navigate = useNavigate();
  const { id } = useParams(); // Get session ID from URL

  // Form states
  const [date, setDate] = useState('');
  const [location, setLocation] = useState('');
  const [sessionName, setSessionName] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [funRating, setFunRating] = useState('');
  const [notes, setNotes] = useState('');

  // Other states
  const [spotOptions, setSpotOptions] = useState([]); // For react-select
  const [isLoadingSpots, setIsLoadingSpots] = useState(true); // Differentiated loading state
  const [isLoading, setIsLoading] = useState(true);
  const [taggedUsers, setTaggedUsers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch spots on component mount
  useEffect(() => {
    const fetchSpots = async () => {
      setIsLoadingSpots(true);
      try {
        const spots = await getSpots();
        const options = spots.map(spot => ({
          value: spot.slug,
          label: `${spot.name} (${spot.region}, ${spot.country})${spot.has_surf_data ? '' : ' [No surf data]'}`
        }));
        setSpotOptions(options);
      } catch (error) {
        console.error("Failed to fetch spots:", error);
        toast.error("Failed to load surf spots.");
      } finally {
        setIsLoadingSpots(false);
      }
    };

    fetchSpots();
  }, []);

  // Fetch existing session data on component mount
  useEffect(() => {
    const fetchSessionData = async () => {
      setIsLoading(true);
      try {
        const response = await apiCall(`/api/surf-sessions/${id}`);
        if (response.status === 'success') {
          const session = response.data;
          
          const tz = session.location_timezone || 'UTC'; // Fallback to UTC

          setDate(formatInTimeZone(session.session_started_at, tz, 'yyyy-MM-dd'));
          setStartTime(formatInTimeZone(session.session_started_at, tz, 'HH:mm'));
          setEndTime(formatInTimeZone(session.session_ended_at, tz, 'HH:mm'));
          
          setLocation(session.location_slug);
          setSessionName(session.session_name);
          setFunRating(session.fun_rating.toString());
          setNotes(session.session_notes);
          const taggedParticipants = session.participants.filter(
            p => p.user_id !== session.user_id
          );
          setTaggedUsers(taggedParticipants || []);
        } else {
          toast.error(response.message || 'Failed to fetch session data.');
        }
      } catch (error) {
        toast.error('An error occurred while fetching session data.');
        console.error(error);
      } finally {
        setIsLoading(false);
      }
    };

    if (id) {
      fetchSessionData();
    }
  }, [id]);

  // Debounced user search
  useEffect(() => {
    if (searchQuery.length < 2) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }

    setIsSearching(true);
    const debounceTimeout = setTimeout(async () => {
      try {
        const response = await apiCall(`/api/users/search?q=${searchQuery}`);
        const filteredResults = response.data.filter(resultUser => 
          !taggedUsers.some(taggedUser => taggedUser.user_id === resultUser.user_id)
        );
        setSearchResults(filteredResults || []);
      } catch (error) {
        console.error("Failed to search users:", error);
        toast.error("Failed to search users.");
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => clearTimeout(debounceTimeout);
  }, [searchQuery, taggedUsers]);

  const handleSelectUser = (user) => {
    if (!taggedUsers.some(taggedUser => taggedUser.user_id === user.user_id)) {
      setTaggedUsers([...taggedUsers, user]);
      setSearchQuery('');
      setSearchResults([]);
    }
  };

  const handleRemoveUser = (userId) => {
    setTaggedUsers(taggedUsers.filter(user => user.user_id !== userId));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);

    if (!date || !location || !sessionName || !startTime || !endTime || !funRating) {
      toast.error("Please fill in all required fields.");
      setIsSubmitting(false);
      return;
    }

    if (new Date(`2000-01-01T${endTime}`) <= new Date(`2000-01-01T${startTime}`)) {
      toast.error("End time must be after start time.");
      setIsSubmitting(false);
      return;
    }

    try {
      const payload = {
        date: date,
        location: location,
        session_name: sessionName,
        time: startTime,
        end_time: endTime,
        fun_rating: parseFloat(funRating),
        session_notes: notes,
        tagged_users: taggedUsers.map(user => user.user_id),
      };

      const response = await apiCall(`/api/surf-sessions/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.status === 'success') {
        toast.success("Surf session updated successfully!");
        navigate(`/session/${id}`, { state: { updatedSession: response.data }, replace: true }); 
      } else {
        toast.error(response.message || "Failed to update surf session.");
      }
    } catch (error) {
      console.error("Error updating surf session:", error);
      toast.error(error.message || "An unexpected error occurred.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return <div className="text-center p-4">Loading session data...</div>;
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold text-center mb-6 text-gray-900">Edit Session</h1>
      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="date" className="block text-sm font-medium text-gray-700">Date</label>
            <Input type="date" id="date" name="date" value={date} onChange={(e) => setDate(e.target.value)} />
          </div>

          <div>
            <label htmlFor="location" className="block text-sm font-medium text-gray-700">Location</label>
            <Select
              id="location"
              name="location"
              options={spotOptions}
              isLoading={isLoadingSpots}
              onChange={(selectedOption) => setLocation(selectedOption ? selectedOption.value : '')}
              isClearable
              placeholder="Search for a surf spot..."
              value={spotOptions.find(option => option.value === location)}
              className="mt-1"
              classNamePrefix="react-select"
              styles={{
                input: (base) => ({ ...base, 'input:focus': { boxShadow: 'none' } }),
              }}
            />
          </div>

          <div>
            <label htmlFor="session_name" className="block text-sm font-medium text-gray-700">Title</label>
            <Input type="text" id="session_name" name="session_name" placeholder="e.g., Fun morning session" value={sessionName} onChange={(e) => setSessionName(e.target.value)} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="start_time" className="block text-sm font-medium text-gray-700">Start Time</label>
              <Input type="time" id="start_time" name="start_time" value={startTime} onChange={(e) => setStartTime(e.target.value)} />
            </div>
            <div>
              <label htmlFor="end_time" className="block text-sm font-medium text-gray-700">End Time</label>
              <Input type="time" id="end_time" name="end_time" value={endTime} onChange={(e) => setEndTime(e.target.value)} />
            </div>
          </div>

          <div>
            <label htmlFor="fun_rating" className="block text-sm font-medium text-gray-700">Fun Rating</label>
            <div className="flex items-center space-x-4">
              <Input 
                type="range" 
                id="fun_rating" 
                name="fun_rating" 
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
            <label htmlFor="notes" className="block text-sm font-medium text-gray-700">Notes</label>
            <Input as="textarea" id="notes" name="notes" placeholder="How were the waves?" value={notes} onChange={(e) => setNotes(e.target.value)}></Input>
          </div>

          <div>
            <label htmlFor="user_search" className="block text-sm font-medium text-gray-700">Tag Surfers</label>
            <Input 
              type="text" 
              id="user_search" 
              name="user_search" 
              placeholder="Search by name or email..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="mt-1"
            />
            {isSearching && <p className="text-gray-400 text-sm mt-1">Searching...</p>}
            {searchResults.length > 0 && (
              <div className="mt-2 bg-gray-700 border border-gray-600 rounded-md shadow-lg max-h-48 overflow-y-auto">
                {searchResults.map(user => (
                  <button 
                    key={user.user_id} 
                    type="button" 
                    onClick={() => handleSelectUser(user)}
                    className="block w-full text-left px-4 py-2 text-white hover:bg-gray-600"
                  >
                    {user.display_name || user.email}
                  </button>
                ))}
              </div>
            )}
            <div className="mt-2 flex flex-wrap gap-2">
              {taggedUsers.map(user => (
                <div key={user.user_id} className="flex items-center bg-gray-600 text-white text-sm font-medium pl-2 pr-1 py-1 rounded-full">
                  <span>{user.display_name}</span>
                  <button type="button" onClick={() => handleRemoveUser(user.user_id)} className="ml-2 text-gray-300 hover:text-white">
                    &times;
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-4 flex space-x-4">
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? 'Updating...' : 'Update Session'}
            </Button>
            <Button type="button" variant="secondary" className="w-full" onClick={() => navigate(`/session/${id}`)}>
              Cancel
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}

export default EditSessionPage;