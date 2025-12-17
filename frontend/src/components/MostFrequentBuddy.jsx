import React from 'react';
import { Link } from 'react-router-dom';
import Card from './UI/Card';
import { UserGroupIcon } from '@heroicons/react/24/outline';

function MostFrequentBuddy({ buddy }) {
  // buddy can be null if there's no frequent buddy for the year
  if (!buddy) {
    return null;
  }

  return (
    <Card className="mt-8 text-center">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Most Frequent Surf Buddy</h3>
      <div className="flex flex-col items-center">
        <UserGroupIcon className="h-16 w-16 text-blue-500 mb-3" />
        <p className="text-2xl font-bold text-gray-900">
          <Link to={`/journal/${buddy.buddy_user_id}`} className="hover:underline">
            {buddy.name}
          </Link>
        </p>
        <p className="text-gray-600">
          <span className="font-semibold">{buddy.count}</span> sessions together
        </p>
      </div>
    </Card>
  );
}

export default MostFrequentBuddy;
