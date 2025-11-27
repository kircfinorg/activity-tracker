'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import Header from '@/components/Header';
import ParentDashboard from '@/components/ParentDashboard';
import ChildDashboard from '@/components/ChildDashboard';
import CreateActivityForm from '@/components/CreateActivityForm';
import { Activity } from '@/types';
import { apiClient } from '@/lib/api';

export default function DashboardPage() {
  const { user, loading, refreshUser } = useAuth();
  const router = useRouter();
  const [activities, setActivities] = useState<Activity[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Refresh user data when component mounts
  useEffect(() => {
    refreshUser();
  }, []);

  useEffect(() => {
    const familyId = user?.family_id || user?.familyId;
    if (!loading && !user) {
      router.push('/');
    } else if (!loading && user && !familyId) {
      router.push('/onboarding');
    }
  }, [user, loading, router]);

  const handleActivityCreated = (newActivity: Activity) => {
    setActivities((prev) => [...prev, newActivity]);
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

  const familyId = user?.family_id || user?.familyId;
  const displayName = user?.display_name || user?.displayName;

  if (!user || !familyId) {
    return null;
  }

  // Responsive dashboard layout (Requirement 13.1, 13.3)
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8 py-4 sm:py-6 lg:py-8">
        {/* Error Message */}
        {errorMessage && (
          <div className="mb-4 p-3 sm:p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800 text-center text-sm sm:text-base">{errorMessage}</p>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-md p-4 sm:p-6 lg:p-8">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 sm:mb-6 gap-3">
            <div className="min-w-0 flex-1">
              <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 mb-1 sm:mb-2 truncate">
                {user.role === 'parent' ? 'Parent Dashboard' : 'My Activities'}
              </h1>
              <p className="text-sm sm:text-base text-gray-600 truncate">
                Welcome, {displayName}!
              </p>
            </div>
            
            {/* View Invite Code button for parents */}
            {user.role === 'parent' && (
              <button
                onClick={() => router.push('/family')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors duration-200 text-sm sm:text-base whitespace-nowrap"
              >
                View Invite Code
              </button>
            )}
          </div>

          {/* Create Activity Form (Parent Only) */}
          {user.role === 'parent' && (
            <div className="mb-6 sm:mb-8">
              <CreateActivityForm
                familyId={familyId}
                onActivityCreated={handleActivityCreated}
              />
            </div>
          )}

          {/* Role-specific Dashboard */}
          {user.role === 'parent' ? (
            <ParentDashboard familyId={familyId} />
          ) : (
            <ChildDashboard userId={user.uid} familyId={familyId} />
          )}
        </div>
      </main>
    </div>
  );
}
