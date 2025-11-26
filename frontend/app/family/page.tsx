'use client';

import FamilyMembersList from '@/components/FamilyMembersList';
import RoleGuard from '@/components/RoleGuard';

export default function FamilyPage() {
  return (
    <RoleGuard>
      <div className="min-h-screen bg-background">
        <FamilyMembersList />
      </div>
    </RoleGuard>
  );
}
