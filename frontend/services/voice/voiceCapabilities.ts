import { Platform } from 'react-native';
import Constants from 'expo-constants';
import { VoiceCapabilities } from './voiceTypes';

export function getVoiceCapabilities(): VoiceCapabilities {
  // Check Web Browser Native Speech Recognition
  if (Platform.OS === 'web') {
    if (typeof window !== 'undefined' && ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
      return {
        level: 'WEB_NATIVE',
        isAvailable: true,
        providerName: 'Web Speech API',
        supportNote: 'Web browser speech recognition available.',
      };
    }
    return {
      level: 'LIMITED_FALLBACK',
      isAvailable: true,
      providerName: 'Web Fallback',
      supportNote: 'Browser Speech API unavailable. Supported voice prompt samples enabled.',
    };
  }

  // Check Mobile Expo Environment
  const isExpoGo = Constants.appOwnership === 'expo' || Constants.executionEnvironment === 'storeClient';

  if (isExpoGo) {
    return {
      level: 'LIMITED_FALLBACK',
      isAvailable: true,
      providerName: 'Expo Go Voice Companion',
      supportNote: 'Live native speech recognition requires a Dhan Saarthi development build. Voice shortcuts & speech playback are fully supported.',
    };
  }

  // Standalone Native Build
  return {
    level: 'FULL_NATIVE',
    isAvailable: true,
    providerName: 'Native Speech Engine',
    supportNote: 'Full native speech recognition active.',
  };
}
