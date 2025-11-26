'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { Theme } from '@/types';
import { themes, defaultTheme } from '@/lib/themes';
import { useAuth } from './AuthContext';
import { doc, updateDoc } from 'firebase/firestore';
import { db } from '@/lib/firebase';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => Promise<void>;
  themeConfig: typeof themes[Theme];
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const [theme, setThemeState] = useState<Theme>(defaultTheme);

  // Load theme from user profile or localStorage
  useEffect(() => {
    if (user?.theme) {
      setThemeState(user.theme);
    } else {
      // Fallback to localStorage for non-authenticated users
      const savedTheme = localStorage.getItem('theme') as Theme;
      if (savedTheme && themes[savedTheme]) {
        setThemeState(savedTheme);
      }
    }
  }, [user]);

  // Apply theme to document root
  useEffect(() => {
    const root = document.documentElement;
    const themeConfig = themes[theme];

    // Apply CSS custom properties
    root.style.setProperty('--background', themeConfig.colors.background);
    root.style.setProperty('--foreground', themeConfig.colors.foreground);
    root.style.setProperty('--card', themeConfig.colors.card);
    root.style.setProperty('--card-foreground', themeConfig.colors.cardForeground);
    root.style.setProperty('--primary', themeConfig.colors.primary);
    root.style.setProperty('--primary-foreground', themeConfig.colors.primaryForeground);
    root.style.setProperty('--secondary', themeConfig.colors.secondary);
    root.style.setProperty('--secondary-foreground', themeConfig.colors.secondaryForeground);
    root.style.setProperty('--accent', themeConfig.colors.accent);
    root.style.setProperty('--accent-foreground', themeConfig.colors.accentForeground);
    root.style.setProperty('--muted', themeConfig.colors.muted);
    root.style.setProperty('--muted-foreground', themeConfig.colors.mutedForeground);
    root.style.setProperty('--border', themeConfig.colors.border);
    root.style.setProperty('--input', themeConfig.colors.input);
    root.style.setProperty('--ring', themeConfig.colors.ring);
    root.style.setProperty('--success', themeConfig.colors.success);
    root.style.setProperty('--warning', themeConfig.colors.warning);
    root.style.setProperty('--error', themeConfig.colors.error);
    root.style.setProperty('--font-body', themeConfig.fonts.body);
    root.style.setProperty('--font-heading', themeConfig.fonts.heading);
    root.style.setProperty('--border-radius', themeConfig.borderRadius);

    // Set data attribute for theme-specific styling
    root.setAttribute('data-theme', theme);
  }, [theme]);

  const setTheme = async (newTheme: Theme) => {
    setThemeState(newTheme);

    // Save to localStorage
    localStorage.setItem('theme', newTheme);

    // Save to Firebase if user is authenticated
    if (user?.uid) {
      try {
        const userRef = doc(db, 'users', user.uid);
        await updateDoc(userRef, { theme: newTheme });
      } catch (error) {
        console.error('Error saving theme to Firebase:', error);
        // Don't throw - theme is still applied locally
      }
    }
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme, themeConfig: themes[theme] }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
