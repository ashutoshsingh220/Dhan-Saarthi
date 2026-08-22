import React, { useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Modal,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { useLanguage } from "@/i18n/LanguageContext";
import { colors } from "@/constants/theme";

interface VoiceInputProps {
  onSpeechResult: (text: string) => void;
  disabled?: boolean;
}

export const VoiceInput: React.FC<VoiceInputProps> = ({ onSpeechResult, disabled }) => {
  const { language, t } = useLanguage();
  const [listening, setListening] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);

  const voiceSamples = language === "hi"
    ? [
        "मेरा फाइनेंशियल हेल्थ स्कोर समझाओ",
        "क्या यह मैसेज एक स्कैम है?",
        "मैं हर महीने ज़्यादा बचत कैसे करूँ?",
        "स्मार्ट फाइनेंशियल प्लान क्या है?",
      ]
    : [
        "Explain my financial health score",
        "Is this suspicious message a scam?",
        "How can I save more money every month?",
        "How does my smart goal plan work?",
      ];

  const handlePressMic = () => {
    if (disabled) return;

    // Check for browser / WebView Web Speech API
    if (typeof window !== "undefined" && ("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
      try {
        setListening(true);
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = language === "hi" ? "hi-IN" : "en-US";

        recognition.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          setListening(false);
          if (transcript && transcript.trim()) {
            onSpeechResult(transcript.trim());
          }
        };

        recognition.onerror = (event: any) => {
          console.warn("Speech recognition error", event.error);
          setListening(false);
          // Fallback to voice modal if web speech fails
          setModalVisible(true);
        };

        recognition.onend = () => {
          setListening(false);
        };

        recognition.start();
        return;
      } catch (err) {
        console.warn("Native web speech start error", err);
        setListening(false);
      }
    }

    // Expo Go / Mobile Managed Fallback Modal
    setModalVisible(true);
  };

  const handleSelectSample = (sample: string) => {
    onSpeechResult(sample);
    setModalVisible(false);
  };

  return (
    <View>
      <TouchableOpacity
        style={[styles.micBtn, listening && styles.micBtnListening]}
        onPress={handlePressMic}
        disabled={disabled}
        accessibilityLabel="Voice Input Microphone Button"
        accessibilityHint="Tap to speak your question to AI Saarthi"
        accessibilityRole="button"
      >
        {listening ? (
          <ActivityIndicator size="small" color="#ffffff" />
        ) : (
          <Text style={styles.micIcon}>🎙️</Text>
        )}
      </TouchableOpacity>

      {/* Voice Input Modal */}
      <Modal visible={modalVisible} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>🎙️ {t("saarthi.voice_input")}</Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Text style={styles.closeText}>✕</Text>
              </TouchableOpacity>
            </View>

            <Text style={styles.modalSubtitle}>
              {language === "hi"
                ? "आवाज़ से प्रश्न पूछें या नीचे दिए गए बोलचाल के सुझावों में से चुनें:"
                : "Speak your query or select a voice prompt shortcut below:"}
            </Text>

            <View style={styles.sampleList}>
              {voiceSamples.map((sample, idx) => (
                <TouchableOpacity
                  key={idx}
                  style={styles.sampleChip}
                  onPress={() => handleSelectSample(sample)}
                  accessibilityRole="button"
                  accessibilityLabel={`Voice prompt sample: ${sample}`}
                >
                  <Text style={styles.sampleIcon}>🗣️</Text>
                  <Text style={styles.sampleText}>"{sample}"</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  micBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.lavender,
    justifyContent: "center",
    alignItems: "center",
    borderWidth: 1,
    borderColor: colors.purple + "44",
  },
  micBtnListening: {
    backgroundColor: "#dc2626",
    borderColor: "#ef4444",
  },
  micIcon: {
    fontSize: 20,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.5)",
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  modalContent: {
    backgroundColor: "#ffffff",
    borderRadius: 20,
    padding: 20,
    width: "100%",
    maxWidth: 400,
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  modalHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: "800",
    color: colors.ink,
  },
  closeText: {
    fontSize: 18,
    color: colors.muted,
    fontWeight: "700",
  },
  modalSubtitle: {
    fontSize: 13,
    color: colors.muted,
    marginBottom: 16,
    lineHeight: 18,
  },
  sampleList: {
    gap: 10,
  },
  sampleChip: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#f8fafc",
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#cbd5e1",
    gap: 10,
  },
  sampleIcon: {
    fontSize: 18,
  },
  sampleText: {
    fontSize: 14,
    fontWeight: "600",
    color: colors.ink,
    flex: 1,
  },
});
