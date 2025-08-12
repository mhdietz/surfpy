import React from 'react';

const SwellDisplay = ({ swellData }) => {
  if (!swellData || swellData.length === 0) {
    return null; // Don't render anything if no data
  }

  const swellComponents = swellData[0]?.swell_components;

  if (!swellComponents) {
    return null;
  }

  const formatDirection = (degrees) => {
    const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
    const index = Math.round(degrees / 22.5) % 16;
    return directions[index];
  };

  // Convert to array, sort by name (swell_1, swell_2, etc.)
  const swells = Object.entries(swellComponents)
    .map(([key, value]) => ({ ...value, name: key }))
    .sort((a, b) => a.name.localeCompare(b.name));

  return (
    <div className="mt-4 mb-4">
      <h2 className="text-xl font-bold mb-2">Swell</h2>
      <div className="text-gray-300 bg-gray-800 p-3 rounded-lg space-y-1">
        {swells.map((swell) => {
          const displayName = swell.name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()); // Format as "Swell 1"
          const swellString = `${displayName}: ${swell.height.toFixed(1)}ft @ ${swell.period.toFixed(1)}s ${formatDirection(swell.direction)} (${swell.direction.toFixed(0)}°)`;
          return <p key={swell.name} className="text-sm">{swellString}</p>;
        })}
      </div>
    </div>
  );
};

export default SwellDisplay;