'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import AccountSettings from '@/components/AccountSettings';
import DeleteAccountDialog from '@/components/DeleteAccountDialog';
import { signOut } from '@/lib/auth';
// RoleGuard not needed - settings page is accessible to all authenticated users

export default function SettingsPage() {
  const router = useRouter();
  const { user, firebaseUser } = useAuth();
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  const handleDeleteAccount = async () => {
    try {
      // Check if guest user
      const guestToken = localStorage.getItem('guest_token');
      
      if (guestToken) {
        // For guest users, just clear localStorage
        localStorage.clear();
        window.location.href = '/';
        return;
      }

      if (!firebaseUser) {
        throw new Error('No authenticated user');
      }

      // Get Firebase ID token
      const token = await firebaseUser.getIdToken();

      // Call backend to delete account
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/delete-account`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete account');
      }

      // Sign out and redirect to home
      await signOut();
      router.push('/');
    } catch (error) {
      console.error('Error deleting account:', error);
      alert('Failed to delete account. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <AccountSettings onDeleteAccount={() => setIsDeleteDialogOpen(true)} />
      
      <DeleteAccountDialog
        isOpen={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        onConfirm={handleDeleteAccount}
        userName={user?.display_name || user?.displayName || 'User'}
      />
    </div>
  );
}
