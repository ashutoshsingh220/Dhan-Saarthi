import { Stack } from "expo-router";
import { AuthProvider } from "@/context/AuthContext";
import { LanguageProvider } from "@/i18n/LanguageContext";
import { AccessibilityProvider } from "@/context/AccessibilityContext";

export default function Layout() {
  return (
    <LanguageProvider>
      <AccessibilityProvider>
        <AuthProvider>
          <Stack screenOptions={{ headerShown: false }} />
        </AuthProvider>
      </AccessibilityProvider>
    </LanguageProvider>
  );
}

