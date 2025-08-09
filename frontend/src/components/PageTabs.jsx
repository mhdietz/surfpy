import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const PageTabs = ({ tabs }) => {
  const location = useLocation();

  const getTabClasses = (path) => {
    const baseClasses = "flex-1 px-4 py-2 text-center rounded-tl-md rounded-tr-md";
    const activeClasses = "bg-blue-600 text-white";
    const inactiveClasses = "bg-gray-200 text-gray-800 hover:bg-gray-300";
    return `${baseClasses} ${location.pathname + location.search === path ? activeClasses : inactiveClasses}`;
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
