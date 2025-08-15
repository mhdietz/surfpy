import React from 'react';
import { format } from 'date-fns';

const TideDisplay = ({ tideData }) => {
  if (!tideData) {
    return null; // Don't render if no data
  }

  const { water_level, direction, next_event_at, next_event_height, next_event_type } = tideData;

  const formatTideTime = (dateString) => {
    if (!dateString) return null; // Handle missing/null dates
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return null; // Handle invalid dates
    return format(date, "h:mm a");
  };

  return (
    <div className="mt-4 mb-4">
      <h2 className="text-xl font-bold mb-2">Tide</h2>
      <div className="text-gray-300 bg-gray-800 p-3 rounded-lg space-y-1">
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