import React from 'react';
import { useAuth } from '../../context/AuthContext';

const AddToHomeScreenPrompt = () => {
  const { showPwaPrompt, setShowPwaPrompt } = useAuth();

  const handleDismiss = () => {
    setShowPwaPrompt(false);
  };

  if (!showPwaPrompt) {
    return null;
  }

  return (
    <div className="fixed bottom-16 left-0 w-full bg-blue-600 text-white p-3 text-center text-sm z-50 flex items-center justify-between sm:max-w-md sm:left-1/2 sm:-translate-x-1/2 sm:rounded-lg sm:bottom-4">
      <span>
        For a better experience, you can add the slapp to your Home Screen from Safari. Tap the <span className="font-bold">Share icon</span>, then 'Add to Home Screen'.
      </span>
      <button onClick={handleDismiss} className="ml-4 p-2 text-white font-bold text-lg">
        &times;
      </button>
    </div>
  );
};

export default AddToHomeScreenPrompt;
