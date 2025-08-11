import React, { useState, useEffect } from 'react';
import { apiCall } from '../services/api';
import Card from '../components/UI/Card';
import Input from '../components/UI/Input';
import Button from '../components/UI/Button';

function CreateSessionPage() {
  const [locations, setLocations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchLocations = async () => {
      try {
        const response = await apiCall('/api/surf-spots-by-region');
        setLocations(response.data || []);
      } catch (error) {
        console.error("Failed to fetch locations:", error);
        // Optionally, set an error state and display a message to the user
      } finally {
        setIsLoading(false);
      }
    };

    fetchLocations();
  }, []);

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold text-center mb-6">Create New Surf Session</h1>
      <Card>
        <form className="space-y-4">
          <div>
            <label htmlFor="date" className="block text-sm font-medium text-gray-300">Date</label>
            <Input type="date" id="date" name="date" />
          </div>

          <div>
            <label htmlFor="location" className="block text-sm font-medium text-gray-300">Location</label>
            <select id="location" name="location" className="mt-1 block w-full bg-gray-700 border-gray-600 text-white rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-2">
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
            </select>
          </div>

          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-300">Title</label>
            <Input type="text" id="title" name="title" placeholder="e.g., Fun morning session" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="start_time" className="block text-sm font-medium text-gray-300">Start Time</label>
              <Input type="time" id="start_time" name="start_time" />
            </div>
            <div>
              <label htmlFor="end_time" className="block text-sm font-medium text-gray-300">End Time</label>
              <Input type="time" id="end_time" name="end_time" />
            </div>
          </div>

          <div>
            <label htmlFor="fun_rating" className="block text-sm font-medium text-gray-300">Fun Rating (1-5)</label>
            <Input type="number" id="fun_rating" name="fun_rating" min="1" max="5" />
          </div>

          <div>
            <label htmlFor="notes" className="block text-sm font-medium text-gray-300">Notes</label>
            <textarea id="notes" name="notes" rows="4" className="mt-1 block w-full bg-gray-700 border-gray-600 text-white rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-2" placeholder="How were the waves?"></textarea>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300">Tag Surfers</label>
            <Button type="button" className="mt-1">Search & Tag Friends</Button>
            {/* Tagged users will be displayed here */}
          </div>

          <div className="pt-4">
            <Button type="submit" className="w-full">Save Session</Button>
          </div>
        </form>
      </Card>
    </div>
  );
}

export default CreateSessionPage;