import React, { useState, useEffect } from 'react';
import { apiCall } from '../services/api';

const JournalFilter = ({ filters, onFilterChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [regions, setRegions] = useState([]);
  const [loadingRegions, setLoadingRegions] = useState(true);
  const [errorRegions, setErrorRegions] = useState(null);

  const toggleFilter = () => {
    setIsOpen(!isOpen);
  };

  // Fetch regions for the dropdown
  useEffect(() => {
    const fetchRegions = async () => {
      try {
        setLoadingRegions(true);
        const response = await apiCall('/api/regions');
        setRegions(response.data);
      } catch (err) {
        console.error('Error fetching regions:', err);
        setErrorRegions('Failed to fetch regions.');
      } finally {
        setLoadingRegions(false);
      }
    };
    fetchRegions();
  }, []);

  const activeFilterCount = Object.values(filters).filter(Boolean).length;

  return (
    <div className="w-full bg-gray-50 border border-gray-200 rounded-lg mb-4">
      {/* Clickable Filter Bar */}
      <div
        className="flex justify-between items-center p-3 cursor-pointer"
        onClick={toggleFilter}
      >
        <div className="flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          <span className="font-semibold text-gray-800">Filter Sessions</span>
        </div>
        <div className="flex items-center">
          {activeFilterCount > 0 && (
            <span className="text-sm bg-blue-500 text-white rounded-full h-6 w-6 flex items-center justify-center mr-2">
              {activeFilterCount}
            </span>
          )}
          <svg xmlns="http://www.w3.org/2000/svg" className={`h-5 w-5 text-gray-600 transform transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {/* Expandable Filter Options */}
      {isOpen && (
        <div className="p-4 border-t border-gray-200 bg-white">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Region Filter */}
            <div>
              <label htmlFor="region" className="block text-sm font-medium text-gray-700">Region</label>
              <select
                id="region"
                name="region"
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                value={filters.region}
                onChange={onFilterChange}
              >
                <option value="">All Regions</option>
                {loadingRegions && <option>Loading...</option>}
                {errorRegions && <option>Error</option>}
                {!loadingRegions && !errorRegions && regions.map((region) => (
                  <option key={region} value={region}>{region}</option>
                ))}
              </select>
            </div>

            {/* Swell Direction Filter */}
            <div>
              <label htmlFor="swell_direction" className="block text-sm font-medium text-gray-700">Swell Direction</label>
              <select id="swell_direction" name="swell_direction" className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 rounded-md" value={filters.swell_direction} onChange={onFilterChange}>
                <option value="">All</option>
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

            {/* Swell Height Filter */}
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700">Swell Height (ft)</label>
              <div className="mt-1 flex space-x-2">
                <input type="number" name="min_swell_height" className="block w-1/2 pl-3 pr-3 py-2 text-base border-gray-300 rounded-md" placeholder="Min" value={filters.min_swell_height} onChange={onFilterChange} />
                <input type="number" name="max_swell_height" className="block w-1/2 pl-3 pr-3 py-2 text-base border-gray-300 rounded-md" placeholder="Max" value={filters.max_swell_height} onChange={onFilterChange} />
              </div>
            </div>

            {/* Swell Period Filter */}
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-gray-700">Swell Period (s)</label>
              <div className="mt-1 flex space-x-2">
                <input type="number" name="min_swell_period" className="block w-1/2 pl-3 pr-3 py-2 text-base border-gray-300 rounded-md" placeholder="Min" value={filters.min_swell_period} onChange={onFilterChange} />
                <input type="number" name="max_swell_period" className="block w-1/2 pl-3 pr-3 py-2 text-base border-gray-300 rounded-md" placeholder="Max" value={filters.max_swell_period} onChange={onFilterChange} />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JournalFilter;
