import React, { useState } from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useAccessibility } from '../../context/AccessibilityContext';
import { useLanguage } from '../../i18n/LanguageContext';
import { VoiceSpeechSynthesis } from '../../services/voice/speechSynthesis';

export interface SequentialStep {
  titleEn: string;
  titleHi: string;
  detailEn: string;
  detailHi: string;
  actionLabelEn?: string;
  actionLabelHi?: string;
  onAction?: () => void;
}

interface SequentialNavigatorProps {
  steps: SequentialStep[];
  onComplete?: () => void;
}

export const SequentialNavigator: React.FC<SequentialNavigatorProps> = ({ steps, onComplete }) => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const { textScale, highContrast, announce } = useAccessibility();
  const { language } = useLanguage();
  const tts = new VoiceSpeechSynthesis();

  if (!steps || steps.length === 0) return null;

  const currentStep = steps[currentStepIndex];
  const total = steps.length;

  const title = language === 'hi' ? currentStep.titleHi : currentStep.titleEn;
  const detail = language === 'hi' ? currentStep.detailHi : currentStep.detailEn;
  const stepAnnouncement = language === 'hi'
    ? `चरण ${currentStepIndex + 1} कुल ${total} में से: ${title}. ${detail}`
    : `Step ${currentStepIndex + 1} of ${total}: ${title}. ${detail}`;

  const speakCurrentStep = () => {
    announce(stepAnnouncement);
    tts.speak(stepAnnouncement, { language: language === 'hi' ? 'HINDI' : 'ENGLISH', speechSpeed: 'NORMAL' });
  };

  const handleNext = () => {
    if (currentStepIndex < total - 1) {
      const nextIdx = currentStepIndex + 1;
      setCurrentStepIndex(nextIdx);
      const nextStep = steps[nextIdx];
      const nextText = language === 'hi'
        ? `चरण ${nextIdx + 1}: ${nextStep.titleHi}. ${nextStep.detailHi}`
        : `Step ${nextIdx + 1}: ${nextStep.titleEn}. ${nextStep.detailEn}`;
      announce(nextText);
      tts.speak(nextText, { language: language === 'hi' ? 'HINDI' : 'ENGLISH', speechSpeed: 'NORMAL' });
    } else if (onComplete) {
      onComplete();
    }
  };

  const handlePrev = () => {
    if (currentStepIndex > 0) {
      const prevIdx = currentStepIndex - 1;
      setCurrentStepIndex(prevIdx);
      const prevStep = steps[prevIdx];
      const prevText = language === 'hi'
        ? `चरण ${prevIdx + 1}: ${prevStep.titleHi}. ${prevStep.detailHi}`
        : `Step ${prevIdx + 1}: ${prevStep.titleEn}. ${prevStep.detailEn}`;
      announce(prevText);
      tts.speak(prevText, { language: language === 'hi' ? 'HINDI' : 'ENGLISH', speechSpeed: 'NORMAL' });
    }
  };


  const bgColor = highContrast ? '#000000' : '#F8FAFC';
  const cardBg = highContrast ? '#111111' : '#FFFFFF';
  const textColor = highContrast ? '#FFFFFF' : '#0F172A';

  return (
    <View style={[styles.container, { backgroundColor: cardBg, borderColor: highContrast ? '#FFFF00' : '#CBD5E1' }]}>
      <View style={styles.headerRow}>
        <Text style={[styles.stepIndicator, { fontSize: 14 * textScale }]}>
          {language === 'hi' ? `चरण ${currentStepIndex + 1} / ${total}` : `Step ${currentStepIndex + 1} of ${total}`}
        </Text>
        <TouchableOpacity
          style={styles.audioBtn}
          onPress={speakCurrentStep}
          accessibilityRole="button"
          accessibilityLabel={language === 'hi' ? 'विवरण सुनें' : 'Listen to details'}
        >
          <Text style={styles.audioBtnText}>🔊 {language === 'hi' ? 'सुनें' : 'Listen'}</Text>
        </TouchableOpacity>
      </View>

      <Text style={[styles.title, { color: textColor, fontSize: 18 * textScale }]}>
        {title}
      </Text>

      <Text style={[styles.detail, { color: textColor, fontSize: 15 * textScale }]}>
        {detail}
      </Text>

      {currentStep.onAction && (
        <TouchableOpacity
          style={styles.actionBtn}
          onPress={currentStep.onAction}
          accessibilityRole="button"
          accessibilityLabel={language === 'hi' ? (currentStep.actionLabelHi || 'आगे बढ़ें') : (currentStep.actionLabelEn || 'Proceed')}
        >
          <Text style={styles.actionBtnText}>
            {language === 'hi' ? (currentStep.actionLabelHi || 'आगे बढ़ें') : (currentStep.actionLabelEn || 'Proceed')}
          </Text>
        </TouchableOpacity>
      )}

      <View style={styles.navRow}>
        <TouchableOpacity
          style={[styles.navBtn, currentStepIndex === 0 && styles.disabledBtn]}
          onPress={handlePrev}
          disabled={currentStepIndex === 0}
          accessibilityRole="button"
          accessibilityLabel={language === 'hi' ? 'पिछला चरण' : 'Previous step'}
        >
          <Text style={styles.navBtnText}>⬅️ {language === 'hi' ? 'पिछला' : 'Previous'}</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navBtnPrimary}
          onPress={handleNext}
          accessibilityRole="button"
          accessibilityLabel={language === 'hi' ? (currentStepIndex === total - 1 ? 'समाप्त करें' : 'अगला चरण') : (currentStepIndex === total - 1 ? 'Finish' : 'Next step')}
        >
          <Text style={styles.navBtnPrimaryText}>
            {currentStepIndex === total - 1 ? (language === 'hi' ? 'समाप्त ✔️' : 'Finish ✔️') : (language === 'hi' ? 'अगला ➡️' : 'Next ➡️')}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
    borderRadius: 16,
    borderWidth: 2,
    marginVertical: 12,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  stepIndicator: {
    fontWeight: '800',
    color: '#0EA5E9',
  },
  audioBtn: {
    backgroundColor: '#E0F2FE',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    minHeight: 36,
    justifyContent: 'center',
  },
  audioBtnText: {
    color: '#0284C7',
    fontWeight: '700',
    fontSize: 13,
  },
  title: {
    fontWeight: '800',
    marginBottom: 8,
  },
  detail: {
    lineHeight: 22,
    marginBottom: 16,
  },
  actionBtn: {
    backgroundColor: '#10B981',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 16,
    minHeight: 48,
    justifyContent: 'center',
  },
  actionBtnText: {
    color: '#FFFFFF',
    fontWeight: '800',
    fontSize: 15,
  },
  navRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  navBtn: {
    backgroundColor: '#E2E8F0',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 10,
    minHeight: 48,
    justifyContent: 'center',
  },
  disabledBtn: {
    opacity: 0.5,
  },
  navBtnText: {
    color: '#334155',
    fontWeight: '700',
  },
  navBtnPrimary: {
    backgroundColor: '#0284C7',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 10,
    minHeight: 48,
    justifyContent: 'center',
  },
  navBtnPrimaryText: {
    color: '#FFFFFF',
    fontWeight: '800',
  },
});
