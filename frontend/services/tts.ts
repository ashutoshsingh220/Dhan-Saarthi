import * as Speech from "expo-speech";

export const ttsService = {
  speak: async (
    text: string,
    language: "en" | "hi" = "en",
    onDone?: () => void,
    onError?: (error: any) => void
  ) => {
    try {
      // Stop any active speech before starting new speech
      await Speech.stop();

      const langCode = language === "hi" ? "hi-IN" : "en-US";
      
      Speech.speak(text, {
        language: langCode,
        pitch: 1.0,
        rate: 0.95,
        onDone: () => {
          if (onDone) onDone();
        },
        onError: (err) => {
          console.warn("TTS Error:", err);
          if (onError) onError(err);
        },
      });
    } catch (err) {
      console.warn("Speech API failed to speak", err);
      if (onError) onError(err);
    }
  },

  stop: async () => {
    try {
      await Speech.stop();
    } catch (err) {
      console.warn("Failed to stop speech", err);
    }
  },

  isSpeaking: async (): Promise<boolean> => {
    try {
      return await Speech.isSpeakingAsync();
    } catch (err) {
      return false;
    }
  },
};
