import { AccessibilityInfo, Platform } from 'react-native';

export function announceForAccessibility(message: string): void {
  if (!message || !message.trim()) return;
  try {
    if (Platform.OS === 'ios' || Platform.OS === 'android') {
      AccessibilityInfo.announceForAccessibility(message.trim());
    } else {
      // Web fallback aria announcement
      const el = document.getElementById('ds-a11y-announcer');
      if (el) {
        el.textContent = message.trim();
      }
    }
  } catch (err) {
    console.warn('Accessibility announcement failed:', err);
  }
}
