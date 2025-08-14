import React from 'react';

const Input = ({ 
  id, 
  type = 'text', 
  value, 
  onChange, 
  required = false, 
  placeholder = '',
  className = '',
  as = 'input', // New prop to specify the element type
  children // For select options
}) => {

  // Dark theme base styles for input, select, and textarea
  const baseStyle = 'w-full px-3 py-4 mt-1 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900 sm:text-sm appearance-none min-h-10';

  // Specific styles to remove default browser UI for date/time inputs
  const dateInputSpecificStyles = `
    &::-webkit-calendar-picker-indicator {
      display: none;
      -webkit-appearance: none;
    }
    &::-webkit-inner-spin-button,
    &::-webkit-outer-spin-button {
      -webkit-appearance: none;
      margin: 0;
    }
  `;

  const combinedClassName = `${baseStyle} ${className} ${dateInputSpecificStyles}`;

  const renderElement = () => {
    switch (as) {
      case 'select':
        return (
          <select
            id={id}
            value={value}
            onChange={onChange}
            required={required}
            className={combinedClassName}
          >
            {children}
          </select>
        );
      case 'textarea':
        return (
          <textarea
            id={id}
            value={value}
            onChange={onChange}
            required={required}
            placeholder={placeholder}
            className={combinedClassName}
            rows="4" // Default rows for textarea
          ></textarea>
        );
      case 'input':
      default:
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
    }
  };

  return renderElement();
};

export default Input;
