import React, { useState, useEffect } from 'react';
import { apiCall } from '../services/api';
import { useAuth } from '../context/AuthContext';
import Spinner from './UI/Spinner';

const Leaderboard = () => {
  const { user: currentUser } = useAuth();
  const [leaderboardData, setLeaderboardData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [year, setYear] = useState(new Date().getFullYear());
  const [stat, setStat] = useState('sessions'); // 'sessions', 'time', or 'rating'

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiCall(`/api/leaderboard?year=${year}&stat=${stat}`);
        setLeaderboardData(response.data);
      } catch (err) {
        console.error('Error fetching leaderboard:', err);
        setError(err.message || 'Failed to fetch leaderboard');
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
  }, [year, stat]);

  const generateYearOptions = () => {
    const currentYear = new Date().getFullYear();
    const years = [];
    for (let i = currentYear; i >= 2023; i--) {
      years.push(i);
    }
    return years;
  };

  if (loading) {
    return <Spinner />;
  }

  if (error) {
    return <div className="text-red-500 text-center p-4">Error: {error}</div>;
  }

  const getStatValue = (user) => {
    if (stat === 'time') return `${(user.total_surf_time_minutes / 60).toFixed(1)} hrs`;
    if (stat === 'rating') return user.average_fun_rating || 'N/A';
    return user.total_sessions || 0;
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-semibold">Community Leaderboard</h3>
        <div className="flex space-x-2">
          <select value={stat} onChange={(e) => setStat(e.target.value)} className="p-2 border rounded-md bg-white">
            <option value="sessions">Sessions</option>
            <option value="time">Time</option>
            <option value="rating">Rating</option>
          </select>
          <select value={year} onChange={(e) => setYear(e.target.value)} className="p-2 border rounded-md bg-white">
            {generateYearOptions().map(y => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>
      </div>
      <ul className="space-y-2">
        {leaderboardData.map((user, index) => (
          <li key={user.user_id} className={`p-3 rounded-lg flex items-center justify-between ${currentUser.id === user.user_id ? 'bg-blue-100' : 'bg-gray-50'}`}>
            <div className="flex items-center">
              <span className="text-lg font-bold text-gray-500 w-8">{index + 1}</span>
              <span className="font-semibold text-gray-800">{user.display_name}</span>
            </div>
            <span className="text-lg font-bold text-gray-700">{getStatValue(user)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Leaderboard;
