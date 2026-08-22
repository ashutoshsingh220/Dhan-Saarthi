import React from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useAccessibility } from '../../context/AccessibilityContext';
import { useLanguage } from '../../i18n/LanguageContext';

export const AccessibilityModeBanner: React.FC = () => {
  const { accessibilityModeEnabled, accessibilityProfile, toggleAccessibilityMode, textScale, highContrast } = useAccessibility();
  const { language } = useLanguage();

  if (!accessibilityModeEnabled) return null;

  const profileLabelsEn: Record<string, string> = {
    STANDARD: 'Standard Assist',
    VISUAL_ASSIST: 'Visual Assist (Screen-Reader Optimized)',
    VOICE_ASSIST: 'Voice Assist (Audio-First)',
    LOW_LITERACY: 'Simplified Text & Spoken Guidance',
    ELDERLY_FRIENDLY: 'Elderly Friendly (Paced & Clear)',
  };

  const profileLabelsHi: Record<string, string> = {
    STANDARD: 'मानक सहायता',
    VISUAL_ASSIST: 'दृष्टि सहायता (स्क्रीन रीडर अनुकूलित)',
    VOICE_ASSIST: 'वॉइस सहायता (ऑडियो-प्रथम)',
    LOW_LITERACY: 'सरल भाषा व बोली सहायता',
    ELDERLY_FRIENDLY: 'वरिष्ठ नागरिक सहायता (धीमी व स्पष्ट)',
  };

  const activeLabel = language === 'hi' 
    ? (profileLabelsHi[accessibilityProfile] || accessibilityProfile)
    : (profileLabelsEn[accessibilityProfile] || accessibilityProfile);

  return (
    <View style={[styles.banner, highContrast && styles.bannerHighContrast]}>
      <View style={styles.content}>
        <Text style={[styles.title, { fontSize: 14 * textScale }]}>
          ♿ {language === 'hi' ? 'एक्सेसिबिलिटी मोड सक्रिय' : 'ACCESSIBILITY MODE ACTIVE'}
        </Text>
        <Text style={[styles.subtitle, { fontSize: 13 * textScale }]}>
          {activeLabel}
        </Text>
      </View>

      <TouchableOpacity
        style={styles.offBtn}
        onPress={() => toggleAccessibilityMode(false)}
        accessibilityRole="button"
        accessibilityLabel={language === 'hi' ? 'एक्सेसिबिलिटी मोड बंद करें' : 'Turn off accessibility mode'}
      >
        <Text style={styles.offBtnText}>
          {language === 'hi' ? 'बंद करें (OFF)' : 'TURN OFF'}
        </Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  banner: {
    backgroundColor: '#0F172A',
    paddingHorizontal: 16,
    paddingVertical: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderRadius: 12,
    marginHorizontal: 16,
    marginTop: 8,
    borderWidth: 1.5,
    borderColor: '#38BDF8',
  },
  bannerHighContrast: {
    backgroundColor: '#000000',
    borderColor: '#FFFF00',
    borderWidth: 2,
  },
  content: {
    flex: 1,
    paddingRight: 8,
  },
  title: {
    color: '#38BDF8',
    fontWeight: '900',
    letterSpacing: 0.5,
  },
  subtitle: {
    color: '#F8FAFC',
    fontWeight: '600',
    marginTop: 2,
  },
  offBtn: {
    backgroundColor: '#EF4444',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    minHeight: 44,
    justifyContent: 'center',
  },
  offBtnText: {
    color: '#FFFFFF',
    fontWeight: '800',
    fontSize: 12,
  },
});
