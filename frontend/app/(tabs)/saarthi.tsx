import { useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import { Screen } from "@/components/Screen";
import { colors } from "@/constants/theme";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/i18n/LanguageContext";
import { api } from "@/services/api";
import { SaarthiMessage } from "@/types/api";

// Prompt 12 Voice Architecture Imports
import { getVoiceCapabilities } from "@/services/voice/voiceCapabilities";
import { createSpeechRecognitionProvider, SpeechRecognitionProvider } from "@/services/voice/speechRecognition";
import { speechSynthesis } from "@/services/voice/speechSynthesis";
import { voiceService } from "@/services/voice/voiceService";
import { FinancialEntity, VoiceCapabilities, VoiceSettings, VoiceState } from "@/services/voice/voiceTypes";

// Prompt 13 Accessibility Architecture Imports
import { useAccessibility } from "@/context/AccessibilityContext";
import { parseVoiceNavigationCommand } from "@/services/accessibility/voiceNavigation";
import { SequentialNavigator, SequentialStep } from "@/components/accessibility/SequentialNavigator";
import { BrandLogo } from "@/components/branding/BrandLogo";



const STARTER_PROMPTS_EN = [
  "How can I improve my financial health score?",
  "What should I focus on first with my monthly surplus?",
  "How much emergency buffer do I need?",
  "Help me plan for my primary financial goal.",
];

const STARTER_PROMPTS_HI = [
  "मैं अपना वित्तीय स्वास्थ्य स्कोर कैसे सुधार सकता हूँ?",
  "मासिक बचत का सबसे अच्छा उपयोग कैसे करें?",
  "मुझे कितनी आपातकालीन बचत की आवश्यकता है?",
  "मेरे मुख्य वित्तीय लक्ष्य की योजना बनाने में मदद करें।",
];

export default function SaarthiTab() {
  const { token, twin } = useAuth();
  const { language, t } = useLanguage();
  const { announce, accessibilityModeEnabled } = useAccessibility();
  const params = useLocalSearchParams<{ initialPrompt?: string }>();


  // Chat & Messaging State
  const [messages, setMessages] = useState<SaarthiMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [speakingMsgId, setSpeakingMsgId] = useState<number | null>(null);
  const flatListRef = useRef<FlatList>(null);

  // Prompt 12 Voice Architecture State
  const [mode, setMode] = useState<"TEXT" | "VOICE">("TEXT");
  const [voiceState, setVoiceState] = useState<VoiceState>("IDLE");
  const [capabilities, setCapabilities] = useState<VoiceCapabilities>(getVoiceCapabilities());
  const [voiceSettings, setVoiceSettings] = useState<VoiceSettings>(voiceService.getSettings());
  const [transcript, setTranscript] = useState("");
  const [detectedEntities, setDetectedEntities] = useState<FinancialEntity[]>([]);
  const [showConfirmCard, setShowConfirmCard] = useState(false);

  const recognitionProviderRef = useRef<SpeechRecognitionProvider | null>(null);

  // Load Voice Settings & Capabilities
  useEffect(() => {
    (async () => {
      const caps = getVoiceCapabilities();
      setCapabilities(caps);
      const settings = await voiceService.loadSettings();
      setVoiceSettings(settings);
      recognitionProviderRef.current = createSpeechRecognitionProvider(caps);
    })();
  }, []);

  // Load latest chat session on mount
  useEffect(() => {
    let mounted = true;
    (async () => {
      if (token) {
        try {
          const sessions = await api.getSaarthiSessions(token);
          if (mounted && sessions.length > 0) {
            const latestSession = sessions[0];
            setSessionId(latestSession.session_id);
            const history = await api.getSaarthiMessages(latestSession.session_id, token);
            if (mounted) setMessages(history);
          }
        } catch {
          // Ignore initial history error if no sessions exist
        } finally {
          if (mounted) setInitialLoading(false);
        }
      } else {
        if (mounted) setInitialLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, [token]);

  // Handle initialPrompt parameter passed from other domain screens
  useEffect(() => {
    if (params.initialPrompt && !loading) {
      handleSendMessage(params.initialPrompt);
    }
  }, [params.initialPrompt]);

  // Speech Recognition Control
  const startVoiceInput = () => {
    // Interruption / Barge-in: Stop AI speech if speaking
    voiceService.interruptSpeech();
    setSpeakingMsgId(null);

    setVoiceState("LISTENING");
    setTranscript("");
    setShowConfirmCard(false);

    const provider = recognitionProviderRef.current || createSpeechRecognitionProvider(capabilities);

    provider.startListening(voiceSettings.inputLanguage, {
      onStart: () => {
        setVoiceState("LISTENING");
      },
      onResult: (result) => {
        setTranscript(result.transcript);
        const entities = voiceService.detectFinancialEntities(result.transcript);
        setDetectedEntities(entities);

        if (result.isFinal) {
          setVoiceState("REVIEWING");
          const navResult = parseVoiceNavigationCommand(result.transcript, language);
          if (navResult.intent !== "UNKNOWN" && navResult.route) {
            announce(navResult.speakAnnouncement);
            router.push(navResult.route as any);
            return;
          }
          if (entities.some((e) => e.requiresConfirmation)) {
            setShowConfirmCard(true);
          } else if (voiceSettings.autoSendVoiceQuery) {
            handleSendMessage(result.transcript);
          }
        }

      },
      onError: (err) => {
        setError(`Voice Error: ${err}`);
        setVoiceState("ERROR");
      },

      onEnd: () => {
        setVoiceState((prev) => (prev === "LISTENING" ? "REVIEWING" : prev));
      },
    });
  };

  const stopVoiceInput = () => {
    if (recognitionProviderRef.current) {
      recognitionProviderRef.current.stopListening();
    }
    setVoiceState("REVIEWING");
  };

  const handleSendMessage = async (textToSend?: string) => {
    const messageText = textToSend || inputMessage.trim() || transcript.trim();
    if (!messageText || loading || !token) return;

    setError(null);
    setInputMessage("");
    setTranscript("");
    setShowConfirmCard(false);
    setVoiceState("THINKING");

    // Optimistically add user message to list
    const tempUserMsg: SaarthiMessage = {
      id: Date.now(),
      role: "user",
      content: messageText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setLoading(true);

    try {
      const response = await api.sendSaarthiMessage(messageText, sessionId || undefined, token);
      if (!sessionId) {
        setSessionId(response.session_id);
      }
      const saarthiMsg: SaarthiMessage = {
        id: response.message_id,
        role: "model",
        content: response.response,
        created_at: response.created_at,
      };
      setMessages((prev) => [...prev, saarthiMsg]);
      setVoiceState("IDLE");

      // Auto-speak AI response if enabled
      if (voiceSettings.autoSpeak && voiceSettings.voiceResponse) {
        setSpeakingMsgId(saarthiMsg.id);
        setVoiceState("SPEAKING");
        speechSynthesis.speak(saarthiMsg.content, {
          language: voiceSettings.inputLanguage === "HINDI" ? "HINDI" : language === "hi" ? "HINDI" : "ENGLISH",
          speechSpeed: voiceSettings.speechSpeed,
          onDone: () => {
            setSpeakingMsgId(null);
            setVoiceState("IDLE");
          },
          onError: () => {
            setSpeakingMsgId(null);
            setVoiceState("IDLE");
          },
        });
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to get response from Saarthi.");
      setVoiceState("ERROR");
    } finally {
      setLoading(false);
    }
  };

  const handleToggleTTS = (msgId: number, text: string) => {
    if (speakingMsgId === msgId) {
      speechSynthesis.stop();
      setSpeakingMsgId(null);
      setVoiceState("IDLE");
    } else {
      setSpeakingMsgId(msgId);
      setVoiceState("SPEAKING");
      speechSynthesis.speak(text, {
        language: language === "hi" ? "HINDI" : "ENGLISH",
        speechSpeed: voiceSettings.speechSpeed,
        onDone: () => {
          setSpeakingMsgId(null);
          setVoiceState("IDLE");
        },
        onError: () => {
          setSpeakingMsgId(null);
          setVoiceState("IDLE");
        },
      });
    }
  };

  const starterPrompts = language === "hi" ? STARTER_PROMPTS_HI : STARTER_PROMPTS_EN;

  const renderMessageItem = ({ item }: { item: SaarthiMessage }) => {
    const isUser = item.role === "user";
    const isSpeakingThis = speakingMsgId === item.id;

    return (
      <View style={[styles.messageWrapper, isUser ? styles.userWrapper : styles.saarthiWrapper]}>
        {!isUser && (
          <View style={styles.avatarMini}>
            <Text style={styles.avatarMiniText}>🤖</Text>
          </View>
        )}
        <View style={[styles.bubble, isUser ? styles.userBubble : styles.saarthiBubble]}>
          <Text style={[styles.messageText, isUser ? styles.userMessageText : styles.saarthiMessageText]}>
            {item.content}
          </Text>

          {!isUser && (
            <TouchableOpacity
              style={styles.ttsButton}
              onPress={() => handleToggleTTS(item.id, item.content)}
              accessibilityRole="button"
              accessibilityLabel={isSpeakingThis ? "Stop audio readout" : "Read AI message aloud"}
              accessibilityHint="Toggles text-to-speech for this AI response"
            >
              <Text style={styles.ttsButtonText}>
                {isSpeakingThis ? "⏹ " + t("voice.stop_speech") : "🔊 " + t("saarthi.listen")}
              </Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    );
  };

  return (
    <Screen style={styles.screenContainer}>
      <KeyboardAvoidingView
        style={styles.keyboardView}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        keyboardVerticalOffset={Platform.OS === "ios" ? 90 : 0}
      >
        {/* Header with Mode Toggle & Capability Note */}

        <View style={styles.header}>
          <View style={styles.titleRow}>
            <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
              <BrandLogo variant="chat" />
            </View>

            {/* Voice vs Text Mode Selector */}
            <View style={styles.modeToggleContainer}>
              <TouchableOpacity
                style={[styles.modeBtn, mode === "TEXT" && styles.modeBtnActive]}
                onPress={() => setMode("TEXT")}
                accessibilityRole="button"
                accessibilityLabel={t("voice.mode_text")}
              >
                <Text style={[styles.modeBtnText, mode === "TEXT" && styles.modeBtnTextActive]}>💬 Text</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.modeBtn, mode === "VOICE" && styles.modeBtnActive]}
                onPress={() => setMode("VOICE")}
                accessibilityRole="button"
                accessibilityLabel={t("voice.mode_voice")}
              >
                <Text style={[styles.modeBtnText, mode === "VOICE" && styles.modeBtnTextActive]}>🎙 Voice</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Honest Capability Banner */}
          {capabilities.level === "LIMITED_FALLBACK" && (
            <View style={styles.capabilityNotice}>
              <Text style={styles.capabilityText}>ℹ️ {capabilities.supportNote}</Text>
            </View>
          )}
        </View>

        {initialLoading ? (
          <View style={styles.centerContainer}>
            <ActivityIndicator size="large" color={colors.purple} />
            <Text style={styles.loadingText}>Connecting to Saarthi...</Text>
          </View>
        ) : (
          <View style={styles.chatContainer}>
            {messages.length === 0 ? (
              <View style={styles.emptyContainer}>
                <BrandLogo variant="header" style={{ marginBottom: 12 }} />
                <Text style={styles.emptyTitle}>
                  {language === "hi" ? "नमस्ते! मैं AI सारथी हूँ" : "Namaste! I'm AI Saarthi"}
                </Text>

                <Text style={styles.emptyDesc}>
                  {language === "hi"
                    ? `मैंने आपके फाइनेंशियल ट्विन (स्कोर: ${twin?.financial_health_score ?? "--"}/100) का विश्लेषण किया है। मुझसे अपनी बचत, खर्चों या लक्ष्यों के बारे में पूछें!`
                    : `I've analyzed your Financial Twin (Score: ${twin?.financial_health_score ?? "--"}/100). Ask me anything about your savings, expenses, or financial goals!`}
                </Text>


                <Text style={styles.starterHeading}>SUGGESTED QUESTIONS</Text>
                <View style={styles.starterContainer}>
                  {starterPrompts.map((prompt, idx) => (
                    <Pressable
                      key={idx}
                      style={styles.starterPill}
                      onPress={() => handleSendMessage(prompt)}
                      disabled={loading}
                      accessibilityRole="button"
                      accessibilityLabel={`Suggested question: ${prompt}`}
                    >
                      <Text style={styles.starterPillText}>{prompt}</Text>
                    </Pressable>
                  ))}
                </View>

              </View>
            ) : (
              <FlatList
                ref={flatListRef}
                data={messages}
                keyExtractor={(item) => item.id.toString()}
                renderItem={renderMessageItem}
                contentContainerStyle={styles.messagesList}
                onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
                onLayout={() => flatListRef.current?.scrollToEnd({ animated: true })}
              />
            )}

            {/* High Impact Financial Value Confirmation Card */}
            {showConfirmCard && (
              <View style={styles.confirmCard}>
                <Text style={styles.confirmTitle}>⚠️ {t("voice.confirm_financial_title")}</Text>
                <Text style={styles.confirmMsg}>{t("voice.confirm_financial_msg")}</Text>
                {detectedEntities.map((ent, i) => (
                  <Text key={i} style={styles.confirmValue}>• {ent.rawText}</Text>
                ))}
                <Text style={styles.transcriptPreview}>"{transcript}"</Text>
                <View style={styles.confirmActionRow}>
                  <TouchableOpacity
                    style={styles.confirmSendBtn}
                    onPress={() => handleSendMessage(transcript)}
                    accessibilityRole="button"
                    accessibilityLabel={t("voice.confirm_btn")}
                  >
                    <Text style={styles.confirmSendText}>{t("voice.confirm_btn")}</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={styles.confirmCancelBtn}
                    onPress={() => setShowConfirmCard(false)}
                    accessibilityRole="button"
                    accessibilityLabel={t("voice.cancel_btn")}
                  >
                    <Text style={styles.confirmCancelText}>{t("voice.cancel_btn")}</Text>
                  </TouchableOpacity>
                </View>
              </View>
            )}

            {/* Voice Mode Main Controls */}
            {mode === "VOICE" ? (
              <View style={styles.voiceModePanel}>
                {voiceState === "LISTENING" ? (
                  <TouchableOpacity
                    style={[styles.bigMicBtn, styles.bigMicActive]}
                    onPress={stopVoiceInput}
                    accessibilityRole="button"
                    accessibilityLabel="Stop voice input"
                    accessibilityState={{ busy: true }}
                  >
                    <Text style={styles.bigMicIcon}>🛑</Text>
                    <Text style={styles.bigMicStatus}>{t("voice.listening_active")}</Text>
                  </TouchableOpacity>
                ) : (
                  <TouchableOpacity
                    style={styles.bigMicBtn}
                    onPress={startVoiceInput}
                    disabled={loading}
                    accessibilityRole="button"
                    accessibilityLabel={t("voice.tap_to_speak")}
                  >
                    <Text style={styles.bigMicIcon}>🎙</Text>
                    <Text style={styles.bigMicStatus}>{t("voice.tap_to_speak")}</Text>
                  </TouchableOpacity>
                )}

                {/* Live Transcript Preview Box */}
                {Boolean(transcript) && !showConfirmCard && (
                  <View style={styles.transcriptBox}>
                    <Text style={styles.transcriptLabel}>{t("voice.transcript_review")}</Text>
                    <Text style={styles.transcriptContent}>"{transcript}"</Text>
                    <View style={styles.transcriptBtnRow}>
                      <TouchableOpacity
                        style={styles.transcriptSendBtn}
                        onPress={() => handleSendMessage(transcript)}
                        accessibilityRole="button"
                        accessibilityLabel={t("voice.confirm_btn")}
                      >
                        <Text style={styles.transcriptSendText}>{t("saarthi.send")}</Text>
                      </TouchableOpacity>
                      <TouchableOpacity
                        style={styles.transcriptClearBtn}
                        onPress={() => setTranscript("")}
                        accessibilityRole="button"
                        accessibilityLabel={t("voice.cancel_btn")}
                      >
                        <Text style={styles.transcriptClearText}>{t("voice.cancel_btn")}</Text>
                      </TouchableOpacity>
                    </View>
                  </View>
                )}
              </View>
            ) : (
              /* Text Input Bar */
              <View style={styles.inputBar}>
                <TextInput
                  style={styles.textInput}
                  placeholder={t("saarthi.type_placeholder")}
                  placeholderTextColor={colors.muted}
                  value={inputMessage}
                  onChangeText={setInputMessage}
                  multiline
                  maxLength={1000}
                  editable={!loading}
                  accessibilityLabel="Saarthi Message Input Box"
                />

                <Pressable
                  style={[
                    styles.sendButton,
                    (!inputMessage.trim() || loading) && styles.sendButtonDisabled,
                  ]}
                  onPress={() => handleSendMessage()}
                  disabled={!inputMessage.trim() || loading}
                  accessibilityRole="button"
                  accessibilityLabel={t("saarthi.send")}
                >
                  <Text style={styles.sendButtonText}>{t("saarthi.send")}</Text>
                </Pressable>
              </View>
            )}
          </View>
        )}
      </KeyboardAvoidingView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  screenContainer: {
    padding: 16,
  },
  keyboardView: {
    flex: 1,
  },
  header: {
    marginBottom: 12,
  },
  titleRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: "800",
    color: colors.ink,
  },
  modeToggleContainer: {
    flexDirection: "row",
    backgroundColor: colors.lavender,
    borderRadius: 20,
    padding: 3,
  },
  modeBtn: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  modeBtnActive: {
    backgroundColor: colors.purple,
  },
  modeBtnText: {
    fontSize: 12,
    fontWeight: "700",
    color: colors.purple,
  },
  modeBtnTextActive: {
    color: "#FFFFFF",
  },
  capabilityNotice: {
    marginTop: 8,
    backgroundColor: "#EFF8FF",
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#B2DDFF",
  },
  capabilityText: {
    fontSize: 11,
    color: "#175CD3",
    fontWeight: "600",
  },
  centerContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  loadingText: {
    marginTop: 12,
    color: colors.muted,
    fontSize: 14,
  },
  chatContainer: {
    flex: 1,
    justifyContent: "space-between",
  },
  emptyContainer: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 12,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 12,
  },
  emptyTitle: {
    fontSize: 22,
    fontWeight: "800",
    color: colors.ink,
    marginBottom: 8,
    textAlign: "center",
  },
  emptyDesc: {
    fontSize: 14,
    color: colors.muted,
    textAlign: "center",
    lineHeight: 20,
    marginBottom: 24,
  },
  starterHeading: {
    fontSize: 11,
    fontWeight: "800",
    color: colors.purple,
    letterSpacing: 1,
    alignSelf: "flex-start",
    marginBottom: 10,
  },
  starterContainer: {
    width: "100%",
  },
  starterPill: {
    backgroundColor: "#FFFFFF",
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 10,
  },
  starterPillText: {
    fontSize: 14,
    fontWeight: "600",
    color: colors.ink,
  },
  messagesList: {
    paddingVertical: 12,
  },
  messageWrapper: {
    flexDirection: "row",
    marginBottom: 14,
    alignItems: "flex-end",
  },
  userWrapper: {
    justifyContent: "flex-end",
  },
  saarthiWrapper: {
    justifyContent: "flex-start",
  },
  avatarMini: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.lavender,
    alignItems: "center",
    justifyContent: "center",
    marginRight: 8,
  },
  avatarMiniText: {
    fontSize: 16,
  },
  bubble: {
    maxWidth: "80%",
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 18,
  },
  userBubble: {
    backgroundColor: colors.purple,
    borderBottomRightRadius: 4,
  },
  saarthiBubble: {
    backgroundColor: colors.lavender,
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: colors.purple + "22",
  },
  messageText: {
    fontSize: 15,
    lineHeight: 22,
  },
  userMessageText: {
    color: "#FFFFFF",
  },
  saarthiMessageText: {
    color: colors.ink,
  },
  ttsButton: {
    marginTop: 6,
    alignSelf: "flex-end",
    backgroundColor: "#ffffff",
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.purple + "33",
  },
  ttsButtonText: {
    fontSize: 11,
    fontWeight: "700",
    color: colors.purple,
  },
  confirmCard: {
    backgroundColor: "#FEF3F2",
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: "#FECDCA",
    marginBottom: 12,
  },
  confirmTitle: {
    fontSize: 14,
    fontWeight: "800",
    color: colors.danger,
    marginBottom: 4,
  },
  confirmMsg: {
    fontSize: 12,
    color: colors.ink,
    marginBottom: 6,
  },
  confirmValue: {
    fontSize: 13,
    fontWeight: "700",
    color: colors.purple,
  },
  transcriptPreview: {
    fontSize: 13,
    fontStyle: "italic",
    color: colors.muted,
    marginVertical: 6,
  },
  confirmActionRow: {
    flexDirection: "row",
    gap: 10,
    marginTop: 8,
  },
  confirmSendBtn: {
    backgroundColor: colors.purple,
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
  },
  confirmSendText: {
    color: "#FFFFFF",
    fontSize: 12,
    fontWeight: "700",
  },
  confirmCancelBtn: {
    backgroundColor: colors.border,
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
  },
  confirmCancelText: {
    color: colors.ink,
    fontSize: 12,
    fontWeight: "600",
  },
  voiceModePanel: {
    alignItems: "center",
    paddingVertical: 16,
  },
  bigMicBtn: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: colors.purple,
    alignItems: "center",
    justifyContent: "center",
    elevation: 4,
    shadowColor: colors.purple,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
  },
  bigMicActive: {
    backgroundColor: colors.danger,
  },
  bigMicIcon: {
    fontSize: 36,
  },
  bigMicStatus: {
    color: "#FFFFFF",
    fontSize: 11,
    fontWeight: "700",
    marginTop: 4,
  },
  transcriptBox: {
    width: "100%",
    backgroundColor: "#FFFFFF",
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: colors.border,
    marginTop: 16,
  },
  transcriptLabel: {
    fontSize: 12,
    fontWeight: "700",
    color: colors.purple,
    marginBottom: 4,
  },
  transcriptContent: {
    fontSize: 14,
    color: colors.ink,
    fontStyle: "italic",
    marginBottom: 10,
  },
  transcriptBtnRow: {
    flexDirection: "row",
    justifyContent: "flex-end",
    gap: 10,
  },
  transcriptSendBtn: {
    backgroundColor: colors.purple,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  transcriptSendText: {
    color: "#FFFFFF",
    fontWeight: "700",
    fontSize: 13,
  },
  transcriptClearBtn: {
    backgroundColor: colors.border,
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
  },
  transcriptClearText: {
    color: colors.ink,
    fontWeight: "600",
    fontSize: 13,
  },
  inputBar: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#FFFFFF",
    borderRadius: 24,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: 10,
    paddingVertical: 6,
    marginTop: 8,
    gap: 8,
  },
  textInput: {
    flex: 1,
    fontSize: 15,
    color: colors.ink,
    maxHeight: 100,
    paddingVertical: 6,
  },
  sendButton: {
    backgroundColor: colors.purple,
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
  },
  sendButtonDisabled: {
    backgroundColor: colors.border,
  },
  sendButtonText: {
    color: "#FFFFFF",
    fontWeight: "700",
    fontSize: 14,
  },
});
