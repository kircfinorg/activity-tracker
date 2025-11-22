'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import Header from '@/components/Header';

export default function OnboardingPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push('/');
    }
  }, [user, loading, router]);

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

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-md p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            {user.role === 'parent' ? 'Create or Join a Family' : 'Join Your Family'}
          </h1>
          <p className="text-gray-600 mb-6">
            {user.role === 'parent'
              ? 'Create a new family group to get started, or join an existing one with an invite code.'
              : 'Enter the invite code provided by your parent to join your family group.'}
          </p>
          <div className="text-center py-12">
            <p className="text-gray-500">
              Family group creation and joining will be implemented in the next task.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
