import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const PageTabs = ({ tabs }) => {
  const location = useLocation();

  const getTabClasses = (tabPath) => {
    const baseClasses = "flex-1 px-4 py-2 text-center rounded-tl-md rounded-tr-md";
    const activeClasses = "bg-blue-600 text-white";
    const inactiveClasses = "bg-gray-200 text-gray-800 hover:bg-gray-300";

    const currentPathname = location.pathname;
    const currentSearchParams = new URLSearchParams(location.search);
    const currentTabParam = currentSearchParams.get('tab') || 'log'; // Default to 'log'

    const tabUrl = new URL(`http://dummy.com${tabPath}`); // Use a dummy base URL to parse the path
    const tabPathname = tabUrl.pathname;
    const tabSearchParams = new URLSearchParams(tabUrl.search);
    const tabTabParam = tabSearchParams.get('tab') || 'log'; // Default to 'log'

    // Check if pathnames match AND tab parameters match
    const isActive = currentPathname === tabPathname && currentTabParam === tabTabParam;

    return `${baseClasses} ${isActive ? activeClasses : inactiveClasses}`;
  };

  return (
    <div className="fixed top-16 left-0 w-full bg-white shadow-md z-10"> {/* top-16 for 64px below main header */}
      <div className="container mx-auto flex justify-around items-center border-b border-gray-200">
        {tabs.map((tab) => (
          <Link key={tab.path} to={tab.path} className={getTabClasses(tab.path)}>
            {tab.label}
          </Link>
        ))}
      </div>
    </div>
  );
};

export default PageTabs;
