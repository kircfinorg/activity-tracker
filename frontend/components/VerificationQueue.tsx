'use client';

import { useState, useEffect } from 'react';
import { LogEntry } from '@/types';
import { logsApi } from '@/lib/api';
import { auth } from '@/lib/firebase';
import { doc, getDoc } from 'firebase/firestore';
import { db } from '@/lib/firebase';
import { usePendingLogsForVerification } from '@/hooks/useLogs';
import VerificationItem from './VerificationItem';
import { AlertCircle, CheckCircle } from 'lucide-react';

interface VerificationQueueProps {
  familyId: string;
}

interface LogWithDetails extends LogEntry {
  activityName: string;
  childName: string;
}

export default function VerificationQueue({ familyId }: VerificationQueueProps) {
  const [logsWithDetails, setLogsWithDetails] = useState<LogWithDetails[]>([]);
  const [verifyingLogId, setVerifyingLogId] = useState<string | null>(null);
  const [detailsError, setDetailsError] = useState<string | null>(null);

  // Fetch pending logs with real-time updates (Requirement 14.3, 16.5)
  const { logs, isLoading, error } = usePendingLogsForVerification(familyId);

  // Fetch activity and user details for each log
  useEffect(() => {
    const fetchDetails = async () => {
      if (logs.length === 0) {
        setLogsWithDetails([]);
        return;
      }

      try {
        setDetailsError(null);
        const logsWithDetailsData: LogWithDetails[] = await Promise.all(
          logs.map(async (log) => {
            // Get activity name
            const activityDoc = await getDoc(doc(db, 'activities', log.activityId));
            const activityName = activityDoc.exists() 
              ? activityDoc.data().name 
              : 'Unknown Activity';

            // Get child name
            const userDoc = await getDoc(doc(db, 'users', log.userId));
            const childName = userDoc.exists() 
              ? userDoc.data().displayName 
              : 'Unknown User';

            return {
              ...log,
              activityName,
              childName,
            };
          })
        );

        setLogsWithDetails(logsWithDetailsData);
      } catch (err: any) {
        console.error('Error fetching log details:', err);
        setDetailsError(err.message || 'Failed to load log details');
      }
    };

    fetchDetails();
  }, [logs]);

  const handleVerify = async (logId: string, status: 'approved' | 'rejected') => {
    try {
      setVerifyingLogId(logId);
      setDetailsError(null);

      const user = auth.currentUser;
      if (!user) {
        throw new Error('User not authenticated');
      }

      const token = await user.getIdToken();
      await logsApi.verifyLog(logId, status, token);

      // The real-time listener will automatically update the list
    } catch (err: any) {
      console.error('Error verifying log:', err);
      setDetailsError(err.message || 'Failed to verify log entry');
    } finally {
      setVerifyingLogId(null);
    }
  };

  // Group logs by child
  const logsByChild = logsWithDetails.reduce((acc, log) => {
    if (!acc[log.childName]) {
      acc[log.childName] = [];
    }
    acc[log.childName].push(log);
    return acc;
  }, {} as Record<string, LogWithDetails[]>);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8 sm:py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || detailsError) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-3 sm:p-4 flex items-start gap-3">
        <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
        <div className="min-w-0 flex-1">
          <h3 className="text-sm font-medium text-red-800">Error</h3>
          <p className="text-sm text-red-700 mt-1">{error || detailsError}</p>
        </div>
      </div>
    );
  }

  if (logsWithDetails.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4 sm:p-6 flex flex-col items-center justify-center text-center">
        <CheckCircle className="text-green-600 mb-3" size={40} />
        <h3 className="text-base sm:text-lg font-medium text-green-900 mb-1">
          All Caught Up!
        </h3>
        <p className="text-xs sm:text-sm text-green-700">
          No pending verifications at this time.
        </p>
      </div>
    );
  }

  // Responsive verification interface (Requirement 13.4, 13.5)
  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-0">
        <h2 className="text-lg sm:text-xl font-semibold text-gray-900">
          Pending Verifications
        </h2>
        <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs sm:text-sm font-medium rounded-full">
          {logsWithDetails.length} pending
        </span>
      </div>

      {/* Logs grouped by child */}
      {Object.entries(logsByChild).map(([childName, childLogs]) => (
        <div key={childName} className="space-y-2 sm:space-y-3">
          <h3 className="text-sm sm:text-base font-medium text-gray-700 border-b border-gray-200 pb-2">
            {childName} ({childLogs.length})
          </h3>
          <div className="space-y-2 sm:space-y-3">
            {childLogs.map((log) => (
              <VerificationItem
                key={log.id}
                log={log}
                activityName={log.activityName}
                childName={log.childName}
                onApprove={() => handleVerify(log.id, 'approved')}
                onReject={() => handleVerify(log.id, 'rejected')}
                isLoading={verifyingLogId === log.id}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
