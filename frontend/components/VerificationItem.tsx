'use client';

import { LogEntry } from '@/types';
import { Check, X, Clock } from 'lucide-react';

interface VerificationItemProps {
  log: LogEntry;
  activityName: string;
  childName: string;
  onApprove: () => void;
  onReject: () => void;
  isLoading?: boolean;
}

export default function VerificationItem({
  log,
  activityName,
  childName,
  onApprove,
  onReject,
  isLoading = false,
}: VerificationItemProps) {
  const formatTimestamp = (date: Date) => {
    const d = new Date(date);
    return d.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  // Responsive verification item (Requirement 13.4, 13.5)
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-3 sm:p-4 shadow-sm hover:shadow-md transition-shadow">
      {/* Log Entry Header */}
      <div className="flex flex-col sm:flex-row items-start justify-between mb-3 gap-2">
        <div className="flex-1 min-w-0">
          <h4 className="text-sm sm:text-base font-semibold text-gray-900 truncate">
            {activityName}
          </h4>
          <p className="text-xs sm:text-sm text-gray-600 mt-1">
            {childName} • {log.units} unit{log.units !== 1 ? 's' : ''}
          </p>
        </div>
        <div className="flex items-center gap-1 text-xs text-gray-500 flex-shrink-0">
          <Clock size={14} />
          <span className="whitespace-nowrap">{formatTimestamp(log.timestamp)}</span>
        </div>
      </div>

      {/* Action Buttons - touch-friendly (Requirement 13.2) */}
      <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
        <button
          onClick={onApprove}
          disabled={isLoading}
          className="flex-1 min-h-touch flex items-center justify-center gap-2 px-4 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm sm:text-base"
          aria-label="Approve log entry"
        >
          <Check size={18} />
          <span>Approve</span>
        </button>
        <button
          onClick={onReject}
          disabled={isLoading}
          className="flex-1 min-h-touch flex items-center justify-center gap-2 px-4 py-3 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm sm:text-base"
          aria-label="Reject log entry"
        >
          <X size={18} />
          <span>Reject</span>
        </button>
      </div>
    </div>
  );
}
