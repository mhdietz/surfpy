import React from 'react';

const ArrowIcon = ({ rotation }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      className="h-4 w-4 inline-block fill-current"
      style={{ transform: `rotate(${rotation}deg)` }}
    >
      <polygon points="12,0 16,24 8,24" />
    </svg>
  );
};

export default ArrowIcon;