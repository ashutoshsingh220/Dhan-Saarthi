export type AccessibilityProfile = 
  | 'STANDARD' 
  | 'VISUAL_ASSIST' 
  | 'VOICE_ASSIST' 
  | 'LOW_LITERACY' 
  | 'ELDERLY_FRIENDLY';

export type TextSizePreference = 'SMALL' | 'STANDARD' | 'LARGE' | 'EXTRA_LARGE';

export type VoiceNavigationIntent = 
  | 'DASHBOARD'
  | 'FINANCIAL_TWIN'
  | 'GOALS'
  | 'SCHEMES'
  | 'SCAM_SHIELD'
  | 'LEARNING'
  | 'MARKET'
  | 'RECOMMENDATIONS'
  | 'AI_SAARTHI'
  | 'SETTINGS'
  | 'UNKNOWN';

export interface AccessibilityPreferences {
  accessibilityModeEnabled: boolean;
  accessibilityProfile: AccessibilityProfile;
  textSizePreference: TextSizePreference;
  highContrastEnabled: boolean;
  reduceMotionEnabled: boolean;
  simplifiedInterfaceEnabled: boolean;
  voiceNavigationEnabled: boolean;
  autoSpeakImportantResults: boolean;
  sequentialNavigationEnabled: boolean;
}

export interface VoiceNavigationResult {
  intent: VoiceNavigationIntent;
  confidence: number;
  route?: string;
  speakAnnouncement: string;
  requiresConfirmation: boolean;
  actionPayload?: any;
}
