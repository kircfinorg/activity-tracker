'use client';

import { useState, useEffect, useCallback } from 'react';
import { Earnings } from '@/types';
import { earningsApi } from '@/lib/api';
import { auth } from '@/lib/firebase';
import { onSnapshot, collection, query, where } from 'firebase/firestore';
import { db } from '@/lib/firebase';

/**
 * Custom hook to fetch and manage earnings with real-time updates
 * 
 * Validates: Requirements 8.3, 8.4 - Recalculate and update earnings when logs are verified
 */
export function useEarnings(userId: string | null, familyId: string | null) {
  const [todayEarnings, setTodayEarnings] = useState<Earnings | null>(null);
  const [weeklyEarnings, setWeeklyEarnings] = useState<Earnings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Function to fetch earnings from API
  const fetchEarnings = useCallback(async () => {
    if (!userId) {
      setIsLoading(false);
      return;
    }

    try {
      setError(null);
      const user = auth.currentUser;
      
      if (!user) {
        throw new Error('User not authenticated');
      }

      const token = await user.getIdToken();

      // Fetch both today's and weekly earnings
      const [todayData, weeklyData] = await Promise.all([
        earningsApi.getTodayEarnings(userId, token),
        earningsApi.getWeeklyEarnings(userId, token),
      ]);

      setTodayEarnings(todayData as Earnings);
      setWeeklyEarnings(weeklyData as Earnings);
    } catch (err: any) {
      console.error('Error fetching earnings:', err);
      setError(err.message || 'Failed to fetch earnings');
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  // Initial fetch
  useEffect(() => {
    fetchEarnings();
  }, [fetchEarnings]);

  // Set up real-time listener for log changes
  useEffect(() => {
    if (!userId || !familyId) {
      return;
    }

    // Listen to log entries for this user to detect verification changes
    const logsQuery = query(
      collection(db, 'logs'),
      where('userId', '==', userId),
      where('familyId', '==', familyId)
    );

    const unsubscribe = onSnapshot(
      logsQuery,
      (snapshot) => {
        // When logs change (e.g., verification status updates), refetch earnings
        snapshot.docChanges().forEach((change) => {
          if (change.type === 'modified') {
            // A log was modified (likely verified), refetch earnings
            fetchEarnings();
          }
        });
      },
      (error) => {
        console.error('Error listening to log changes:', error);
      }
    );

    return () => unsubscribe();
  }, [userId, familyId, fetchEarnings]);

  return {
    todayEarnings,
    weeklyEarnings,
    isLoading,
    error,
    refetch: fetchEarnings,
  };
}
