'use client';

import { Activity, UserRole, Earnings } from '@/types';
import { Trash2, Plus } from 'lucide-react';

interface ActivityCardProps {
  activity: Activity;
  userRole: UserRole;
  earnings?: Earnings;
  onIncrement?: () => void;
  onDelete?: () => void;
  isLoading?: boolean;
}

export default function ActivityCard({
  activity,
  userRole,
  earnings,
  onIncrement,
  onDelete,
  isLoading = false,
}: ActivityCardProps) {
  return (
    <div className="bg-card border border-border rounded-theme p-4 sm:p-6 shadow-sm hover:shadow-md transition-shadow">
      {/* Activity Header */}
      <div className="flex justify-between items-start mb-3 sm:mb-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-base sm:text-lg font-semibold text-card-foreground truncate">
            {activity.name}
          </h3>
          <p className="text-sm text-muted-foreground mt-1">
            ${activity.rate.toFixed(2)} per {activity.unit}
          </p>
        </div>

        {/* Delete button for parents - touch-friendly */}
        {userRole === 'parent' && onDelete && (
          <button
            onClick={onDelete}
            disabled={isLoading}
            className="min-h-touch min-w-touch flex items-center justify-center p-2 text-error hover:bg-error/10 rounded-theme transition-colors disabled:opacity-50 disabled:cursor-not-allowed ml-2 flex-shrink-0"
            aria-label="Delete activity"
            title="Delete activity"
          >
            <Trash2 size={20} />
          </button>
        )}
      </div>

      {/* Earnings display for children */}
      {userRole === 'child' && earnings && (
        <div className="mb-3 sm:mb-4 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Pending:</span>
            <span className="font-medium text-warning">
              ${earnings.pending.toFixed(2)}
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Verified:</span>
            <span className="font-medium text-success">
              ${earnings.verified.toFixed(2)}
            </span>
          </div>
        </div>
      )}

      {/* Total earnings for parents */}
      {userRole === 'parent' && earnings && (
        <div className="mb-3 sm:mb-4">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Total Earnings:</span>
            <span className="font-medium text-card-foreground">
              ${(earnings.pending + earnings.verified).toFixed(2)}
            </span>
          </div>
        </div>
      )}

      {/* Increment button for children - touch-friendly */}
      {userRole === 'child' && onIncrement && (
        <button
          onClick={onIncrement}
          disabled={isLoading}
          className="w-full min-h-touch flex items-center justify-center gap-2 px-4 py-3 bg-primary text-white rounded-theme hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm sm:text-base"
        >
          <Plus size={20} />
          <span>Log 1 {activity.unit}</span>
        </button>
      )}
    </div>
  );
}
