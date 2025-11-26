'use client';

import { useState } from 'react';

interface CreateFamilyFormProps {
  onSuccess: (familyId: string, inviteCode: string) => void;
  onError: (error: string) => void;
}

export default function CreateFamilyForm({ onSuccess, onError }: CreateFamilyFormProps) {
  const [familyName, setFamilyName] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  const generateInviteCode = (): string => {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let code = '';
    for (let i = 0; i < 6; i++) {
      code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return code;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!familyName.trim()) {
      onError('Please enter a family name');
      return;
    }

    setIsCreating(true);

    try {
      // Generate unique family ID and invite code
      const familyId = `family_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const inviteCode = generateInviteCode();

      // For guest mode, store family in localStorage
      const guestUser = localStorage.getItem('guest_user');
      if (guestUser) {
        const user = JSON.parse(guestUser);
        
        // Create family object
        const family = {
          id: familyId,
          name: familyName.trim(),
          inviteCode: inviteCode,
          ownerId: user.uid,
          members: [user.uid],
          createdAt: new Date().toISOString()
        };

        // Store family
        localStorage.setItem(`family_${familyId}`, JSON.stringify(family));
        
        // Store invite code mapping
        const inviteCodes = JSON.parse(localStorage.getItem('invite_codes') || '{}');
        inviteCodes[inviteCode] = familyId;
        localStorage.setItem('invite_codes', JSON.stringify(inviteCodes));

        // Update user with family ID
        user.family_id = familyId;
        localStorage.setItem('guest_user', JSON.stringify(user));

        onSuccess(familyId, inviteCode);
      } else {
        onError('User not found. Please sign in again.');
      }
    } catch (err: any) {
      console.error('Error creating family:', err);
      onError(err.message || 'Failed to create family');
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="familyName" className="block text-sm font-medium text-gray-700 mb-2">
          Family Name
        </label>
        <input
          type="text"
          id="familyName"
          value={familyName}
          onChange={(e) => setFamilyName(e.target.value)}
          placeholder="Enter your family name"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm sm:text-base"
          disabled={isCreating}
          maxLength={50}
        />
      </div>

      <button
        type="submit"
        disabled={isCreating || !familyName.trim()}
        className="w-full py-3 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed min-h-touch text-sm sm:text-base"
      >
        {isCreating ? 'Creating...' : 'Create Family'}
      </button>
    </form>
  );
}
