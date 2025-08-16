import React from 'react';
import { formatInTimeZone } from 'date-fns-tz';

const TideDisplay = ({ tideData, location_timezone }) => {
  if (!tideData) {
    return null; // Don't render if no data
  }

  const { water_level, direction, next_event_at, next_event_height, next_event_type } = tideData;

  const formatTideTime = (dateString) => {
    if (!dateString) return null;
    try {
      // Use the timezone from the session data, with a fallback to UTC.
      const tz = location_timezone || 'UTC';
      return formatInTimeZone(dateString, tz, "h:mm a");
    } catch (error) {
      console.error("Error formatting tide time:", error);
      return new Date(dateString).toLocaleTimeString(); // Fallback
    }
  };

  return (
    <div className="mt-4 mb-4">
      <div className="text-gray-800 bg-white p-3 rounded-lg space-y-1 border border-black">
        <h2 className="text-xl font-bold mb-2">Tide</h2>
        {/* Always show water level if available */}
        {water_level !== null && water_level !== undefined && (
          <p className="text-sm">
            <span className="font-semibold">Water Level:</span> {water_level?.toFixed(1)} ft{direction ? ` and ${direction}` : ''}
          </p>
        )}
        
        {/* Only show next tide if we have complete data */}
        {next_event_at && next_event_type && next_event_height && (
          <p className="text-sm">
            <span className="font-semibold">Next:</span> {next_event_type?.charAt(0).toUpperCase() + next_event_type?.slice(1)} tide of {next_event_height?.toFixed(1)} ft at {formatTideTime(next_event_at)}
          </p>
        )}
        
        {/* Show partial info message for old sessions */}
        {water_level !== null && water_level !== undefined && (!next_event_at || !next_event_type || !next_event_height) && (
          <p className="text-xs text-gray-400 italic">Limited tide data available for this session</p>
        )}
      </div>
    </div>
  );
};

export default TideDisplay;