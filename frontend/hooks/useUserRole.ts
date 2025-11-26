'use client';

import { useAuth } from '@/contexts/AuthContext';

/**
 * Custom hook for role-based access control in UI
 * 
 * Validates: Requirements 4.1, 4.2 - Application displays role-appropriate UI
 * 
 * @returns Object with role information and helper functions
 */
export function useUserRole() {
  const { user } = useAuth();

  const role = user?.role || null;
  const isParent = role === 'parent';
  const isChild = role === 'child';
  const hasRole = role !== null;

  return {
    role,
    isParent,
    isChild,
    hasRole,
    user,
  };
}

/**
 * Hook to check if user has a specific role
 * 
 * @param requiredRole - The role to check for ('parent' or 'child')
 * @returns boolean indicating if user has the required role
 */
export function useRequireRole(requiredRole: 'parent' | 'child'): boolean {
  const { role } = useUserRole();
  return role === requiredRole;
}

/**
 * Hook to check if user is a parent
 * 
 * @returns boolean indicating if user is a parent
 */
export function useIsParent(): boolean {
  const { isParent } = useUserRole();
  return isParent;
}

/**
 * Hook to check if user is a child
 * 
 * @returns boolean indicating if user is a child
 */
export function useIsChild(): boolean {
  const { isChild } = useUserRole();
  return isChild;
}
