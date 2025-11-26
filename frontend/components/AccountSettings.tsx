'use client';

import { useAuth } from '@/contexts/AuthContext';
import { User, Trash2 } from 'lucide-react';
import { useState } from 'react';

interface AccountSettingsProps {
  onDeleteAccount: () => void;
}

export default function AccountSettings({ onDeleteAccount }: AccountSettingsProps) {
  const { user, firebaseUser } = useAuth();

  if (!user || !firebaseUser) {
    return null;
  }

  return (
    <div className="max-w-2xl mx-auto p-4 sm:p-6">
      <h2 className="text-2xl font-bold text-card-foreground mb-6">Account Settings</h2>

      {/* User Profile Information */}
      <div className="bg-card border border-border rounded-theme p-6 mb-6 shadow-sm">
        <div className="flex items-center gap-4 mb-4">
          {firebaseUser.photoURL ? (
            <img
              src={firebaseUser.photoURL}
              alt={user.displayName}
              className="w-16 h-16 rounded-full"
            />
          ) : (
            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center">
              <User size={32} className="text-muted-foreground" />
            </div>
          )}
          <div>
            <h3 className="text-lg font-semibold text-card-foreground">{user.displayName}</h3>
            <p className="text-sm text-muted-foreground">{firebaseUser.email}</p>
            <p className="text-sm text-muted-foreground capitalize mt-1">
              Role: <span className="font-medium">{user.role}</span>
            </p>
          </div>
        </div>

        {user.familyId && (
          <div className="mt-4 pt-4 border-t border-border">
            <p className="text-sm text-muted-foreground">
              Family ID: <span className="font-mono text-card-foreground">{user.familyId}</span>
            </p>
          </div>
        )}
      </div>

      {/* Danger Zone */}
      <div className="bg-card border border-error/30 rounded-theme p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-error mb-2 flex items-center gap-2">
          <Trash2 size={20} />
          Danger Zone
        </h3>
        <p className="text-sm text-muted-foreground mb-4">
          Once you delete your account, there is no going back. Please be certain.
        </p>
        <button
          onClick={onDeleteAccount}
          className="px-4 py-2 bg-error text-white font-medium rounded-theme hover:bg-error/90 transition-colors duration-200 min-h-touch flex items-center gap-2"
        >
          <Trash2 size={16} />
          Delete Account
        </button>
      </div>
    </div>
  );
}
