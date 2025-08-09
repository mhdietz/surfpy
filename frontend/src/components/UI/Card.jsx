import React from 'react';

const Card = ({ children, className = '' }) => {

  const baseStyle = 'w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md';

  const combinedClassName = `${baseStyle} ${className}`;

  return (
    <div className={combinedClassName}>
      {children}
    </div>
  );
};

export default Card;
