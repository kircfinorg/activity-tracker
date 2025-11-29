'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Users, Crown, User } from 'lucide-react';

interface FamilyMember {
  uid: string;
  displayName: string;
  email: string;
  photoURL: string;
  role: 'parent' | 'child';
}

interface FamilyData {
  id: string;
  name: string;
  ownerId: string;
  members: string[];
  inviteCode: string;
}

export default function FamilyMembersList() {
  const { user, firebaseUser } = useAuth();
  const [familyData, setFamilyData] = useState<FamilyData | null>(null);
  const [members, setMembers] = useState<FamilyMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const familyId = user?.family_id || user?.familyId;

    if (!familyId) {
      setLoading(false);
      return;
    }

    const fetchFamilyData = async () => {
      try {
        // Get auth token (works for both guest and Firebase users)
        const { getIdToken } = await import('@/lib/auth');
        const token = await getIdToken();

        if (!token) {
          throw new Error('Not authenticated');
        }

        // Call backend API to get family details
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/families/${familyId}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch family data');
        }

        const data = await response.json();

        // Transform the response to match our interface
        setFamilyData({
          id: data.family.id,
          name: 'Family', // Backend doesn't store name
          ownerId: data.family.owner_id,
          members: data.family.members,
          inviteCode: data.family.invite_code,
        });

        // Transform members data
        const membersList: FamilyMember[] = data.members.map((member: any) => ({
          uid: member.uid,
          displayName: member.display_name || member.displayName || 'User',
          email: member.email || '',
          photoURL: member.photo_url || member.photoURL || '',
          role: member.role,
        }));

        setMembers(membersList);
      } catch (err) {
        console.error('Error fetching family data:', err);
        setError('Failed to load family members');
      } finally {
        setLoading(false);
      }
    };

    fetchFamilyData();
  }, [user?.familyId, user?.family_id, firebaseUser]);

  const familyId = user?.family_id || user?.familyId;

  if (!familyId) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">You are not part of a family yet.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">Loading family members...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-error">{error}</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-4 sm:p-6">
      <div className="flex items-center gap-3 mb-6">
        <Users size={28} className="text-primary" />
        <h2 className="text-2xl font-bold text-card-foreground">Family Members</h2>
      </div>

      {familyData && (
        <div className="bg-card border border-border rounded-theme p-4 mb-6 shadow-sm">
          <p className="text-sm text-muted-foreground mb-2">Family Name</p>
          <p className="text-lg font-semibold text-card-foreground mb-3">{familyData.name}</p>
          <p className="text-sm text-muted-foreground mb-1">Invite Code</p>
          <p className="text-lg font-mono font-bold text-primary">{familyData.inviteCode}</p>
        </div>
      )}

      <div className="space-y-3">
        {members.map((member) => {
          const isOwner = familyData?.ownerId === member.uid;
          const isCurrentUser = member.uid === user.uid;

          return (
            <div
              key={member.uid}
              className="bg-card border border-border rounded-theme p-4 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex items-center gap-4">
                {member.photoURL ? (
                  <img
                    src={member.photoURL}
                    alt={member.displayName}
                    className="w-12 h-12 rounded-full"
                  />
                ) : (
                  <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center">
                    <User size={24} className="text-muted-foreground" />
                  </div>
                )}

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="font-semibold text-card-foreground truncate">
                      {member.displayName}
                      {isCurrentUser && (
                        <span className="text-sm text-muted-foreground ml-2">(You)</span>
                      )}
                    </p>
                    {isOwner && (
                      <Crown size={16} className="text-warning flex-shrink-0" />
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground truncate">{member.email}</p>
                </div>

                <div className="flex-shrink-0">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${member.role === 'parent'
                        ? 'bg-primary/10 text-primary'
                        : 'bg-secondary/10 text-secondary'
                      }`}
                  >
                    {member.role === 'parent' ? 'Parent' : 'Child'}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {members.length === 0 && (
        <div className="text-center py-8">
          <p className="text-muted-foreground">No family members found.</p>
        </div>
      )}
    </div>
  );
}
