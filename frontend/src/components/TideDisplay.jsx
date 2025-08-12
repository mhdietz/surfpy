import React from 'react';
import { format } from 'date-fns';

const TideDisplay = ({ tideData }) => {
  if (!tideData) {
    return null; // Don't render if no data
  }

  const { water_level, direction, next_event_at, next_event_height, next_event_type } = tideData;

  const formatTideTime = (dateString) => {
    const date = new Date(dateString);
    return format(date, "h:mm a");
  };

  return (
    <div className="mt-4 mb-4">
      <h2 className="text-xl font-bold mb-2">Tide</h2>
      <div className="text-gray-300 bg-gray-800 p-3 rounded-lg space-y-1">
        <p className="text-sm">
          <span className="font-semibold">Water Level:</span> {water_level?.toFixed(1)} ft and {direction}
        </p>
        <p className="text-sm">
          <span className="font-semibold">Next:</span> {next_event_type?.charAt(0).toUpperCase() + next_event_type?.slice(1)} tide of {next_event_height?.toFixed(1)} ft at {formatTideTime(next_event_at)}
        </p>
      </div>
    </div>
  );
};

export default TideDisplay;
