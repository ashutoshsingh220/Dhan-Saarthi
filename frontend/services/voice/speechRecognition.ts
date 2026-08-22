import { Platform } from 'react-native';
import { SpeechRecognitionCallbacks, SpeechRecognitionResult, VoiceCapabilities, VoiceLanguage } from './voiceTypes';

export interface SpeechRecognitionProvider {
  startListening(language: VoiceLanguage, callbacks: SpeechRecognitionCallbacks): void;
  stopListening(): void;
  cancelListening(): void;
  isAvailable(): boolean;
}

export class WebSpeechRecognitionProvider implements SpeechRecognitionProvider {
  private recognition: any = null;

  isAvailable(): boolean {
    return typeof window !== 'undefined' && ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);
  }

  startListening(language: VoiceLanguage, callbacks: SpeechRecognitionCallbacks): void {
    if (!this.isAvailable()) {
      callbacks.onError('Web Speech API is not supported on this browser.');
      return;
    }

    try {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = true;

      if (language === 'HINDI') {
        this.recognition.lang = 'hi-IN';
      } else if (language === 'ENGLISH') {
        this.recognition.lang = 'en-IN';
      } else {
        this.recognition.lang = 'hi-IN'; // Default to Hindi-India for automatic detection
      }

      this.recognition.onstart = () => {
        if (callbacks.onStart) callbacks.onStart();
      };

      this.recognition.onresult = (event: any) => {
        let transcript = '';
        let isFinal = false;

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          transcript += event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            isFinal = true;
          }
        }

        callbacks.onResult({
          transcript: transcript.trim(),
          isFinal,
          confidence: event.results[0] ? event.results[0][0].confidence : 0.9,
          entities: [],
        });

      };

      this.recognition.onerror = (event: any) => {
        callbacks.onError(event.error || 'Speech recognition error occurred.');
      };

      this.recognition.onend = () => {
        callbacks.onEnd();
      };

      this.recognition.start();
    } catch (err: any) {
      callbacks.onError(err.message || 'Failed to start Web Speech Recognition.');
    }
  }

  stopListening(): void {
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (ex) {}
    }
  }

  cancelListening(): void {
    if (this.recognition) {
      try {
        this.recognition.abort();
      } catch (ex) {}
    }
  }
}

export class FallbackSpeechRecognitionProvider implements SpeechRecognitionProvider {
  private activeTimer: any = null;

  isAvailable(): boolean {
    return true;
  }

  startListening(language: VoiceLanguage, callbacks: SpeechRecognitionCallbacks): void {
    if (callbacks.onStart) callbacks.onStart();

    const sampleQueries = language === 'HINDI'
      ? [
          'मेरे पास हर महीने 5000 रुपये बचते हैं, मुझे कहाँ निवेश करना चाहिए?',
          'PM Kisan Yojana के लिए पात्रता क्या है?',
          'इमरजेंसी फंड के लिए मुझे कितने रुपये बचाने चाहिए?',
        ]
      : [
          'How much money should I keep in my emergency buffer?',
          'I have Rs 10000 surplus per month, what is my best financial priority?',
          'Can you explain my portfolio guidance in simple terms?',
        ];

    const randomQuery = sampleQueries[Math.floor(Math.random() * sampleQueries.length)];

    this.activeTimer = setTimeout(() => {
      callbacks.onResult({
        transcript: randomQuery,
        isFinal: true,
        confidence: 0.95,
        entities: [],
      });
      callbacks.onEnd();
    }, 1200);
  }

  stopListening(): void {
    if (this.activeTimer) {
      clearTimeout(this.activeTimer);
      this.activeTimer = null;
    }
  }

  cancelListening(): void {
    this.stopListening();
  }
}

export function createSpeechRecognitionProvider(capabilities: VoiceCapabilities): SpeechRecognitionProvider {
  if (capabilities.level === 'WEB_NATIVE') {
    return new WebSpeechRecognitionProvider();
  }
  return new FallbackSpeechRecognitionProvider();
}
