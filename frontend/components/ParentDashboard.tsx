'use client';

import { useState } from 'react';
import { User } from '@/types';
import { usePendingLogs } from '@/hooks/usePendingLogs';
import { useFamilyChildren } from '@/hooks/useFamily';
import { Users, AlertCircle, CheckCircle, ChevronRight } from 'lucide-react';
import VerificationQueue from './VerificationQueue';
import ChildActivityHistory from './ChildActivityHistory';

interface ParentDashboardProps {
  familyId: string;
}

/**
 * ParentDashboard component
 * 
 * Displays all children with pending verification counts, total pending verifications,
 * provides navigation to verification interface, and displays empty state when no pending verifications.
 * 
 * Validates: Requirements 9.1, 9.4, 9.5
 */
export default function ParentDashboard({ familyId }: ParentDashboardProps) {
  const [selectedChild, setSelectedChild] = useState<User | null>(null);
  const { pendingCount } = usePendingLogs();

  // Fetch family children with real-time updates (Requirement 14.3, 16.5)
  const { children: familyMembers, isLoading, error } = useFamilyChildren(familyId);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8 sm:py-12 px-4">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm sm:text-base text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 sm:p-6 mx-4 sm:mx-0">
        <div className="flex items-start gap-3">
          <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  // If viewing a specific child's details
  if (selectedChild) {
    return (
      <div className="space-y-4 sm:space-y-6">
        <button
          onClick={() => setSelectedChild(null)}
          className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium min-h-touch px-2"
        >
          <ChevronRight className="rotate-180" size={20} />
          <span className="text-sm sm:text-base">Back to Dashboard</span>
        </button>

        <div className="bg-white rounded-lg shadow-md p-4 sm:p-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4 mb-4 sm:mb-6">
            <img
              src={selectedChild.photoURL}
              alt={selectedChild.displayName}
              className="w-12 h-12 sm:w-16 sm:h-16 rounded-full"
            />
            <div className="min-w-0 flex-1">
              <h2 className="text-xl sm:text-2xl font-bold text-gray-900 truncate">
                {selectedChild.displayName}
              </h2>
              <p className="text-sm sm:text-base text-gray-600 truncate">{selectedChild.email}</p>
            </div>
          </div>

          {/* Child's Activity History */}
          <ChildActivityHistory childId={selectedChild.uid} familyId={familyId} />
        </div>

        {/* Pending Logs for this Child */}
        <div className="bg-white rounded-lg shadow-md p-4 sm:p-6">
          <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-4">
            Pending Verifications
          </h3>
          <VerificationQueue familyId={familyId} />
        </div>
      </div>
    );
  }

  // Main dashboard view - responsive layout (Requirement 13.1, 13.4, 13.5)
  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header with total pending count */}
      <div className="bg-white rounded-lg shadow-md p-4 sm:p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex-1 min-w-0">
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-1 sm:mb-2">
              Verification Dashboard
            </h2>
            <p className="text-sm sm:text-base text-gray-600">
              Review and approve your children's activities
            </p>
          </div>
          <div className="text-center sm:text-right flex-shrink-0">
            <div className="text-3xl sm:text-4xl font-bold text-blue-600">
              {pendingCount}
            </div>
            <p className="text-xs sm:text-sm text-gray-600 mt-1">
              Total Pending
            </p>
          </div>
        </div>
      </div>

      {/* Children list with pending counts */}
      {familyMembers.length === 0 ? (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 sm:p-8 text-center">
          <Users className="w-10 h-10 sm:w-12 sm:h-12 text-blue-400 mx-auto mb-3 sm:mb-4" />
          <h3 className="text-base sm:text-lg font-medium text-blue-900 mb-2">
            No Children Yet
          </h3>
          <p className="text-sm sm:text-base text-blue-700 px-4">
            Share your family invite code with your children so they can join and start tracking activities.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md p-4 sm:p-6">
          <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-3 sm:mb-4">
            Family Members
          </h3>
          <div className="space-y-2 sm:space-y-3">
            {familyMembers.map((child) => (
              <button
                key={child.uid}
                onClick={() => setSelectedChild(child)}
                className="w-full min-h-touch flex items-center justify-between p-3 sm:p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <div className="flex items-center gap-3 sm:gap-4 min-w-0 flex-1">
                  <img
                    src={child.photoURL}
                    alt={child.displayName}
                    className="w-10 h-10 sm:w-12 sm:h-12 rounded-full flex-shrink-0"
                  />
                  <div className="text-left min-w-0 flex-1">
                    <h4 className="font-medium text-gray-900 text-sm sm:text-base truncate">
                      {child.displayName}
                    </h4>
                    <p className="text-xs sm:text-sm text-gray-600 truncate">{child.email}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
                  <span className="hidden sm:inline-block px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
                    Child
                  </span>
                  <ChevronRight className="text-gray-400" size={20} />
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Verification Queue */}
      {pendingCount > 0 ? (
        <div className="bg-white rounded-lg shadow-md p-4 sm:p-6">
          <VerificationQueue familyId={familyId} />
        </div>
      ) : (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 sm:p-8 text-center">
          <CheckCircle className="w-10 h-10 sm:w-12 sm:h-12 text-green-600 mx-auto mb-3 sm:mb-4" />
          <h3 className="text-base sm:text-lg font-medium text-green-900 mb-2">
            All Caught Up!
          </h3>
          <p className="text-sm sm:text-base text-green-700 px-4">
            No pending verifications at this time. Great job staying on top of things!
          </p>
        </div>
      )}
    </div>
  );
}
