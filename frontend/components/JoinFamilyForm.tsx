'use client';

import { useState } from 'react';

interface JoinFamilyFormProps {
  onSuccess: (familyId: string) => void;
  onError: (error: string) => void;
}

export default function JoinFamilyForm({ onSuccess, onError }: JoinFamilyFormProps) {
  const [inviteCode, setInviteCode] = useState('');
  const [isJoining, setIsJoining] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inviteCode.trim()) {
      onError('Please enter an invite code');
      return;
    }

    setIsJoining(true);

    try {
      const code = inviteCode.trim().toUpperCase();

      // Get auth token (works for both guest and Firebase users)
      const { getIdToken } = await import('@/lib/auth');
      const token = await getIdToken();
      
      if (!token) {
        throw new Error('Not authenticated');
      }

      // Call backend API to join family
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/families/join`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            invite_code: code
          }),
        }
      );

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to join family' }));
        throw new Error(error.detail || 'Failed to join family');
      }

      const data = await response.json();
      
      // Update guest user with family ID if in guest mode
      const guestUser = localStorage.getItem('guest_user');
      if (guestUser) {
        const user = JSON.parse(guestUser);
        user.family_id = data.family_id;
        localStorage.setItem('guest_user', JSON.stringify(user));
      }

      onSuccess(data.family_id);
    } catch (err: any) {
      console.error('Error joining family:', err);
      onError(err.message || 'Failed to join family');
    } finally {
      setIsJoining(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="inviteCode" className="block text-sm font-medium text-gray-700 mb-2">
          Invite Code
        </label>
        <input
          type="text"
          id="inviteCode"
          value={inviteCode}
          onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
          placeholder="Enter 6-character code"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base uppercase tracking-wider text-gray-900 placeholder:text-gray-400"
          disabled={isJoining}
          maxLength={6}
        />
      </div>

      <button
        type="submit"
        disabled={isJoining || inviteCode.length !== 6}
        className="w-full py-3 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed min-h-touch text-sm sm:text-base"
      >
        {isJoining ? 'Joining...' : 'Join Family'}
      </button>
    </form>
  );
}
