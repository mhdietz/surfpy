import React, { useState, useEffect } from 'react';

const AddToHomeScreenPrompt = () => {
  const [showPrompt, setShowPrompt] = useState(false);

  useEffect(() => {
    // Check if already dismissed
    const dismissed = localStorage.getItem('pwaPromptDismissed');
    if (dismissed) {
      return;
    }

    // Check if running in standalone mode (already installed)
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
    if (isStandalone) {
      return;
    }

    // Check for Safari on iOS/iPadOS
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);

    if (isIOS && isSafari) {
      setShowPrompt(true);
    }
  }, []);

  const handleDismiss = () => {
    localStorage.setItem('pwaPromptDismissed', 'true');
    setShowPrompt(false);
  };

  if (!showPrompt) {
    return null;
  }

  return (
    <div className="fixed bottom-0 left-0 w-full bg-blue-600 text-white p-3 text-center text-sm z-50 flex items-center justify-between">
      <span>
        For a better experience, you can add the slapp to your Home Screen from Safari. Tap the <span className="font-bold">Share icon</span>, then 'Add to Home Screen'.
      </span>
      <button onClick={handleDismiss} className="ml-4 text-white font-bold text-lg">
        &times;
      </button>
    </div>
  );
};

export default AddToHomeScreenPrompt;