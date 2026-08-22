import React from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useRouter } from 'expo-router';
import { useAccessibility } from '../../context/AccessibilityContext';
import { useLanguage } from '../../i18n/LanguageContext';

export const AccessibleQuickActions: React.FC = () => {
  const router = useRouter();
  const { accessibilityModeEnabled, textScale, highContrast } = useAccessibility();
  const { language } = useLanguage();

  if (!accessibilityModeEnabled) return null;

  const actions = [
    {
      id: 'saarthi',
      icon: '🎙️',
      titleEn: '1. Ask Saarthi',
      titleHi: '१. सारथी से पूछें',
      hintEn: 'Opens voice AI conversation',
      hintHi: 'वॉइस AI चैट खोलता है',
      route: '/(tabs)/saarthi',
    },
    {
      id: 'twin',
      icon: '💰',
      titleEn: '2. My Money',
      titleHi: '२. मेरी बचत व स्कोर',
      hintEn: 'Opens Financial Twin dashboard and score',
      hintHi: 'फाइनेंशियल ट्विन स्कोर खोलता है',
      route: '/domain/financial-twin',
    },
    {
      id: 'goals',
      icon: '🎯',
      titleEn: '3. My Goals',
      titleHi: '३. मेरे लक्ष्य',
      hintEn: 'Opens financial planning goals',
      hintHi: 'लक्ष्य और योजनाएं खोलता है',
      route: '/domain/planning',
    },
    {
      id: 'schemes',
      icon: '🌾',
      titleEn: '4. Govt Schemes',
      titleHi: '४. सरकारी योजनाएँ',
      hintEn: 'Opens farmer and small business schemes',
      hintHi: 'किसान व बिजनेस योजनाएँ खोलता है',
      route: '/domain/schemes',
    },
    {
      id: 'scam',
      icon: '🛡️',
      titleEn: '5. Scam Check',
      titleHi: '५. धोखाधड़ी जांच',
      hintEn: 'Opens scam shield fraud detector',
      hintHi: 'स्कैम चेकर खोलता है',
      route: '/domain/scam-shield',
    },
    {
      id: 'learn',
      icon: '📚',
      titleEn: '6. Learn',
      titleHi: '६. वित्तीय साक्षरता',
      hintEn: 'Opens financial literacy lessons',
      hintHi: 'वित्तीय शिक्षा खोलता है',
      route: '/(tabs)/learn',
    },
    {
      id: 'market',
      icon: '📈',
      titleEn: '7. Market Update',
      titleHi: '७. मार्केट अपडेट',
      hintEn: 'Opens live market intelligence',
      hintHi: 'मार्केट अपडेट खोलता है',
      route: '/domain/market-intelligence',
    },
    {
      id: 'recommendations',
      icon: '⭐',
      titleEn: '8. Next Actions',
      titleHi: '८. क्या करना चाहिए',
      hintEn: 'Opens personalized financial guidance',
      hintHi: 'व्यक्तिगत वित्तीय सुझाव खोलता है',
      route: '/domain/recommendations',
    },
  ];

  const bgColor = highContrast ? '#000000' : '#F4F7FB';
  const cardBg = highContrast ? '#111111' : '#FFFFFF';
  const textColor = highContrast ? '#FFFFFF' : '#1E293B';
  const borderColor = highContrast ? '#FFFF00' : '#E2E8F0';

  return (
    <View style={[styles.container, { backgroundColor: bgColor }]}>
      <Text
        style={[
          styles.heading,
          { color: textColor, fontSize: 18 * textScale },
        ]}
        accessibilityRole="header"
      >
        {language === 'hi' ? '♿ सुलभ त्वरित कार्रवाइयां (Quick Actions)' : '♿ Accessible Quick Actions'}
      </Text>

      <View style={styles.grid}>
        {actions.map((act) => (
          <TouchableOpacity
            key={act.id}
            style={[
              styles.actionBtn,
              { backgroundColor: cardBg, borderColor: borderColor },
            ]}
            onPress={() => router.push(act.route as any)}
            accessibilityRole="button"
            accessibilityLabel={language === 'hi' ? act.titleHi : act.titleEn}
            accessibilityHint={language === 'hi' ? act.hintHi : act.hintEn}
            activeOpacity={0.7}
          >
            <Text style={styles.icon}>{act.icon}</Text>
            <Text style={[styles.btnText, { color: textColor, fontSize: 15 * textScale }]}>
              {language === 'hi' ? act.titleHi : act.titleEn}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
    borderRadius: 16,
    marginVertical: 12,
  },
  heading: {
    fontWeight: '800',
    marginBottom: 12,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionBtn: {
    width: '48%',
    minHeight: 64, // > 56px logical pixels
    paddingHorizontal: 12,
    paddingVertical: 14,
    borderRadius: 12,
    borderWidth: 2,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
  },
  icon: {
    fontSize: 24,
    marginRight: 8,
  },
  btnText: {
    fontWeight: '700',
    flexShrink: 1,
  },
});
