import React from 'react';

const WindDisplay = ({ windData }) => {
  if (!windData || windData.length === 0) {
    return null; // Don't render if no data
  }

  const wind = windData[0];

  const formatDirection = (degrees) => {
    if (degrees === null || degrees === undefined) return 'N/A';
    const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
    const index = Math.round(degrees / 22.5) % 16;
    return directions[index];
  };

  // Check for detailed data (from NDBC buoy)
  const isDetailed = wind.hasOwnProperty('air_temperature');

  return (
    <div className="mt-4 mb-4">
      <div className="text-gray-800 bg-white p-3 rounded-lg space-y-1 border border-black">
        <h2 className="text-xl font-bold mb-2">Wind & Weather</h2>
        <p className="text-sm">
          <span className="font-semibold">Wind:</span> {wind.wind_speed?.toFixed(1)} mph from {wind.wind_direction?.toFixed(0)}° ({formatDirection(wind.wind_direction)})
          {wind.wind_gust && ` gusting to ${wind.wind_gust.toFixed(1)} mph`}
        </p>
        {isDetailed && (
          <>
            <p className="text-sm"><span className="font-semibold">Air Temp:</span> {wind.air_temperature?.toFixed(1)}°F</p>
            <p className="text-sm"><span className="font-semibold">Water Temp:</span> {wind.water_temperature?.toFixed(1)}°F</p>
            <p className="text-sm"><span className="font-semibold">Pressure:</span> {wind.pressure?.toFixed(1)} hPa</p>
          </>
        )}
      </div>
    </div>
  );
};

export default WindDisplay;
