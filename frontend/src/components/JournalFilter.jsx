import React, { useState } from 'react';

const JournalFilter = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleFilter = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-md mb-6">
      <button
        onClick={toggleFilter}
        className="w-full flex justify-between items-center text-lg font-semibold text-gray-800 focus:outline-none"
      >
        Filter Sessions
        <svg
          className={`w-5 h-5 transform transition-transform ${isOpen ? 'rotate-180' : 'rotate-0'}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
        </svg>
      </button>

      {isOpen && (
        <div className="mt-4 space-y-4">
          {/* Region Filter */}
          <div>
            <label htmlFor="dummyRegion" className="block text-sm font-medium text-gray-700">Region (Dummy)</label>
            <select
              id="dummyRegion"
              name="dummyRegion"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option value="">All Regions</option>
              <option value="dummy1">Dummy Region 1</option>
              <option value="dummy2">Dummy Region 2</option>
            </select>
          </div>

          {/* Swell Height Filter (Range) */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Swell Height (ft)</label>
            <div className="mt-1 flex space-x-2">
              <input
                type="number"
                id="minSwellHeight"
                name="minSwellHeight"
                className="block w-1/2 pl-3 pr-3 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                placeholder="Min"
              />
              <input
                type="number"
                id="maxSwellHeight"
                name="maxSwellHeight"
                className="block w-1/2 pl-3 pr-3 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                placeholder="Max"
              />
            </div>
          </div>

          {/* Swell Period Filter (Range) */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Swell Period (s)</label>
            <div className="mt-1 flex space-x-2">
              <input
                type="number"
                id="minSwellPeriod"
                name="minSwellPeriod"
                className="block w-1/2 pl-3 pr-3 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                placeholder="Min"
              />
              <input
                type="number"
                id="maxSwellPeriod"
                name="maxSwellPeriod"
                className="block w-1/2 pl-3 pr-3 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                placeholder="Max"
              />
            </div>
          </div>

          {/* Swell Direction Filter */}
          <div>
            <label htmlFor="swellDirection" className="block text-sm font-medium text-gray-700">Swell Direction</label>
            <select
              id="swellDirection"
              name="swellDirection"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option value="">All Directions</option>
              <option value="N">N</option>
              <option value="NE">NE</option>
              <option value="E">E</option>
              <option value="SE">SE</option>
              <option value="S">S</option>
              <option value="SW">SW</option>
              <option value="W">W</option>
              <option value="NW">NW</option>
            </select>
          </div>
        </div>
      )}
    </div>
  );
};

export default JournalFilter;

