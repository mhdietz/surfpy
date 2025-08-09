import React from 'react';

const Button = ({ 
  children, 
  onClick, 
  type = 'button', 
  variant = 'primary', 
  className = '' 
}) => {
  const baseStyle = 'w-full px-4 py-2 text-lg font-semibold rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2';

  const variants = {
    primary: 'text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500',
    destructive: 'text-white bg-red-500 hover:bg-red-600 focus:ring-red-500',
    secondary: 'text-gray-700 bg-gray-200 hover:bg-gray-300 focus:ring-gray-500',
  };

  const combinedClassName = `${baseStyle} ${variants[variant]} ${className}`;

  return (
    <button 
      type={type} 
      onClick={onClick} 
      className={combinedClassName}
    >
      {children}
    </button>
  );
};

export default Button;
