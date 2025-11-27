export type UserRole = 'parent' | 'child';

export type VerificationStatus = 'pending' | 'approved' | 'rejected';

export type Theme = 'hacker-terminal' | 'soft-serenity' | 'deep-ocean';

export interface User {
  uid: string;
  email: string;
  displayName?: string;
  display_name?: string;
  photoURL?: string;
  photo_url?: string;
  role: UserRole;
  familyId?: string | null;
  family_id?: string | null;
  theme: Theme;
  created_at?: string;
}

export interface Family {
  id: string;
  inviteCode: string;
  ownerId: string;
  members: string[];
  createdAt: Date;
}

export interface Activity {
  id: string;
  familyId: string;
  name: string;
  unit: string;
  rate: number;
  createdBy: string;
  createdAt: Date;
  assignedTo?: string[] | null; // List of child user IDs, null/undefined means all children
}

export interface LogEntry {
  id: string;
  activityId: string;
  userId: string;
  familyId: string;
  units: number;
  timestamp: Date;
  verificationStatus: VerificationStatus;
  verifiedBy: string | null;
  verifiedAt: Date | null;
}

export interface Earnings {
  pending: number;
  verified: number;
}
