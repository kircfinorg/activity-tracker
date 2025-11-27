'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import Header from '@/components/Header';
import CreateFamilyForm from '@/components/CreateFamilyForm';
import JoinFamilyForm from '@/components/JoinFamilyForm';

export default function OnboardingPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'create' | 'join'>('create');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [inviteCode, setInviteCode] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/');
    }
    // Set default tab based on role
    if (user && user.role === 'child') {
      setActiveTab('join');
    }
  }, [user, loading, router]);

  const handleCreateSuccess = (familyId: string, code: string) => {
    setError(null);
    setInviteCode(code);
    setSuccess('Family created successfully! Redirecting...');
    
    // Direct navigation to dashboard
    setTimeout(() => {
      router.push('/dashboard');
    }, 2000);
  };

  const handleJoinSuccess = (familyId: string) => {
    setError(null);
    setSuccess('Successfully joined family! Redirecting...');
    
    // Direct navigation to dashboard
    setTimeout(() => {
      router.push('/dashboard');
    }, 1500);
  };

  const handleError = (errorMessage: string) => {
    setError(errorMessage);
    setSuccess(null);
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

  if (!user) {
    return null;
  }

  // Responsive onboarding page (Requirement 13.1, 13.3)
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="max-w-2xl mx-auto px-3 sm:px-4 lg:px-8 py-4 sm:py-6 lg:py-8">
        <div className="bg-white rounded-lg shadow-md p-4 sm:p-6 lg:p-8">
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 mb-3 sm:mb-4">
            {user.role === 'parent' ? 'Create or Join a Family' : 'Join Your Family'}
          </h1>
          <p className="text-sm sm:text-base text-gray-600 mb-6">
            {user.role === 'parent'
              ? 'Create a new family group to get started, or join an existing one with an invite code.'
              : 'Enter the invite code provided by your parent to join your family group.'}
          </p>

          {error && (
            <div className="mb-4 p-3 sm:p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-xs sm:text-sm text-red-800">{error}</p>
            </div>
          )}

          {success && (
            <div className="mb-4 p-3 sm:p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-xs sm:text-sm text-green-800">{success}</p>
              {inviteCode && (
                <div className="mt-3 p-3 bg-white border border-green-300 rounded">
                  <p className="text-xs text-gray-600 mb-1">Share this invite code with your family:</p>
                  <p className="text-2xl font-bold text-gray-900 tracking-wider">{inviteCode}</p>
                </div>
              )}
            </div>
          )}

          {user.role === 'parent' && (
            <div className="mb-6">
              <div className="flex border-b border-gray-200">
                <button
                  onClick={() => setActiveTab('create')}
                  className={`flex-1 py-3 px-4 text-sm sm:text-base font-medium transition-colors ${
                    activeTab === 'create'
                      ? 'border-b-2 border-blue-600 text-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Create Family
                </button>
                <button
                  onClick={() => setActiveTab('join')}
                  className={`flex-1 py-3 px-4 text-sm sm:text-base font-medium transition-colors ${
                    activeTab === 'join'
                      ? 'border-b-2 border-blue-600 text-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Join Family
                </button>
              </div>
            </div>
          )}

          <div className="mt-6">
            {activeTab === 'create' ? (
              <CreateFamilyForm onSuccess={handleCreateSuccess} onError={handleError} />
            ) : (
              <JoinFamilyForm onSuccess={handleJoinSuccess} onError={handleError} />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
