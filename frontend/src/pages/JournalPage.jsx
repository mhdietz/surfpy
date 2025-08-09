import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import PageTabs from '../components/PageTabs'; // Import PageTabs

const JournalPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const queryParams = new URLSearchParams(location.search);
  const currentTab = queryParams.get('tab') || 'log'; // Default to 'log'

  // Define tabs for JournalPage
  const journalTabs = [
    { label: 'My Sessions', path: '/journal?tab=log' },
    { label: 'My Stats', path: '/journal?tab=stats' },
  ];

  return (
    <div className="bg-gray-100 min-h-screen py-8"> {/* Adjusted root div */} 
      {/* PageTabs component will be fixed at the top, so main content needs padding */}
      <main className="max-w-2xl mx-auto space-y-6 px-4 pt-16"> {/* Main content wrapper with pt-16 */} 
        {/* Page Header / Sub-Navigation - now handled by PageTabs */}
        <PageTabs tabs={journalTabs} />

        {/* Conditional Content */}
        <div className="w-full bg-white p-6 rounded-lg shadow-md"> {/* Main content card */} 
          {currentTab === 'log' && (
            <div>
              <h3 className="text-xl font-semibold mb-2">My Sessions Log</h3>
              <p>This is where your surf sessions will be displayed.</p>
              {/* SessionsList component will go here eventually */}
            </div>
          )}

          {currentTab === 'stats' && (
            <div>
              <h3 className="text-xl font-semibold mb-2">My Aggregated Stats</h3>
              <p>This is where your personal surf statistics will be displayed.</p>
              {/* Stats components will go here eventually */}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default JournalPage;