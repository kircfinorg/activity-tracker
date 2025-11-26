'use client';

import { Activity, UserRole, Earnings } from '@/types';
import ActivityCard from './ActivityCard';

interface ActivityGridProps {
  activities: Activity[];
  userRole: UserRole;
  earningsMap?: Map<string, Earnings>;
  onIncrement?: (activityId: string) => void;
  onDelete?: (activityId: string) => void;
  isLoading?: boolean;
}

export default function ActivityGrid({
  activities,
  userRole,
  earningsMap,
  onIncrement,
  onDelete,
  isLoading = false,
}: ActivityGridProps) {
  // Handle empty state
  if (activities.length === 0) {
    return (
      <div className="text-center py-8 sm:py-12 px-4">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
          <svg
            className="w-8 h-8 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
        </div>
        <h3 className="text-base sm:text-lg font-medium text-gray-900 mb-2">
          No activities yet
        </h3>
        <p className="text-sm sm:text-base text-gray-600 max-w-sm mx-auto px-4">
          {userRole === 'parent'
            ? 'Create your first activity to start tracking your children\'s progress.'
            : 'Ask your parent to create activities for you to track.'}
        </p>
      </div>
    );
  }

  // Single-column on mobile, responsive grid on larger screens (Requirement 13.1, 13.4)
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
      {activities.map((activity) => (
        <ActivityCard
          key={activity.id}
          activity={activity}
          userRole={userRole}
          earnings={earningsMap?.get(activity.id)}
          onIncrement={onIncrement ? () => onIncrement(activity.id) : undefined}
          onDelete={onDelete ? () => onDelete(activity.id) : undefined}
          isLoading={isLoading}
        />
      ))}
    </div>
  );
}
