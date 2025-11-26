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
  const [isGuestMode, setIsGuestMode] = useState(false);

  useEffect(() => {
    const familyId = user?.family_id || user?.familyId;
    // If user is authenticated and has a profile with family, redirect to dashboard
    if (user && familyId) {
      router.push('/dashboard');
    }
    // If user has a role but no family, redirect to onboarding
    else if (user && user.role && !familyId) {
      router.push('/onboarding');
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
      if (isGuestMode) {
        // Guest login flow - create local guest user
        const guestId = `guest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const guestUser = {
          uid: guestId,
          email: `${guestId}@guest.local`,
          display_name: `Guest ${role === 'parent' ? 'Parent' : 'Child'}`,
          photo_url: '',
          role: role,
          family_id: null,
          theme: 'deep-ocean',
          created_at: new Date().toISOString()
        };
        
        // Store guest data in localStorage
        localStorage.setItem('guest_token', `guest_token_${guestId}`);
        localStorage.setItem('guest_user', JSON.stringify(guestUser));
        
        setShowRoleModal(false);
        setError(null);
        
        // Force page reload to pick up guest user
        window.location.href = '/onboarding';
      } else {
        // Regular Firebase auth flow
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
      }
    } catch (err: any) {
      console.error('Error setting role:', err);
      setError(err.message || 'Failed to set role');
    } finally {
      setIsSettingRole(false);
    }
  };

  const handleGuestLogin = () => {
    setIsGuestMode(true);
    setShowRoleModal(true);
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center px-4">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm sm:text-base text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If user is authenticated but doesn't have a family yet, show appropriate message
  if (user && !user.familyId) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="flex flex-col items-center justify-center p-4 sm:p-8 pt-20 sm:pt-24">
          <div className="max-w-md w-full bg-white rounded-lg shadow-md p-6 sm:p-8 text-center">
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-3 sm:mb-4">
              Welcome, {user.displayName}!
            </h2>
            <p className="text-sm sm:text-base text-gray-600 mb-4 sm:mb-6">
              {user.role === 'parent' 
                ? 'Create a family group or join an existing one to get started.'
                : 'Ask your parent for an invite code to join your family group.'}
            </p>
            <button
              onClick={() => router.push('/onboarding')}
              className="w-full py-3 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors duration-200 min-h-touch text-sm sm:text-base"
            >
              Continue
            </button>
          </div>
        </main>
      </div>
    );
  }

  // Don't show login page if user already has a role (they'll be redirected)
  if (user && user.role) {
    return (
      <div className="flex min-h-screen items-center justify-center px-4">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm sm:text-base text-gray-600">Redirecting...</p>
        </div>
      </div>
    );
  }

  // Responsive landing page (Requirement 13.1, 13.2, 13.3)
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <main className="flex flex-col items-center justify-center min-h-screen p-4 sm:p-8">
        <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-6 sm:p-8 text-center">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">
            Activity Tracker
          </h1>
          <p className="text-sm sm:text-base text-gray-600 mb-6 sm:mb-8">
            Track activities, earn rewards, and stay motivated!
          </p>

          {error && (
            <div className="mb-4 sm:mb-6 p-3 sm:p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-xs sm:text-sm text-red-800">{error}</p>
            </div>
          )}

          <GoogleSignInButton
            onSuccess={handleSignInSuccess}
            onError={handleSignInError}
          />

          <div className="mt-4 sm:mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">or</span>
              </div>
            </div>

            <button
              onClick={handleGuestLogin}
              className="mt-4 w-full py-3 px-4 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors duration-200 min-h-touch text-sm sm:text-base border border-gray-300"
            >
              Continue as Guest
            </button>
          </div>

          <p className="mt-4 sm:mt-6 text-xs text-gray-500">
            By signing in, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>
      </main>

      <RoleSelectionModal
        isOpen={showRoleModal && !isSettingRole}
        onRoleSelect={handleRoleSelect}
      />

      {isSettingRole && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 sm:p-8 text-center">
            <div className="w-12 h-12 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4" />
            <p className="text-sm sm:text-base text-gray-600">Setting up your profile...</p>
          </div>
        </div>
      )}
    </div>
  );
}
