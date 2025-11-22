'use client';

import { useState } from 'react';
import { UserRole } from '@/types';

interface RoleSelectionModalProps {
  isOpen: boolean;
  onRoleSelect: (role: UserRole) => void;
}

export default function RoleSelectionModal({ isOpen, onRoleSelect }: RoleSelectionModalProps) {
  const [selectedRole, setSelectedRole] = useState<UserRole | null>(null);

  if (!isOpen) return null;

  const handleSubmit = () => {
    if (selectedRole) {
      onRoleSelect(selectedRole);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome!</h2>
        <p className="text-gray-600 mb-6">
          Please select your role to get started with the Activity Tracker.
        </p>

        <div className="space-y-3 mb-6">
          <button
            onClick={() => setSelectedRole('parent')}
            className={`w-full p-4 rounded-lg border-2 transition-all duration-200 text-left min-h-[44px] ${
              selectedRole === 'parent'
                ? 'border-blue-600 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-1">
                <div
                  className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                    selectedRole === 'parent'
                      ? 'border-blue-600 bg-blue-600'
                      : 'border-gray-300'
                  }`}
                >
                  {selectedRole === 'parent' && (
                    <div className="w-2 h-2 bg-white rounded-full" />
                  )}
                </div>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Parent</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Create activities, verify completions, and manage your family group.
                </p>
              </div>
            </div>
          </button>

          <button
            onClick={() => setSelectedRole('child')}
            className={`w-full p-4 rounded-lg border-2 transition-all duration-200 text-left min-h-[44px] ${
              selectedRole === 'child'
                ? 'border-blue-600 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-1">
                <div
                  className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                    selectedRole === 'child'
                      ? 'border-blue-600 bg-blue-600'
                      : 'border-gray-300'
                  }`}
                >
                  {selectedRole === 'child' && (
                    <div className="w-2 h-2 bg-white rounded-full" />
                  )}
                </div>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Child</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Log your activities and track your earnings.
                </p>
              </div>
            </div>
          </button>
        </div>

        <button
          onClick={handleSubmit}
          disabled={!selectedRole}
          className="w-full py-3 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed min-h-[44px]"
        >
          Continue
        </button>
      </div>
    </div>
  );
}
