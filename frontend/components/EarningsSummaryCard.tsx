'use client';

import { DollarSign, TrendingUp } from 'lucide-react';
import { Earnings } from '@/types';

interface EarningsSummaryCardProps {
  title: string;
  earnings: Earnings | null;
  isLoading?: boolean;
  showPending?: boolean;
}

/**
 * EarningsSummaryCard component
 * 
 * Displays earnings summary for a specific time period (today or weekly).
 * Shows pending and verified amounts for children.
 * 
 * Validates: Requirements 8.1, 8.2 - Display today's and weekly earnings
 */
export default function EarningsSummaryCard({
  title,
  earnings,
  isLoading = false,
  showPending = true,
}: EarningsSummaryCardProps) {
  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 sm:p-6 animate-pulse">
        <div className="h-5 sm:h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-3 sm:mb-4"></div>
        <div className="h-7 sm:h-8 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
        {showPending && (
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
        )}
      </div>
    );
  }

  const totalEarnings = earnings ? earnings.verified + earnings.pending : 0;
  const verifiedEarnings = earnings ? earnings.verified : 0;
  const pendingEarnings = earnings ? earnings.pending : 0;

  // Responsive earnings card (Requirement 13.1)
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 sm:p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between mb-3 sm:mb-4">
        <h3 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">
          {title}
        </h3>
        <div className="p-2 bg-green-100 dark:bg-green-900 rounded-full flex-shrink-0">
          <DollarSign className="w-4 h-4 sm:w-5 sm:h-5 text-green-600 dark:text-green-400" />
        </div>
      </div>

      <div className="space-y-2 sm:space-y-3">
        {/* Verified Earnings */}
        <div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
              ${verifiedEarnings.toFixed(2)}
            </span>
            <span className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
              verified
            </span>
          </div>
        </div>

        {/* Pending Earnings (shown for children) */}
        {showPending && pendingEarnings > 0 && (
          <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <span className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                Pending verification
              </span>
              <span className="text-base sm:text-lg font-semibold text-yellow-600 dark:text-yellow-400">
                ${pendingEarnings.toFixed(2)}
              </span>
            </div>
          </div>
        )}

        {/* Total (if there's pending) */}
        {showPending && pendingEarnings > 0 && (
          <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <span className="text-xs sm:text-sm font-medium text-gray-700 dark:text-gray-300">
                Total (if approved)
              </span>
              <span className="text-base sm:text-lg font-bold text-gray-900 dark:text-white">
                ${totalEarnings.toFixed(2)}
              </span>
            </div>
          </div>
        )}

        {/* No earnings message */}
        {totalEarnings === 0 && (
          <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
            <TrendingUp className="w-4 h-4" />
            <span className="text-xs sm:text-sm">Start logging activities to earn!</span>
          </div>
        )}
      </div>
    </div>
  );
}
