import React, { useState, useEffect } from 'react';
import { apiCall } from '../services/api';
import Card from '../components/UI/Card';
import Input from '../components/UI/Input';
import Button from '../components/UI/Button';
import { toast } from 'react-hot-toast'; // Import toast for notifications
import { useNavigate } from 'react-router-dom'; // Import useNavigate for redirection

function CreateSessionPage() {
  const navigate = useNavigate();

  // Form states
  const [date, setDate] = useState(() => {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0'); // Month is 0-indexed
    const day = String(today.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  });
  const [location, setLocation] = useState('');
  const [sessionName, setSessionName] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [funRating, setFunRating] = useState('5');
  const [notes, setNotes] = useState('');

  // Other states
  const [locations, setLocations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [taggedUsers, setTaggedUsers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch locations on component mount
  useEffect(() => {
    const fetchLocations = async () => {
      try {
        const response = await apiCall('/api/surf-spots-by-region');
        setLocations(response.data || []);
      } catch (error) {
        console.error("Failed to fetch locations:", error);
        toast.error("Failed to load surf spots.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchLocations();
  }, []);

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
        // Filter out already tagged users from search results
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
    }, 300); // 300ms debounce

    return () => clearTimeout(debounceTimeout);
  }, [searchQuery, taggedUsers]); // Re-run when searchQuery or taggedUsers change

  const handleSelectUser = (user) => {
    // Add user if not already tagged
    if (!taggedUsers.some(taggedUser => taggedUser.user_id === user.user_id)) {
      setTaggedUsers([...taggedUsers, user]);
      setSearchQuery(''); // Clear search input
      setSearchResults([]); // Clear search results
    }
  };

  const handleRemoveUser = (userId) => {
    setTaggedUsers(taggedUsers.filter(user => user.user_id !== userId));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);

    // Basic validation
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
        location: location, // This is the slug
        session_name: sessionName,
        time: startTime,
        end_time: endTime,
        fun_rating: parseFloat(funRating), // Changed from parseInt to parseFloat
        session_notes: notes,
        tagged_users: taggedUsers.map(user => user.user_id) // Send only user IDs
      };

      const response = await apiCall('/api/surf-sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.status === 'success') {
        toast.success("Surf session created successfully!");
        // Redirect to the new session's detail page or journal
        navigate(`/session/${response.data.id}`); 
      } else {
        toast.error(response.message || "Failed to create surf session.");
      }
    } catch (error) {
      console.error("Error creating surf session:", error);
      toast.error(error.message || "An unexpected error occurred.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold text-center mb-1 text-gray-900">Log a session</h1>
      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="date" className="block text-sm font-medium text-gray-700">Date</label>
            <Input type="date" id="date" name="date" value={date} onChange={(e) => setDate(e.target.value)} />
          </div>

          <div>
            <label htmlFor="location" className="block text-sm font-medium text-gray-700">Location</label>
            <Input as="select" id="location" name="location" value={location} onChange={(e) => setLocation(e.target.value)} isPlaceholder={!location}>
              {isLoading ? (
                <option>Loading locations...</option>
              ) : (
                <>
                  <option value="">Select a spot</option>
                  {locations.map(region => (
                    <optgroup key={region.region} label={region.region}>
                      {region.spots.map(spot => (
                        <option key={spot.slug} value={spot.slug}>
                          {spot.name}
                        </option>
                      ))}
                    </optgroup>
                  ))}
                </>
              )}
            </Input>
          </div>

          <div>
            <label htmlFor="session_name" className="block text-sm font-medium text-gray-700">Title</label>
            <Input type="text" id="session_name" name="session_name" placeholder="e.g., Fun morning session" value={sessionName} onChange={(e) => setSessionName(e.target.value)} />
          </div>

          <div>
            <label htmlFor="start_time" className="block text-sm font-medium text-gray-700">Start Time</label>
            <Input type="time" id="start_time" name="start_time" value={startTime} onChange={(e) => setStartTime(e.target.value)} />
          </div>
          <div>
            <label htmlFor="end_time" className="block text-sm font-medium text-gray-700">End Time</label>
            <Input type="time" id="end_time" name="end_time" value={endTime} onChange={(e) => setEndTime(e.target.value)} />
          </div>

          <div>
            <label htmlFor="fun_rating" className="block text-sm font-medium text-gray-700">Stoke</label>
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
              <div className="mt-2 bg-white border border-gray-300 rounded-md shadow-lg max-h-48 overflow-y-auto">
                {searchResults.map(user => (
                  <button 
                    key={user.user_id} 
                    type="button" 
                    onClick={() => handleSelectUser(user)}
                    className="block w-full text-left px-4 py-2 text-gray-900 hover:bg-gray-100"
                  >
                    {user.display_name || user.email}
                  </button>
                ))}
              </div>
            )}
            <div className="mt-2 flex flex-wrap gap-2">
              {taggedUsers.map(user => (
                <div key={user.user_id} className="flex items-center bg-gray-200 text-gray-800 text-sm font-medium pl-2 pr-1 py-1 rounded-full">
                  <span>{user.display_name}</span>
                  <button type="button" onClick={() => handleRemoveUser(user.user_id)} className="ml-2 text-gray-500 hover:text-gray-700">
                    &times;
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-4">
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : 'Save Session'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}

export default CreateSessionPage;