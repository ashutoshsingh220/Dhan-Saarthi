import * as SecureStore from 'expo-secure-store';
import { AccessibilityPreferences, AccessibilityProfile, TextSizePreference } from './accessibilityTypes';

const STORAGE_KEYS = {
  MODE_ENABLED: 'ds_acc_mode_enabled',
  PROFILE: 'ds_acc_profile',
  TEXT_SIZE: 'ds_acc_text_size',
  HIGH_CONTRAST: 'ds_acc_high_contrast',
  REDUCE_MOTION: 'ds_acc_reduce_motion',
  SIMPLIFIED: 'ds_acc_simplified',
  VOICE_NAV: 'ds_acc_voice_nav',
  AUTO_SPEAK: 'ds_acc_auto_speak',
  SEQ_NAV: 'ds_acc_seq_nav',
};

export const DEFAULT_ACCESSIBILITY_PREFERENCES: AccessibilityPreferences = {
  accessibilityModeEnabled: false,
  accessibilityProfile: 'STANDARD',
  textSizePreference: 'STANDARD',
  highContrastEnabled: false,
  reduceMotionEnabled: false,
  simplifiedInterfaceEnabled: false,
  voiceNavigationEnabled: false,
  autoSpeakImportantResults: false,
  sequentialNavigationEnabled: false,
};

export async function loadAccessibilityPreferences(): Promise<AccessibilityPreferences> {
  try {
    const mode = await SecureStore.getItemAsync(STORAGE_KEYS.MODE_ENABLED);
    const profile = await SecureStore.getItemAsync(STORAGE_KEYS.PROFILE);
    const textSize = await SecureStore.getItemAsync(STORAGE_KEYS.TEXT_SIZE);
    const contrast = await SecureStore.getItemAsync(STORAGE_KEYS.HIGH_CONTRAST);
    const motion = await SecureStore.getItemAsync(STORAGE_KEYS.REDUCE_MOTION);
    const simplified = await SecureStore.getItemAsync(STORAGE_KEYS.SIMPLIFIED);
    const voiceNav = await SecureStore.getItemAsync(STORAGE_KEYS.VOICE_NAV);
    const autoSpeak = await SecureStore.getItemAsync(STORAGE_KEYS.AUTO_SPEAK);
    const seqNav = await SecureStore.getItemAsync(STORAGE_KEYS.SEQ_NAV);

    return {
      accessibilityModeEnabled: mode === 'true',
      accessibilityProfile: (profile as AccessibilityProfile) || 'STANDARD',
      textSizePreference: (textSize as TextSizePreference) || 'STANDARD',
      highContrastEnabled: contrast === 'true',
      reduceMotionEnabled: motion === 'true',
      simplifiedInterfaceEnabled: simplified === 'true',
      voiceNavigationEnabled: voiceNav === 'true',
      autoSpeakImportantResults: autoSpeak === 'true',
      sequentialNavigationEnabled: seqNav === 'true',
    };
  } catch {
    return DEFAULT_ACCESSIBILITY_PREFERENCES;
  }
}

export async function saveAccessibilityPreferences(
  prefs: Partial<AccessibilityPreferences>
): Promise<void> {
  try {
    if (prefs.accessibilityModeEnabled !== undefined) {
      await SecureStore.setItemAsync(STORAGE_KEYS.MODE_ENABLED, String(prefs.accessibilityModeEnabled));
    }
    if (prefs.accessibilityProfile !== undefined) {
      await SecureStore.setItemAsync(STORAGE_KEYS.PROFILE, prefs.accessibilityProfile);
    }
    if (prefs.textSizePreference !== undefined) {
      await SecureStore.setItemAsync(STORAGE_KEYS.TEXT_SIZE, prefs.textSizePreference);
    }
    if (prefs.highContrastEnabled !== undefined) {
      await SecureStore.setItemAsync(STORAGE_KEYS.HIGH_CONTRAST, String(prefs.highContrastEnabled));
    }
    if (prefs.reduceMotionEnabled !== undefined) {
      await SecureStore.setItemAsync(STORAGE_KEYS.REDUCE_MOTION, String(prefs.reduceMotionEnabled));
    }
    if (prefs.simplifiedInterfaceEnabled !== undefined) {
      await SecureStore.setItemAsync(STORAGE_KEYS.SIMPLIFIED, String(prefs.simplifiedInterfaceEnabled));
    }
    if (prefs.voiceNavigationEnabled !== undefined) {
      await SecureStore.setItemAsync(STORAGE_KEYS.VOICE_NAV, String(prefs.voiceNavigationEnabled));
    }
    if (prefs.autoSpeakImportantResults !== undefined) {
      await SecureStore.setItemAsync(STORAGE_KEYS.AUTO_SPEAK, String(prefs.autoSpeakImportantResults));
    }
    if (prefs.sequentialNavigationEnabled !== undefined) {
      await SecureStore.setItemAsync(STORAGE_KEYS.SEQ_NAV, String(prefs.sequentialNavigationEnabled));
    }
  } catch (err) {
    console.warn('Failed to save accessibility preferences:', err);
  }
}

export function getTextScaleFactor(textSize: TextSizePreference): number {
  switch (textSize) {
    case 'SMALL':
      return 0.85;
    case 'LARGE':
      return 1.25;
    case 'EXTRA_LARGE':
      return 1.5;
    case 'STANDARD':
    default:
      return 1.0;
  }
}
