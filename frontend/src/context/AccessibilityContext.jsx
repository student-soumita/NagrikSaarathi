import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const STORAGE_KEY = 'nagrik_accessibility';

const defaults = {
  fontScale: 1,       // 0.875 | 1 | 1.125
  isHighContrast: false,
};

const AccessibilityContext = createContext({
  ...defaults,
  setFontScale: () => {},
  setIsHighContrast: () => {},
  toggleHighContrast: () => {},
});

export function AccessibilityProvider({ children }) {
  const [fontScale, setFontScaleRaw] = useState(() => {
    try {
      const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      return stored.fontScale ?? defaults.fontScale;
    } catch (_) {
      return defaults.fontScale;
    }
  });

  const [isHighContrast, setIsHighContrastRaw] = useState(() => {
    try {
      const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      return stored.isHighContrast ?? defaults.isHighContrast;
    } catch (_) {
      return defaults.isHighContrast;
    }
  });

  // Persist whenever values change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ fontScale, isHighContrast }));
    } catch (_) {}
  }, [fontScale, isHighContrast]);

  // Apply global class to <html> so ALL pages inherit contrast immediately
  useEffect(() => {
    if (isHighContrast) {
      document.documentElement.classList.add('gov-high-contrast');
    } else {
      document.documentElement.classList.remove('gov-high-contrast');
    }
  }, [isHighContrast]);

  // Apply font scale to <html>
  useEffect(() => {
    document.documentElement.style.fontSize = `${fontScale * 16}px`;
  }, [fontScale]);

  const setFontScale = useCallback((v) => setFontScaleRaw(v), []);
  const setIsHighContrast = useCallback((v) => setIsHighContrastRaw(v), []);
  const toggleHighContrast = useCallback(() => setIsHighContrastRaw((prev) => !prev), []);

  return (
    <AccessibilityContext.Provider
      value={{ fontScale, isHighContrast, setFontScale, setIsHighContrast, toggleHighContrast }}
    >
      {children}
    </AccessibilityContext.Provider>
  );
}

export function useAccessibility() {
  return useContext(AccessibilityContext);
}
