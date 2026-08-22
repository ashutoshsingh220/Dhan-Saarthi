import React, { createContext, useContext, useEffect, useState } from "react";
import * as SecureStore from "expo-secure-store";
import { en } from "./translations/en";
import { hi } from "./translations/hi";

export type SupportedLanguage = "en" | "hi";

interface LanguageContextType {
  language: SupportedLanguage;
  setLanguage: (lang: SupportedLanguage) => Promise<void>;
  voiceAssistanceEnabled: boolean;
  setVoiceAssistanceEnabled: (enabled: boolean) => Promise<void>;
  t: (key: string, params?: Record<string, string | number>) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<SupportedLanguage>("en");
  const [voiceAssistanceEnabled, setVoiceAssistanceState] = useState<boolean>(true);

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      const storedLang = await SecureStore.getItemAsync("user_language");
      if (storedLang === "en" || storedLang === "hi") {
        setLanguageState(storedLang);
      }

      const storedVoice = await SecureStore.getItemAsync("voice_assistance_enabled");
      if (storedVoice !== null) {
        setVoiceAssistanceState(storedVoice === "true");
      }
    } catch (err) {
      console.warn("Failed to load language/voice preferences", err);
    }
  };

  const setLanguage = async (lang: SupportedLanguage) => {
    setLanguageState(lang);
    try {
      await SecureStore.setItemAsync("user_language", lang);
    } catch (err) {
      console.warn("Failed to persist language preference", err);
    }
  };

  const setVoiceAssistanceEnabled = async (enabled: boolean) => {
    setVoiceAssistanceState(enabled);
    try {
      await SecureStore.setItemAsync("voice_assistance_enabled", enabled ? "true" : "false");
    } catch (err) {
      console.warn("Failed to persist voice assistance preference", err);
    }
  };

  const t = (key: string, params?: Record<string, string | number>): string => {
    const dict = language === "hi" ? hi : en;
    let val = dict[key] || en[key] || key;

    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        val = val.replace(new RegExp(`\\{${k}\\}`, "g"), String(v));
      });
    }

    return val;
  };

  return (
    <LanguageContext.Provider
      value={{
        language,
        setLanguage,
        voiceAssistanceEnabled,
        setVoiceAssistanceEnabled,
        t,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
};
