import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { apiCall } from '../services/api';
import Spinner from './UI/Spinner';
import Input from './UI/Input';

const UserSearch = ({ onClose }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (query.length < 2) {
      setResults([]);
      return;
    }

    const debounceTimeout = setTimeout(() => {
      const fetchUsers = async () => {
        setLoading(true);
        setError(null);
        try {
          const response = await apiCall(`/api/users/search?q=${query}`);
          setResults(response.data || []);
        } catch (err) {
          setError('Failed to fetch users.');
          console.error(err);
          setResults([]);
        } finally {
          setLoading(false);
        }
      };
      fetchUsers();
    }, 300); // 300ms debounce

    return () => clearTimeout(debounceTimeout);
  }, [query]);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-40 flex justify-center items-start pt-20">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md m-4">
        <div className="p-4 border-b flex justify-between items-center">
          <h2 className="text-lg font-semibold">Search for Users</h2>
          <button onClick={onClose} className="text-2xl font-bold">&times;</button>
        </div>
        <div className="p-4">
          <Input
            type="text"
            placeholder="Search by email or name..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
          />
        </div>
        <div className="p-4 h-64 overflow-y-auto">
          {loading && <Spinner />}
          {error && <p className="text-red-500">{error}</p>}
          {!loading && !error && results.length === 0 && query.length > 1 && (
            <p className="text-gray-500">No users found.</p>
          )}
          <ul>
            {!loading && !error && results.map(user => (
              <li key={user.user_id} className="border-b">
                {onSelectUser ? (
                    <button
                      onClick={() => {
                        onSelectUser(user);
                        onClose(); // Optionally close modal on selection
                      }}
                      className="block w-full text-left p-2 hover:bg-gray-100"
                    >
                      {user.display_name || user.email}
                    </button>
                  ) : (
                    <Link
                      to={`/journal/${user.user_id}`}
                      onClick={onClose} // Close modal on navigation
                      className="block p-2 hover:bg-gray-100"
                    >
                      {user.display_name || user.email}
                    </Link>
                  )}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default UserSearch;