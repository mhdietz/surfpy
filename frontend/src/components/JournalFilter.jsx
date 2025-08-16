import React, { useState, useEffect, useRef } from 'react';
import { apiCall } from '../services/api';
import Button from './UI/Button'; // Using our button for consistency

const JournalFilter = ({ filters, onFilterChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [regions, setRegions] = useState([]);
  const [loadingRegions, setLoadingRegions] = useState(true);
  const [errorRegions, setErrorRegions] = useState(null);
  const wrapperRef = useRef(null);

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

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [wrapperRef]);

  return (
    <div className="relative inline-block text-left" ref={wrapperRef}>
      <Button onClick={toggleFilter} variant="secondary">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
        </svg>
        Filter
      </Button>

      {isOpen && (
        <div className="origin-top-right absolute right-0 mt-2 w-64 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-10">
          <div className="p-4 space-y-4">
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

            {/* Swell Height Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700">Swell Height (ft)</label>
              <div className="mt-1 flex space-x-2">
                <input type="number" name="min_swell_height" className="block w-1/2 pl-3 pr-3 py-2 text-base border-gray-300 rounded-md" placeholder="Min" value={filters.min_swell_height} onChange={onFilterChange} />
                <input type="number" name="max_swell_height" className="block w-1/2 pl-3 pr-3 py-2 text-base border-gray-300 rounded-md" placeholder="Max" value={filters.max_swell_height} onChange={onFilterChange} />
              </div>
            </div>

            {/* Swell Period Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700">Swell Period (s)</label>
              <div className="mt-1 flex space-x-2">
                <input type="number" name="min_swell_period" className="block w-1/2 pl-3 pr-3 py-2 text-base border-gray-300 rounded-md" placeholder="Min" value={filters.min_swell_period} onChange={onFilterChange} />
                <input type="number" name="max_swell_period" className="block w-1/2 pl-3 pr-3 py-2 text-base border-gray-300 rounded-md" placeholder="Max" value={filters.max_swell_period} onChange={onFilterChange} />
              </div>
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
          </div>
        </div>
      )}
    </div>
  );
};

export default JournalFilter;