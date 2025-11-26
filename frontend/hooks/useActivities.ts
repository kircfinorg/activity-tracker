'use client';

import { useState, useEffect } from 'react';
import { Activity } from '@/types';
import { db } from '@/lib/firebase';
import { collection, query, where, onSnapshot, orderBy } from 'firebase/firestore';
import { 
  getFirebaseErrorMessage, 
  retryOperation,
  validateDocumentData,
  safeGetField 
} from '@/lib/firebaseErrorHandler';

/**
 * Custom hook to fetch and manage activities with real-time updates
 * 
 * Validates: Requirements 14.3, 16.5 - Real-time listeners for activities
 * 
 * @param familyId - The family ID to fetch activities for
 * @returns Object with activities, loading state, and error
 */
export function useActivities(familyId: string | null) {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!familyId) {
      setActivities([]);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    // Set up real-time listener for activities
    const activitiesQuery = query(
      collection(db, 'activities'),
      where('familyId', '==', familyId),
      orderBy('createdAt', 'desc')
    );

    const unsubscribe = onSnapshot(
      activitiesQuery,
      (snapshot) => {
        try {
          const activitiesData: Activity[] = [];
          
          snapshot.forEach((doc) => {
            const data = doc.data();
            
            // Validate document data (Requirement 14.5)
            try {
              validateDocumentData(data, ['familyId', 'name', 'unit', 'rate', 'createdBy']);
              
              activitiesData.push({
                id: doc.id,
                familyId: safeGetField(data, 'familyId', ''),
                name: safeGetField(data, 'name', 'Unknown Activity'),
                unit: safeGetField(data, 'unit', 'unit'),
                rate: safeGetField(data, 'rate', 0),
                createdBy: safeGetField(data, 'createdBy', ''),
                createdAt: data.createdAt?.toDate() || new Date(),
              });
            } catch (validationError) {
              console.error(`Corrupted activity data for ${doc.id}:`, validationError);
              // Skip corrupted documents but continue processing others
            }
          });

          setActivities(activitiesData);
          setIsLoading(false);
        } catch (err) {
          console.error('Error processing activities:', err);
          setError(getFirebaseErrorMessage(err));
          setIsLoading(false);
        }
      },
      (err) => {
        console.error('Error listening to activities:', err);
        setError(getFirebaseErrorMessage(err));
        setIsLoading(false);
      }
    );

    // Cleanup listener on unmount
    return () => unsubscribe();
  }, [familyId]);

  return {
    activities,
    isLoading,
    error,
  };
}
