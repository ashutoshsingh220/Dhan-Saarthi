import React, { createContext, useContext, useEffect, useState } from 'react';
import {
  AccessibilityPreferences,
  AccessibilityProfile,
  TextSizePreference,
} from '../services/accessibility/accessibilityTypes';
import {
  DEFAULT_ACCESSIBILITY_PREFERENCES,
  getTextScaleFactor,
  loadAccessibilityPreferences,
  saveAccessibilityPreferences,
} from '../services/accessibility/accessibilityService';
import { announceForAccessibility } from '../services/accessibility/accessibilityAnnouncements';

interface AccessibilityContextType extends AccessibilityPreferences {
  textScale: number;
  highContrast: boolean;
  reduceMotion: boolean;
  updatePreferences: (newPrefs: Partial<AccessibilityPreferences>) => Promise<void>;
  toggleAccessibilityMode: (enabled?: boolean) => Promise<void>;
  announce: (message: string) => void;
}

const AccessibilityContext = createContext<AccessibilityContextType>({
  ...DEFAULT_ACCESSIBILITY_PREFERENCES,
  textScale: 1.0,
  highContrast: false,
  reduceMotion: false,
  updatePreferences: async () => {},
  toggleAccessibilityMode: async () => {},
  announce: () => {},
});


export const AccessibilityProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [prefs, setPrefs] = useState<AccessibilityPreferences>(DEFAULT_ACCESSIBILITY_PREFERENCES);

  useEffect(() => {
    loadAccessibilityPreferences().then(setPrefs);
  }, []);

  const updatePreferences = async (newPrefs: Partial<AccessibilityPreferences>) => {
    const updated = { ...prefs, ...newPrefs };
    setPrefs(updated);
    await saveAccessibilityPreferences(newPrefs);
  };

  const toggleAccessibilityMode = async (enabled?: boolean) => {
    const nextVal = enabled !== undefined ? enabled : !prefs.accessibilityModeEnabled;
    const nextProfile: AccessibilityProfile = nextVal && prefs.accessibilityProfile === 'STANDARD' ? 'VISUAL_ASSIST' : prefs.accessibilityProfile;
    const nextSeq = nextVal ? true : prefs.sequentialNavigationEnabled;
    const nextVoiceNav = nextVal ? true : prefs.voiceNavigationEnabled;

    const updated: AccessibilityPreferences = {
      ...prefs,
      accessibilityModeEnabled: nextVal,
      accessibilityProfile: nextProfile,
      sequentialNavigationEnabled: nextSeq,
      voiceNavigationEnabled: nextVoiceNav,
    };

    setPrefs(updated);
    await saveAccessibilityPreferences(updated);

    const msg = nextVal ? 'Accessibility Mode Enabled' : 'Accessibility Mode Disabled';
    announceForAccessibility(msg);
  };

  const textScale = getTextScaleFactor(prefs.textSizePreference);

  return (
    <AccessibilityContext.Provider
      value={{
        ...prefs,
        textScale,
        highContrast: prefs.highContrastEnabled,
        reduceMotion: prefs.reduceMotionEnabled,
        updatePreferences,
        toggleAccessibilityMode,
        announce: announceForAccessibility,
      }}
    >
      {children}
    </AccessibilityContext.Provider>
  );
};

export const useAccessibility = () => useContext(AccessibilityContext);

