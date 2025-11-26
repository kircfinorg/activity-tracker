'use client';

import { useState, useEffect } from 'react';
import { Family, User } from '@/types';
import { db } from '@/lib/firebase';
import { doc, onSnapshot, collection, query, where, getDocs } from 'firebase/firestore';

/**
 * Custom hook to fetch and manage family data with real-time updates
 * 
 * Validates: Requirements 14.3, 16.5 - Real-time listeners for family data
 * 
 * @param familyId - The family ID to fetch
 * @returns Object with family data, loading state, and error
 */
export function useFamily(familyId: string | null) {
  const [family, setFamily] = useState<Family | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!familyId) {
      setFamily(null);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    // Set up real-time listener for family document
    const familyRef = doc(db, 'families', familyId);

    const unsubscribe = onSnapshot(
      familyRef,
      (snapshot) => {
        if (snapshot.exists()) {
          const data = snapshot.data();
          setFamily({
            id: snapshot.id,
            inviteCode: data.inviteCode,
            ownerId: data.ownerId,
            members: data.members || [],
            createdAt: data.createdAt?.toDate() || new Date(),
          });
        } else {
          setFamily(null);
          setError('Family not found');
        }
        setIsLoading(false);
      },
      (err) => {
        console.error('Error listening to family:', err);
        setError(err.message || 'Failed to load family');
        setIsLoading(false);
      }
    );

    // Cleanup listener on unmount
    return () => unsubscribe();
  }, [familyId]);

  return {
    family,
    isLoading,
    error,
  };
}

/**
 * Hook to fetch family members with real-time updates
 * 
 * @param familyId - The family ID to fetch members for
 * @returns Object with family members, loading state, and error
 */
export function useFamilyMembers(familyId: string | null) {
  const [members, setMembers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!familyId) {
      setMembers([]);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    // Set up real-time listener for family members
    const usersQuery = query(
      collection(db, 'users'),
      where('familyId', '==', familyId)
    );

    const unsubscribe = onSnapshot(
      usersQuery,
      (snapshot) => {
        const membersData: User[] = [];
        
        snapshot.forEach((doc) => {
          const data = doc.data();
          membersData.push({
            uid: doc.id,
            email: data.email,
            displayName: data.displayName,
            photoURL: data.photoURL,
            role: data.role,
            familyId: data.familyId,
            theme: data.theme || 'deep-ocean',
          });
        });

        setMembers(membersData);
        setIsLoading(false);
      },
      (err) => {
        console.error('Error listening to family members:', err);
        setError(err.message || 'Failed to load family members');
        setIsLoading(false);
      }
    );

    // Cleanup listener on unmount
    return () => unsubscribe();
  }, [familyId]);

  return {
    members,
    isLoading,
    error,
  };
}

/**
 * Hook to get children in a family (for parent view)
 * 
 * @param familyId - The family ID
 * @returns Object with children, loading state, and error
 */
export function useFamilyChildren(familyId: string | null) {
  const { members, isLoading, error } = useFamilyMembers(familyId);
  
  const children = members.filter(member => member.role === 'child');

  return {
    children,
    isLoading,
    error,
  };
}
