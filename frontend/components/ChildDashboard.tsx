'use client';

import { useState, useEffect } from 'react';
import { logsApi } from '@/lib/api';
import { auth } from '@/lib/firebase';
import { useEarnings } from '@/hooks/useEarnings';
import { useActivities } from '@/hooks/useActivities';
import ActivityGrid from './ActivityGrid';
import EarningsSummaryCard from './EarningsSummaryCard';
import { AlertCircle, Clock } from 'lucide-react';
import { collection, query, where, onSnapshot } from 'firebase/firestore';
import { db } from '@/lib/firebase';

interface ChildDashboardProps {
  userId: string;
  familyId: string;
}

/**
 * ChildDashboard component
 * 
 * Displays activity grid for logging, earnings summary cards, and pending verification status.
 * 
 * Validates: Requirements 8.1, 8.2, 6.4
 */
export default function ChildDashboard({ userId, familyId }: ChildDashboardProps) {
  const [loggingActivity, setLoggingActivity] = useState<string | null>(null);
  const [pendingLogsCount, setPendingLogsCount] = useState(0);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Fetch earnings for the child
  const { todayEarnings, weeklyEarnings, isLoading: earningsLoading } = useEarnings(
    userId,
    familyId
  );

  // Fetch activities with real-time updates (Requirement 14.3, 16.5)
  const { activities, isLoading: isLoadingActivities, error: activitiesError } = useActivities(familyId);

  // Set error message if activities fail to load
  useEffect(() => {
    if (activitiesError) {
      setErrorMessage(activitiesError);
    }
  }, [activitiesError]);

  // Set up real-time listener for pending logs count
  useEffect(() => {
    if (!userId || !familyId) return;

    const logsRef = collection(db, 'logs');
    const q = query(
      logsRef,
      where('userId', '==', userId),
      where('familyId', '==', familyId),
      where('verificationStatus', '==', 'pending')
    );

    const unsubscribe = onSnapshot(
      q,
      (snapshot) => {
        setPendingLogsCount(snapshot.size);
      },
      (error) => {
        console.error('Error listening to pending logs:', error);
      }
    );

    return () => unsubscribe();
  }, [userId, familyId]);

  const handleIncrement = async (activityId: string) => {
    try {
      setLoggingActivity(activityId);
      setErrorMessage(null);

      const user = auth.currentUser;
      if (!user) {
        throw new Error('User not authenticated');
      }

      const token = await user.getIdToken();
      await logsApi.createLog(activityId, 1, token);

      // Show success feedback
      setShowSuccessMessage(true);
      setTimeout(() => setShowSuccessMessage(false), 3000);
    } catch (err: any) {
      console.error('Error logging activity:', err);
      setErrorMessage(err.message || 'Failed to log activity');
      setTimeout(() => setErrorMessage(null), 5000);
    } finally {
      setLoggingActivity(null);
    }
  };

  if (isLoadingActivities) {
    return (
      <div className="flex items-center justify-center py-8 sm:py-12 px-4">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm sm:text-base text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  // Responsive layout for child dashboard (Requirement 13.1, 13.4, 13.5)
  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Success Message */}
      {showSuccessMessage && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-3 sm:p-4">
          <p className="text-green-800 text-center font-medium text-sm sm:text-base">
            ✓ Activity logged successfully! Pending verification.
          </p>
        </div>
      )}

      {/* Error Message */}
      {errorMessage && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 sm:p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
            <p className="text-red-800 text-sm sm:text-base">{errorMessage}</p>
          </div>
        </div>
      )}

      {/* Pending Verification Status */}
      {pendingLogsCount > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 sm:p-4">
          <div className="flex items-start gap-3">
            <Clock className="text-yellow-600 flex-shrink-0 mt-0.5" size={20} />
            <div className="min-w-0 flex-1">
              <p className="text-yellow-900 font-medium text-sm sm:text-base">
                {pendingLogsCount} {pendingLogsCount === 1 ? 'activity' : 'activities'} pending verification
              </p>
              <p className="text-yellow-700 text-xs sm:text-sm mt-1">
                Your parent will review and approve your logged activities soon.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Earnings Summary Cards */}
      <div>
        <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-3 sm:mb-4">
          Your Earnings
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
          <EarningsSummaryCard
            title="Today's Earnings"
            earnings={todayEarnings}
            isLoading={earningsLoading}
            showPending={true}
          />
          <EarningsSummaryCard
            title="This Week's Earnings"
            earnings={weeklyEarnings}
            isLoading={earningsLoading}
            showPending={true}
          />
        </div>
      </div>

      {/* Activities Grid */}
      <div>
        <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-3 sm:mb-4">
          Track Your Progress
        </h2>
        <ActivityGrid
          activities={activities}
          userRole="child"
          onIncrement={handleIncrement}
          isLoading={loggingActivity !== null}
        />
      </div>
    </div>
  );
}
