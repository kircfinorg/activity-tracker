'use client';

import { useState, useEffect } from 'react';
import { LogEntry } from '@/types';
import { db } from '@/lib/firebase';
import { collection, query, where, onSnapshot, orderBy, Timestamp } from 'firebase/firestore';

/**
 * Custom hook to fetch and manage log entries with real-time updates
 * 
 * Validates: Requirements 14.3, 16.5 - Real-time listeners for logs
 * 
 * @param familyId - The family ID to fetch logs for
 * @param userId - Optional user ID to filter logs by user
 * @param verificationStatus - Optional status to filter by ('pending', 'approved', 'rejected')
 * @returns Object with logs, loading state, and error
 */
export function useLogs(
  familyId: string | null,
  userId?: string | null,
  verificationStatus?: 'pending' | 'approved' | 'rejected'
) {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!familyId) {
      setLogs([]);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    // Build query with filters
    let logsQuery = query(
      collection(db, 'logs'),
      where('familyId', '==', familyId)
    );

    // Add user filter if provided
    if (userId) {
      logsQuery = query(logsQuery, where('userId', '==', userId));
    }

    // Add verification status filter if provided
    if (verificationStatus) {
      logsQuery = query(logsQuery, where('verificationStatus', '==', verificationStatus));
    }

    // Order by timestamp descending (most recent first)
    logsQuery = query(logsQuery, orderBy('timestamp', 'desc'));

    const unsubscribe = onSnapshot(
      logsQuery,
      (snapshot) => {
        const logsData: LogEntry[] = [];
        
        snapshot.forEach((doc) => {
          const data = doc.data();
          logsData.push({
            id: doc.id,
            activityId: data.activityId,
            userId: data.userId,
            familyId: data.familyId,
            units: data.units,
            timestamp: data.timestamp instanceof Timestamp 
              ? data.timestamp.toDate() 
              : new Date(data.timestamp),
            verificationStatus: data.verificationStatus,
            verifiedBy: data.verifiedBy || null,
            verifiedAt: data.verifiedAt 
              ? (data.verifiedAt instanceof Timestamp 
                  ? data.verifiedAt.toDate() 
                  : new Date(data.verifiedAt))
              : null,
          });
        });

        setLogs(logsData);
        setIsLoading(false);
      },
      (err) => {
        console.error('Error listening to logs:', err);
        setError(err.message || 'Failed to load logs');
        setIsLoading(false);
      }
    );

    // Cleanup listener on unmount
    return () => unsubscribe();
  }, [familyId, userId, verificationStatus]);

  return {
    logs,
    isLoading,
    error,
  };
}

/**
 * Hook to get pending logs for verification (parent view)
 * 
 * @param familyId - The family ID to fetch pending logs for
 * @returns Object with pending logs, loading state, and error
 */
export function usePendingLogsForVerification(familyId: string | null) {
  return useLogs(familyId, null, 'pending');
}

/**
 * Hook to get user's activity history
 * 
 * @param familyId - The family ID
 * @param userId - The user ID to fetch logs for
 * @returns Object with user logs, loading state, and error
 */
export function useUserLogs(familyId: string | null, userId: string | null) {
  return useLogs(familyId, userId);
}
