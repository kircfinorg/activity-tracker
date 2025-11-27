'use client';

import { useState } from 'react';

interface CreateFamilyFormProps {
  onSuccess: (familyId: string, inviteCode: string) => void;
  onError: (error: string) => void;
}

export default function CreateFamilyForm({ onSuccess, onError }: CreateFamilyFormProps) {
  const [isCreating, setIsCreating] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setIsCreating(true);

    try {
      // Get auth token (works for both guest and Firebase users)
      const { getIdToken } = await import('@/lib/auth');
      const token = await getIdToken();
      
      if (!token) {
        throw new Error('Not authenticated');
      }

      // Call backend API to create family
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/families`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to create family' }));
        throw new Error(error.detail || 'Failed to create family');
      }

      const data = await response.json();
      
      // Update guest user with family ID if in guest mode
      const guestUser = localStorage.getItem('guest_user');
      if (guestUser) {
        const user = JSON.parse(guestUser);
        user.family_id = data.family_id;
        localStorage.setItem('guest_user', JSON.stringify(user));
      }

      onSuccess(data.family_id, data.invite_code);
    } catch (err: any) {
      console.error('Error creating family:', err);
      onError(err.message || 'Failed to create family');
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="text-center mb-4">
        <p className="text-sm text-gray-600">
          Click the button below to create your family group and get a unique invite code.
        </p>
      </div>

      <button
        type="submit"
        disabled={isCreating}
        className="w-full py-3 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed min-h-touch text-sm sm:text-base"
      >
        {isCreating ? 'Creating...' : 'Create Family'}
      </button>
    </form>
  );
}
