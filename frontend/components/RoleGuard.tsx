'use client';

import { ReactNode } from 'react';
import { useUserRole } from '@/hooks/useUserRole';

interface RoleGuardProps {
  children: ReactNode;
  allowedRoles: ('parent' | 'child')[];
  fallback?: ReactNode;
}

/**
 * Component that conditionally renders children based on user role
 * 
 * Validates: Requirements 4.1, 4.2 - Application displays role-appropriate UI
 * 
 * @param children - Content to render if user has allowed role
 * @param allowedRoles - Array of roles that can see the content
 * @param fallback - Optional content to render if user doesn't have allowed role
 */
export function RoleGuard({ children, allowedRoles, fallback = null }: RoleGuardProps) {
  const { role } = useUserRole();

  if (!role) {
    return <>{fallback}</>;
  }

  if (allowedRoles.includes(role)) {
    return <>{children}</>;
  }

  return <>{fallback}</>;
}

interface ParentOnlyProps {
  children: ReactNode;
  fallback?: ReactNode;
}

/**
 * Component that only renders for parent users
 * 
 * Validates: Requirements 4.1 - Parent users see activity creation controls
 */
export function ParentOnly({ children, fallback = null }: ParentOnlyProps) {
  return (
    <RoleGuard allowedRoles={['parent']} fallback={fallback}>
      {children}
    </RoleGuard>
  );
}

interface ChildOnlyProps {
  children: ReactNode;
  fallback?: ReactNode;
}

/**
 * Component that only renders for child users
 * 
 * Validates: Requirements 4.2 - Child users see only activity logging controls
 */
export function ChildOnly({ children, fallback = null }: ChildOnlyProps) {
  return (
    <RoleGuard allowedRoles={['child']} fallback={fallback}>
      {children}
    </RoleGuard>
  );
}
