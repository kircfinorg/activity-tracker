import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { db } from '@/lib/firebase';
import { collection, query, where, onSnapshot } from 'firebase/firestore';

export function usePendingLogs() {
  const { user } = useAuth();
  const [pendingCount, setPendingCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Only parents should see pending notifications
    if (!user || user.role !== 'parent' || !user.familyId) {
      setPendingCount(0);
      setLoading(false);
      return;
    }

    // Set up real-time listener for pending logs
    const logsRef = collection(db, 'logs');
    const q = query(
      logsRef,
      where('familyId', '==', user.familyId),
      where('verificationStatus', '==', 'pending')
    );

    const unsubscribe = onSnapshot(
      q,
      (snapshot) => {
        setPendingCount(snapshot.size);
        setLoading(false);
      },
      (error) => {
        console.error('Error listening to pending logs:', error);
        setLoading(false);
      }
    );

    return () => unsubscribe();
  }, [user]);

  return { pendingCount, loading };
}
