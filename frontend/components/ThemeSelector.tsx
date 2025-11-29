'use client';

import { useTheme } from '@/contexts/ThemeContext';
import { Theme } from '@/types';
import { themes } from '@/lib/themes';
import { Palette } from 'lucide-react';
import { useState } from 'react';

export default function ThemeSelector() {
  const { theme, setTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);

  const handleThemeChange = async (newTheme: Theme) => {
    await setTheme(newTheme);
    setIsOpen(false);
  };

  // Touch-friendly theme selector (Requirement 13.2)
  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 sm:px-4 py-2 min-h-touch rounded-theme bg-card text-card-foreground border border-border hover:bg-muted transition-colors"
        aria-label="Select theme"
      >
        <Palette size={20} />
        <span className="hidden sm:inline text-sm">{themes[theme].displayName}</span>
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />

          {/* Dropdown menu */}
          <div className="absolute right-0 mt-2 w-64 sm:w-56 bg-card border border-border rounded-theme shadow-lg z-50 overflow-hidden max-h-[80vh] flex flex-col">
            <div className="text-xs sm:text-sm font-semibold text-muted-foreground px-5 py-3 border-b border-border bg-card sticky top-0 z-10">
              Select Theme
            </div>
            <div className="overflow-y-auto p-2">
              {(Object.keys(themes) as Theme[]).map((themeKey) => {
                const themeConfig = themes[themeKey];
                const isSelected = theme === themeKey;

                return (
                  <button
                    key={themeKey}
                    onClick={() => handleThemeChange(themeKey)}
                    className={`w-full text-left px-3 py-3 min-h-touch rounded transition-colors ${
                      isSelected
                        ? 'bg-primary text-primary-foreground'
                        : 'hover:bg-muted text-card-foreground'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-sm">{themeConfig.displayName}</span>
                      {isSelected && (
                        <svg
                          className="w-4 h-4 flex-shrink-0"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <div
                        className="w-6 h-6 rounded border border-border flex-shrink-0"
                        style={{ backgroundColor: themeConfig.colors.background }}
                        title="Background"
                      />
                      <div
                        className="w-6 h-6 rounded border border-border flex-shrink-0"
                        style={{ backgroundColor: themeConfig.colors.primary }}
                        title="Primary"
                      />
                      <div
                        className="w-6 h-6 rounded border border-border flex-shrink-0"
                        style={{ backgroundColor: themeConfig.colors.accent }}
                        title="Accent"
                      />
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
