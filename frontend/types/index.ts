export type UserRole = 'parent' | 'child';

export type VerificationStatus = 'pending' | 'approved' | 'rejected';

export type Theme = 'hacker-terminal' | 'soft-serenity' | 'deep-ocean';

export interface User {
  uid: string;
  email: string;
  displayName: string;
  photoURL: string;
  role: UserRole;
  familyId: string | null;
  theme: Theme;
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
