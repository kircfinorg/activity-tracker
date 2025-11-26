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

      // For guest mode, check localStorage
      const guestUser = localStorage.getItem('guest_user');
      if (guestUser) {
        const user = JSON.parse(guestUser);

        // Check if user is already in a family
        if (user.family_id) {
          onError('You are already a member of a family');
          setIsJoining(false);
          return;
        }

        // Look up family by invite code
        const inviteCodes = JSON.parse(localStorage.getItem('invite_codes') || '{}');
        const familyId = inviteCodes[code];

        if (!familyId) {
          onError('Invalid invite code');
          setIsJoining(false);
          return;
        }

        // Get family data
        const familyData = localStorage.getItem(`family_${familyId}`);
        if (!familyData) {
          onError('Family not found');
          setIsJoining(false);
          return;
        }

        const family = JSON.parse(familyData);

        // Add user to family members
        if (!family.members.includes(user.uid)) {
          family.members.push(user.uid);
          localStorage.setItem(`family_${familyId}`, JSON.stringify(family));
        }

        // Update user with family ID
        user.family_id = familyId;
        localStorage.setItem('guest_user', JSON.stringify(user));

        onSuccess(familyId);
      } else {
        onError('User not found. Please sign in again.');
      }
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
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base uppercase tracking-wider"
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
