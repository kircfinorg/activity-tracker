'use client';

import { useState, useEffect } from 'react';
import { connectionMonitor } from '@/lib/firebaseErrorHandler';
import { WifiOff, Wifi } from 'lucide-react';

/**
 * ConnectionStatus component
 * 
 * Displays connection status indicator and handles offline/online states
 * 
 * Validates: Requirements 14.4 - Display error messages to users
 */
export default function ConnectionStatus() {
  const [isOnline, setIsOnline] = useState(true);
  const [showOfflineMessage, setShowOfflineMessage] = useState(false);

  useEffect(() => {
    // Subscribe to connection status changes
    const unsubscribe = connectionMonitor.subscribe((online) => {
      setIsOnline(online);
      
      if (!online) {
        setShowOfflineMessage(true);
      } else {
        // Show "back online" message briefly
        setShowOfflineMessage(true);
        setTimeout(() => setShowOfflineMessage(false), 3000);
      }
    });

    // Set initial status
    setIsOnline(connectionMonitor.getStatus());

    return () => unsubscribe();
  }, []);

  // Don't show anything if online and no message to display
  if (isOnline && !showOfflineMessage) {
    return null;
  }

  return (
    <div
      className={`fixed top-4 right-4 z-50 max-w-sm rounded-lg shadow-lg p-4 transition-all ${
        isOnline
          ? 'bg-green-50 border border-green-200'
          : 'bg-yellow-50 border border-yellow-200'
      }`}
    >
      <div className="flex items-start gap-3">
        {isOnline ? (
          <Wifi className="text-green-600 flex-shrink-0 mt-0.5" size={20} />
        ) : (
          <WifiOff className="text-yellow-600 flex-shrink-0 mt-0.5" size={20} />
        )}
        <div className="min-w-0 flex-1">
          <h3
            className={`text-sm font-medium ${
              isOnline ? 'text-green-900' : 'text-yellow-900'
            }`}
          >
            {isOnline ? 'Back Online' : 'Connection Lost'}
          </h3>
          <p
            className={`text-xs mt-1 ${
              isOnline ? 'text-green-700' : 'text-yellow-700'
            }`}
          >
            {isOnline
              ? 'Your connection has been restored.'
              : 'Please check your internet connection. Changes may not be saved.'}
          </p>
        </div>
        {isOnline && (
          <button
            onClick={() => setShowOfflineMessage(false)}
            className="text-green-600 hover:text-green-700 flex-shrink-0"
            aria-label="Dismiss"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
