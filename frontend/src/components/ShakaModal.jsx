import React from 'react';
import { Link } from 'react-router-dom';

const ShakaModal = ({ users = [], onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-40 flex justify-center items-center">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-sm m-4">
        <div className="p-4 border-b flex justify-between items-center">
          <h2 className="text-lg font-semibold">Shakas</h2>
          <button onClick={onClose} className="text-2xl font-bold">&times;</button>
        </div>
        <div className="p-4 max-h-64 overflow-y-auto">
          {users.length > 0 ? (
            <ul>
              {users.map(user => (
                <li key={user.user_id} className="border-b last:border-b-0">
                  <Link
                    to={`/journal/${user.user_id}`}
                    onClick={onClose} // Close modal on selection
                    className="block p-2 hover:bg-gray-100"
                  >
                    {user.display_name || user.email}
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
             <p className="text-gray-500">No shakas yet.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ShakaModal;