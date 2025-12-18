import React from 'react';
import { MapPinIcon } from '@heroicons/react/24/solid';

function TopLocations({ locations }) {
  if (!locations || locations.length === 0) {
    return null; // Don't render anything if there are no top locations
  }

  return (
    <div className="mt-8">
      <h3 className="text-xl font-bold text-gray-800 mb-4 text-center">Top Surf Spots</h3>
      <ul className="space-y-3">
        {locations.map((location, index) => (
          <li key={index} className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
            <div className="flex items-center justify-between p-3">
              <div className="flex-grow flex items-center">
                <MapPinIcon className="h-5 w-5 text-gray-500 mr-2 flex-shrink-0" />
                <div>
                  <p className="font-semibold text-gray-900">{location.name}</p>
                  {location.region && <p className="text-sm text-gray-500">{location.region}</p>}
                </div>
              </div>
              <div className="flex-shrink-0 ml-4 text-right">
                <span className="font-bold text-lg text-gray-900">{location.session_count}</span>
                <p className="text-sm text-gray-600">Sessions</p>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default TopLocations;
