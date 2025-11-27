'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User as FirebaseUser } from 'firebase/auth';
import { onAuthChange, getCurrentUser, getIdToken } from '@/lib/auth';
import { User } from '@/types';
import { authApi } from '@/lib/api';

interface AuthContextType {
  firebaseUser: FirebaseUser | null;
  user: User | null;
  loading: boolean;
  error: string | null;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUserProfile = async (fbUser: FirebaseUser) => {
    try {
      const token = await getIdToken();
      if (!token) {
        throw new Error('Failed to get authentication token');
      }

      const response = await authApi.getProfile(token);
      setUser(response.user);
      setError(null);
    } catch (err: any) {
      // If profile doesn't exist (404), that's okay - user needs to set role
      if (err.message.includes('not found') || err.message.includes('404')) {
        setUser(null);
        setError(null);
      } else {
        console.error('Error fetching user profile:', err);
        setError(err.message);
      }
    }
  };

  const refreshUser = async () => {
    // Check for guest user first
    const guestToken = localStorage.getItem('guest_token');
    const guestUserData = localStorage.getItem('guest_user');
    
    if (guestToken && guestUserData) {
      try {
        const guestUser = JSON.parse(guestUserData);
        setUser(guestUser);
        return;
      } catch (err) {
        console.error('Error parsing guest user data:', err);
      }
    }

    const fbUser = getCurrentUser();
    if (fbUser) {
      await fetchUserProfile(fbUser);
    }
  };

  const loadGuestUser = () => {
    const guestToken = localStorage.getItem('guest_token');
    const guestUserData = localStorage.getItem('guest_user');
    
    if (guestToken && guestUserData) {
      try {
        const guestUser = JSON.parse(guestUserData);
        setUser(guestUser);
        setLoading(false);
        return true;
      } catch (err) {
        console.error('Error parsing guest user data:', err);
        localStorage.removeItem('guest_token');
        localStorage.removeItem('guest_user');
      }
    }
    return false;
  };

  useEffect(() => {
    // Check for guest user first
    if (loadGuestUser()) {
      return;
    }

    const unsubscribe = onAuthChange(async (fbUser) => {
      setFirebaseUser(fbUser);
      
      if (fbUser) {
        await fetchUserProfile(fbUser);
      } else {
        // No Firebase user and no guest user - clear everything
        setUser(null);
        setError(null);
      }
      
      setLoading(false);
    });

    // Set loading to false after a short delay if still loading
    // This handles the case where onAuthChange doesn't fire immediately
    const timeoutId = setTimeout(() => {
      if (loading) {
        setLoading(false);
      }
    }, 1000);

    return () => {
      unsubscribe();
      clearTimeout(timeoutId);
    };
  }, []);

  // Listen for storage changes (for guest users)
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'guest_user' && e.newValue) {
        try {
          const guestUser = JSON.parse(e.newValue);
          setUser(guestUser);
        } catch (err) {
          console.error('Error parsing guest user data from storage event:', err);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  return (
    <AuthContext.Provider value={{ firebaseUser, user, loading, error, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
