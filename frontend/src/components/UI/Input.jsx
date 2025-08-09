import React from 'react';

const Input = ({ 
  id, 
  type = 'text', 
  value, 
  onChange, 
  required = false, 
  placeholder = '',
  className = '' 
}) => {

  const baseStyle = 'w-full px-3 py-2 mt-1 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500';

  const combinedClassName = `${baseStyle} ${className}`;

  return (
    <input
      id={id}
      type={type}
      value={value}
      onChange={onChange}
      required={required}
      placeholder={placeholder}
      className={combinedClassName}
    />
  );
};

export default Input;
