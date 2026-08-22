import * as SecureStore from 'expo-secure-store';
import { FinancialEntity, VoiceSettings } from './voiceTypes';
import { speechSynthesis } from './speechSynthesis';

const VOICE_SETTINGS_KEY = 'dhan_saarthi_voice_settings';

export const DEFAULT_VOICE_SETTINGS: VoiceSettings = {
  inputLanguage: 'AUTOMATIC',
  voiceResponse: true,
  autoSpeak: true,
  speechSpeed: 'NORMAL',
  interruptAiSpeech: true,
  autoSendVoiceQuery: false, // DEFAULT OFF as required by Section E
};

export class VoiceService {
  private settings: VoiceSettings = { ...DEFAULT_VOICE_SETTINGS };

  async loadSettings(): Promise<VoiceSettings> {
    try {
      const stored = await SecureStore.getItemAsync(VOICE_SETTINGS_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        this.settings = { ...DEFAULT_VOICE_SETTINGS, ...parsed };
      }
    } catch (e) {
      console.warn('Failed to load voice settings from SecureStore:', e);
    }
    return this.settings;
  }

  async saveSettings(newSettings: Partial<VoiceSettings>): Promise<VoiceSettings> {
    this.settings = { ...this.settings, ...newSettings };
    try {
      await SecureStore.setItemAsync(VOICE_SETTINGS_KEY, JSON.stringify(this.settings));
    } catch (e) {
      console.warn('Failed to save voice settings to SecureStore:', e);
    }
    return this.settings;
  }

  getSettings(): VoiceSettings {
    return this.settings;
  }

  /**
   * Detects high-impact financial entities in speech transcripts.
   * Prompts confirmation if high-impact amounts or percentages are detected.
   */
  detectFinancialEntities(transcript: string): FinancialEntity[] {
    const entities: FinancialEntity[] = [];
    if (!transcript) return entities;

    // Currency pattern matching (e.g., ₹50,000, Rs 10000, 5000 rupees, 10 lakh, 5 hazar)
    const currencyRegex = /(?:₹|rs\.?|rupees|रुपये|रु\.?)\s*([\d,]+(?:\.\d+)?)|([\d,]+(?:\.\d+)?)\s*(?:rupees|रुपये|lakh|lakhs|लाख|crore|करोड़|hazar|हजार)/gi;
    let match;
    while ((match = currencyRegex.exec(transcript)) !== null) {
      const matchedVal = match[1] || match[2] || match[0];
      entities.push({
        rawText: match[0],
        matchedValue: matchedVal,
        type: 'CURRENCY',
        requiresConfirmation: true,
      });
    }

    // Percentage pattern matching (e.g. 10%, 15 percent, 8 प्रतिशत)
    const pctRegex = /([\d.]+)\s*(?:%|percent|प्रतिशत)/gi;
    while ((match = pctRegex.exec(transcript)) !== null) {
      entities.push({
        rawText: match[0],
        matchedValue: match[1],
        type: 'PERCENTAGE',
        requiresConfirmation: true,
      });
    }

    // High impact keywords
    const keywords = ['income', 'expense', 'expenses', 'monthly', 'investment', 'loan', 'emergency', 'आय', 'खर्च', 'निवेश', 'कर्ज'];
    for (const kw of keywords) {
      if (transcript.toLowerCase().includes(kw)) {
        entities.push({
          rawText: kw,
          matchedValue: kw,
          type: 'FINANCIAL_KEYWORD',
          requiresConfirmation: false,
        });
      }
    }

    return entities;
  }

  /**
   * Interruption / Barge-in: Stops AI Speech immediately if user starts speaking or taps mic.
   */
  interruptSpeech(): void {
    if (this.settings.interruptAiSpeech) {
      speechSynthesis.stop();
    }
  }
}

export const voiceService = new VoiceService();
