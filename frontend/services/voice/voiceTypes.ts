export type VoiceState =
  | 'IDLE'
  | 'LISTENING'
  | 'PROCESSING_TRANSCRIPT'
  | 'REVIEWING'
  | 'THINKING'
  | 'SPEAKING'
  | 'ERROR'
  | 'UNAVAILABLE';

export type CapabilityLevel = 'FULL_NATIVE' | 'WEB_NATIVE' | 'LIMITED_FALLBACK' | 'UNAVAILABLE';

export interface VoiceCapabilities {
  level: CapabilityLevel;
  isAvailable: boolean;
  providerName: string;
  supportNote: string;
}

export type VoiceLanguage = 'AUTOMATIC' | 'ENGLISH' | 'HINDI';

export type SpeechSpeed = 'SLOW' | 'NORMAL' | 'FAST';

export interface VoiceSettings {
  inputLanguage: VoiceLanguage;
  voiceResponse: boolean;
  autoSpeak: boolean;
  speechSpeed: SpeechSpeed;
  interruptAiSpeech: boolean;
  autoSendVoiceQuery: boolean;
}

export interface FinancialEntity {
  rawText: string;
  matchedValue: string;
  type: 'CURRENCY' | 'PERCENTAGE' | 'FINANCIAL_KEYWORD';
  confidence?: number;
  requiresConfirmation: boolean;
}

export interface SpeechRecognitionResult {
  transcript: string;
  isFinal: boolean;
  confidence?: number;
  entities: FinancialEntity[];
}

export interface SpeechRecognitionCallbacks {
  onResult: (result: SpeechRecognitionResult) => void;
  onError: (error: string) => void;
  onEnd: () => void;
  onStart?: () => void;
}
