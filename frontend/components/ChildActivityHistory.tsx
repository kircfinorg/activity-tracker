'use client';

import { useState, useEffect } from 'react';
import { LogEntry, Activity } from '@/types';
import { auth } from '@/lib/firebase';
import { collection, query, where, orderBy, onSnapshot, doc, getDoc } from 'firebase/firestore';
import { db } from '@/lib/firebase';
import { Clock, CheckCircle, XCircle, TrendingUp } from 'lucide-react';

interface ChildActivityHistoryProps {
  childId: string;
  familyId: string;
}

interface LogWithActivity extends LogEntry {
  activityName: string;
  activityRate: number;
}

/**
 * ChildActivityHistory component
 * 
 * Displays a child's activity history including all logged activities
 * with their verification status.
 * 
 * Validates: Requirements 9.2 - Display child's activity history
 */
export default function ChildActivityHistory({ childId, familyId }: ChildActivityHistoryProps) {
  const [logs, setLogs] = useState<LogWithActivity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!childId || !familyId) return;

    setIsLoading(true);
    setError(null);

    const logsRef = collection(db, 'logs');
    const q = query(
      logsRef,
      where('userId', '==', childId),
      where('familyId', '==', familyId),
      orderBy('timestamp', 'desc')
    );

    const unsubscribe = onSnapshot(
      q,
      async (snapshot) => {
        try {
          // Fetch activity details for each log
          const logsWithActivity: LogWithActivity[] = await Promise.all(
            snapshot.docs.map(async (logDoc) => {
              const logData = logDoc.data();

              // Get activity details
              const activityDoc = await getDoc(doc(db, 'activities', logData.activityId));
              const activityData = activityDoc.exists() ? activityDoc.data() : null;

              // Convert Firestore timestamp to Date
              const timestamp = logData.timestamp?.toDate() || new Date();
              const verifiedAt = logData.verifiedAt?.toDate() || null;

              return {
                id: logData.id,
                activityId: logData.activityId,
                userId: logData.userId,
                familyId: logData.familyId,
                units: logData.units,
                timestamp,
                verificationStatus: logData.verificationStatus,
                verifiedBy: logData.verifiedBy || null,
                verifiedAt,
                activityName: activityData?.name || 'Unknown Activity',
                activityRate: activityData?.rate || 0,
              };
            })
          );

          setLogs(logsWithActivity);
          setIsLoading(false);
        } catch (err: any) {
          console.error('Error processing activity history:', err);
          setError(err.message || 'Failed to load activity history');
          setIsLoading(false);
        }
      },
      (err) => {
        console.error('Error listening to activity history:', err);
        setError(err.message || 'Failed to load activity history');
        setIsLoading(false);
      }
    );

    return () => unsubscribe();
  }, [childId, familyId]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="text-green-600" size={20} />;
      case 'rejected':
        return <XCircle className="text-red-600" size={20} />;
      case 'pending':
        return <Clock className="text-yellow-600" size={20} />;
      default:
        return null;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved':
        return (
          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
            Approved
          </span>
        );
      case 'rejected':
        return (
          <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded-full">
            Rejected
          </span>
        );
      case 'pending':
        return (
          <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded-full">
            Pending
          </span>
        );
      default:
        return null;
    }
  };

  const formatDate = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
  };

  const calculateEarnings = (units: number, rate: number) => {
    return (units * rate).toFixed(2);
  };

  // Calculate summary statistics
  const totalLogs = logs.length;
  const approvedLogs = logs.filter(log => log.verificationStatus === 'approved').length;
  const pendingLogs = logs.filter(log => log.verificationStatus === 'pending').length;
  const totalEarnings = logs
    .filter(log => log.verificationStatus === 'approved')
    .reduce((sum, log) => sum + (log.units * log.activityRate), 0);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800 text-sm">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="text-2xl font-bold text-blue-900">{totalLogs}</div>
          <div className="text-sm text-blue-700">Total Activities</div>
        </div>
        <div className="bg-green-50 rounded-lg p-4">
          <div className="text-2xl font-bold text-green-900">{approvedLogs}</div>
          <div className="text-sm text-green-700">Approved</div>
        </div>
        <div className="bg-yellow-50 rounded-lg p-4">
          <div className="text-2xl font-bold text-yellow-900">{pendingLogs}</div>
          <div className="text-sm text-yellow-700">Pending</div>
        </div>
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="text-2xl font-bold text-purple-900">${totalEarnings.toFixed(2)}</div>
          <div className="text-sm text-purple-700">Total Earned</div>
        </div>
      </div>

      {/* Activity History */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Activity History
        </h3>
        
        {logs.length === 0 ? (
          <div className="bg-gray-50 rounded-lg p-8 text-center">
            <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600">No activities logged yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {logs.map((log) => (
              <div
                key={log.id}
                className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    {getStatusIcon(log.verificationStatus)}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium text-gray-900">
                          {log.activityName}
                        </h4>
                        {getStatusBadge(log.verificationStatus)}
                      </div>
                      <p className="text-sm text-gray-600">
                        {log.units} unit{log.units > 1 ? 's' : ''} × ${log.activityRate.toFixed(2)} = ${calculateEarnings(log.units, log.activityRate)}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatDate(log.timestamp)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
