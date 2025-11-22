'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { UserCredential } from 'firebase/auth';
import GoogleSignInButton from '@/components/GoogleSignInButton';
import RoleSelectionModal from '@/components/RoleSelectionModal';
import Header from '@/components/Header';
import { useAuth } from '@/contexts/AuthContext';
import { getIdToken } from '@/lib/auth';
import { authApi } from '@/lib/api';
import { UserRole } from '@/types';

export default function Home() {
  const { firebaseUser, user, loading, refreshUser } = useAuth();
  const router = useRouter();
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSettingRole, setIsSettingRole] = useState(false);

  useEffect(() => {
    // If user is authenticated and has a profile with family, redirect to dashboard
    if (user && user.familyId) {
      router.push('/dashboard');
    }
  }, [user, router]);

  const handleSignInSuccess = async (credential: UserCredential) => {
    try {
      setError(null);
      // Refresh user profile to check if they have a role
      await refreshUser();
      
      // Check if user needs to set role
      const token = await getIdToken();
      if (token) {
        try {
          const response = await authApi.getProfile(token);
          if (!response.user.role) {
            setShowRoleModal(true);
          }
        } catch (err: any) {
          // If profile doesn't exist, show role selection
          if (err.message.includes('not found') || err.message.includes('404')) {
            setShowRoleModal(true);
          } else {
            throw err;
          }
        }
      }
    } catch (err: any) {
      console.error('Error after sign in:', err);
      setError(err.message || 'An error occurred during sign in');
    }
  };

  const handleSignInError = (error: Error) => {
    console.error('Sign in error:', error);
    setError(error.message || 'Failed to sign in with Google');
  };

  const handleRoleSelect = async (role: UserRole) => {
    setIsSettingRole(true);
    try {
      const token = await getIdToken();
      if (!token) {
        throw new Error('Failed to get authentication token');
      }

      await authApi.setRole(role, token);
      await refreshUser();
      setShowRoleModal(false);
      setError(null);
      
      // Redirect based on role - parents need to create/join family, children need to join
      router.push('/onboarding');
    } catch (err: any) {
      console.error('Error setting role:', err);
      setError(err.message || 'Failed to set role');
    } finally {
      setIsSettingRole(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If user is authenticated but doesn't have a family yet, show appropriate message
  if (user && !user.familyId) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="flex flex-col items-center justify-center p-8 pt-24">
          <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8 text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Welcome, {user.displayName}!
            </h2>
            <p className="text-gray-600 mb-6">
              {user.role === 'parent' 
                ? 'Create a family group or join an existing one to get started.'
                : 'Ask your parent for an invite code to join your family group.'}
            </p>
            <button
              onClick={() => router.push('/onboarding')}
              className="w-full py-3 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors duration-200 min-h-[44px]"
            >
              Continue
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <main className="flex flex-col items-center justify-center min-h-screen p-8">
        <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Activity Tracker
          </h1>
          <p className="text-gray-600 mb-8">
            Track activities, earn rewards, and stay motivated!
          </p>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <GoogleSignInButton
            onSuccess={handleSignInSuccess}
            onError={handleSignInError}
          />

          <p className="mt-6 text-xs text-gray-500">
            By signing in, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>
      </main>

      <RoleSelectionModal
        isOpen={showRoleModal && !isSettingRole}
        onRoleSelect={handleRoleSelect}
      />

      {isSettingRole && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 text-center">
            <div className="w-12 h-12 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Setting up your profile...</p>
          </div>
        </div>
      )}
    </div>
  );
}
