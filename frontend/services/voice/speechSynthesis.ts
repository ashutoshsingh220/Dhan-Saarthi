import * as Speech from 'expo-speech';
import { SpeechSpeed, VoiceLanguage } from './voiceTypes';

export interface SpeakOptions {
  language?: VoiceLanguage;
  speechSpeed?: SpeechSpeed;
  onDone?: () => void;
  onError?: (err: any) => void;
}

export class VoiceSpeechSynthesis {
  private isSpeakingActive: boolean = false;
  private lastSpokenText: string = '';
  private lastOptions: SpeakOptions = {};

  speak(text: string, options: SpeakOptions = {}): void {
    const cleanText = text.replace(/[*#_`~]/g, '').trim();
    if (!cleanText) return;

    // Stop active speech before starting new speech (Interruption / Barge-in)
    this.stop();

    this.lastSpokenText = cleanText;
    this.lastOptions = options;
    this.isSpeakingActive = true;

    let rate = 1.0;
    if (options.speechSpeed === 'SLOW') rate = 0.85;
    else if (options.speechSpeed === 'FAST') rate = 1.15;

    let languageTag = 'hi-IN';
    if (options.language === 'ENGLISH') languageTag = 'en-IN';
    else if (options.language === 'HINDI') languageTag = 'hi-IN';

    try {
      Speech.speak(cleanText, {
        language: languageTag,
        rate: rate,
        onDone: () => {
          this.isSpeakingActive = false;
          if (options.onDone) options.onDone();
        },
        onError: (err) => {
          this.isSpeakingActive = false;
          if (options.onError) options.onError(err);
        },
        onStopped: () => {
          this.isSpeakingActive = false;
        },
      });
    } catch (e) {
      this.isSpeakingActive = false;
      if (options.onError) options.onError(e);
    }
  }

  stop(): void {
    try {
      Speech.stop();
    } catch (e) {}
    this.isSpeakingActive = false;
  }

  replay(): void {
    if (this.lastSpokenText) {
      this.speak(this.lastSpokenText, this.lastOptions);
    }
  }

  isSpeaking(): boolean {
    return this.isSpeakingActive;
  }
}

export const speechSynthesis = new VoiceSpeechSynthesis();
