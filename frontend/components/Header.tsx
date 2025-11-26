'use client';

import { useAuth } from '@/contexts/AuthContext';
import { signOut } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { usePendingLogs } from '@/hooks/usePendingLogs';
import { Bell, Settings } from 'lucide-react';
import ThemeSelector from './ThemeSelector';
import Link from 'next/link';

export default function Header() {
  const { user, firebaseUser } = useAuth();
  const router = useRouter();
  const [isSigningOut, setIsSigningOut] = useState(false);
  const { pendingCount } = usePendingLogs();

  const handleSignOut = async () => {
    setIsSigningOut(true);
    try {
      await signOut();
      router.push('/');
    } catch (error) {
      console.error('Error signing out:', error);
    } finally {
      setIsSigningOut(false);
    }
  };

  if (!firebaseUser) {
    return null;
  }

  // Responsive header (Requirement 13.1, 13.2, 13.5)
  return (
    <header className="bg-card shadow-sm border-b border-border">
      <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8">
        <div className="flex justify-between items-center h-14 sm:h-16">
          <div className="flex items-center min-w-0 flex-1">
            <h1 className="text-base sm:text-xl font-bold text-card-foreground truncate">
              Activity Tracker
            </h1>
          </div>

          <div className="flex items-center gap-1 sm:gap-3 flex-shrink-0">
            {/* Theme Selector */}
            <div className="hidden sm:block">
              <ThemeSelector />
            </div>

            {/* Settings Link */}
            {user && (
              <Link
                href="/settings"
                className="p-2 text-card-foreground hover:bg-muted rounded-theme transition-colors min-h-touch min-w-touch flex items-center justify-center"
                title="Account Settings"
                aria-label="Account Settings"
              >
                <Settings size={20} />
              </Link>
            )}

            {/* Notification Badge for Parents - touch-friendly */}
            {user && user.role === 'parent' && pendingCount > 0 && (
              <div className="relative">
                <button
                  className="p-2 text-card-foreground hover:bg-muted rounded-theme transition-colors relative min-h-touch min-w-touch flex items-center justify-center"
                  title={`${pendingCount} pending verification${pendingCount !== 1 ? 's' : ''}`}
                  aria-label={`${pendingCount} pending verifications`}
                >
                  <Bell size={20} />
                  <span className="absolute top-1 right-1 flex h-5 w-5 items-center justify-center rounded-full bg-error text-xs font-bold text-white">
                    {pendingCount > 9 ? '9+' : pendingCount}
                  </span>
                </button>
              </div>
            )}

            {user && (
              <div className="flex items-center gap-2 sm:gap-3">
                {firebaseUser.photoURL && (
                  <img
                    src={firebaseUser.photoURL}
                    alt={user.displayName}
                    className="w-8 h-8 sm:w-10 sm:h-10 rounded-full"
                  />
                )}
                <div className="hidden md:block">
                  <p className="text-sm font-medium text-card-foreground truncate max-w-[120px]">
                    {user.displayName}
                  </p>
                  <p className="text-xs text-muted-foreground capitalize">
                    {user.role}
                  </p>
                </div>
              </div>
            )}

            {/* Touch-friendly sign out button (Requirement 13.2) */}
            <button
              onClick={handleSignOut}
              disabled={isSigningOut}
              className="px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium text-card-foreground hover:bg-muted rounded-theme transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed min-h-touch"
            >
              <span className="hidden sm:inline">{isSigningOut ? 'Signing out...' : 'Sign Out'}</span>
              <span className="sm:hidden">Out</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
