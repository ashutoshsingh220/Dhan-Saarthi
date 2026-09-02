import React, { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  FlatList,
  ListRenderItem,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { router } from "expo-router";
import * as SecureStore from "expo-secure-store";
import { Button } from "@/components/Form";
import { Screen } from "@/components/Screen";
import { colors } from "@/constants/theme";
import { api } from "@/services/api";

import { useAuth } from "@/context/AuthContext";
import type { ScamScan } from "@/types/api";


import * as ImagePicker from 'expo-image-picker';

export default function ScamShieldScreen() {
  const { token } = useAuth();
  const [inputText, setInputText] = useState("");
  const [selectedImageUri, setSelectedImageUri] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [currentScan, setCurrentScan] = useState<ScamScan | null>(null);
  const [history, setHistory] = useState<ScamScan[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, [token]);

  const fetchHistory = async () => {
    try {
      setLoadingHistory(true);
      if (!token) return;
      const res = await api.getScamHistory(token);
      setHistory(res.scans);
    } catch (err) {
      console.warn("Failed to load scam history", err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      quality: 0.8,
    });

    if (!result.canceled && result.assets && result.assets.length > 0) {
      setSelectedImageUri(result.assets[0].uri);
      setInputText(""); // clear text if image selected
    }
  };

  const handleAnalyzeImage = async () => {
    if (!selectedImageUri) return;
    try {
      setAnalyzing(true);
      if (!token) {
        Alert.alert("Authentication Error", "Please sign in to analyze messages.");
        return;
      }
      const scan = await api.analyzeScamImage(selectedImageUri, "image/jpeg", token);
      setCurrentScan(scan);
      fetchHistory();
    } catch (err: any) {
      Alert.alert("Analysis Failed", err.message || "Failed to analyze image. Please try again.");
    } finally {
      setAnalyzing(false);
    }
  };

  const handleAnalyze = async () => {
    if (selectedImageUri) {
      return handleAnalyzeImage();
    }
    
    if (!inputText.trim() || inputText.trim().length < 5) {
      Alert.alert("Invalid Input", "Please enter a message with at least 5 characters to analyze.");
      return;
    }

    try {
      setAnalyzing(true);
      if (!token) {
        Alert.alert("Authentication Error", "Please sign in to analyze messages.");
        return;
      }

      const scan = await api.analyzeScamMessage(inputText.trim(), token);
      setCurrentScan(scan);
      fetchHistory();
    } catch (err: any) {
      Alert.alert("Analysis Failed", err.message || "Failed to analyze message. Please try again.");
    } finally {
      setAnalyzing(false);
    }
  };

  const askSaarthiAboutScan = (scan: ScamScan) => {
    const promptMessage = `Please explain this Scam Shield result in simple language. Why was this message assigned a risk score of ${scan.risk_score}/100 (${scan.risk_level})? Message/Text: "${scan.extracted_text || scan.input_text}". Explain the detected indicators, related evidence patterns, and tell me what safe action I should take without changing the deterministic scam score.`;
    router.push({
      pathname: "/(tabs)/saarthi",
      params: { initialPrompt: promptMessage },
    });
  };


  const getRiskColor = (level: string) => {
    switch (level) {
      case "CRITICAL":
        return "#dc2626";
      case "HIGH":
        return "#ea580c";
      case "MODERATE":
        return "#d97706";
      case "LOW":
      default:
        return "#16a34a";
    }
  };

  const getRiskBg = (level: string) => {
    switch (level) {
      case "CRITICAL":
        return "#fef2f2";
      case "HIGH":
        return "#fff7ed";
      case "MODERATE":
        return "#fffbeb";
      case "LOW":
      default:
        return "#f0fdf4";
    }
  };

  const renderHistoryItem: ListRenderItem<ScamScan> = ({ item: scan }) => (
    <TouchableOpacity
      style={styles.historyItem}
      onPress={() => setCurrentScan(scan)}
    >
      <View style={styles.historyTop}>
        <View style={[styles.miniRiskBadge, { backgroundColor: getRiskBg(scan.risk_level) }]}>
          <Text style={[styles.miniRiskText, { color: getRiskColor(scan.risk_level) }]}>
            {scan.risk_level} ({scan.risk_score})
          </Text>
        </View>
        <Text style={styles.historyDate}>
          {new Date(scan.created_at).toLocaleDateString()}
        </Text>
      </View>
      <Text style={styles.historyText} numberOfLines={2}>
        "{scan.input_text}"
      </Text>
    </TouchableOpacity>
  );

  const listHeader = (
    <>
      {/* HEADER */}
      <View style={styles.header}>
        <Text style={styles.headerIcon}>🛡️</Text>
        <Text style={styles.headerTitle}>Scam Shield</Text>
        <Text style={styles.headerSubtitle}>Check suspicious financial messages before taking action.</Text>
      </View>

      {/* INPUT CARD */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Analyze Suspicious Message</Text>
        
        <View style={{ flexDirection: 'row', marginBottom: 12, gap: 8 }}>
          <TouchableOpacity 
            style={[styles.sampleChip, !selectedImageUri ? { backgroundColor: colors.purple, borderColor: colors.purple } : {}]}
            onPress={() => setSelectedImageUri(null)}
          >
            <Text style={[styles.sampleText, !selectedImageUri ? { color: 'white' } : {}]}>📝 Paste Text</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.sampleChip, selectedImageUri ? { backgroundColor: colors.purple, borderColor: colors.purple } : {}]}
            onPress={pickImage}
          >
            <Text style={[styles.sampleText, selectedImageUri ? { color: 'white' } : {}]}>📸 Analyze Screenshot</Text>
          </TouchableOpacity>
        </View>

        {!selectedImageUri ? (
          <>
            <TextInput
              style={styles.textInput}
              multiline
              numberOfLines={4}
              placeholder="Paste suspicious SMS, WhatsApp message, email, or financial message here..."
              placeholderTextColor="#9ca3af"
              value={inputText}
              onChangeText={setInputText}
            />

            {/* Quick Demo Shortcuts */}
            <Text style={styles.sampleLabel}>Quick Samples for Testing:</Text>
            <View style={styles.sampleContainer}>
              <TouchableOpacity
                style={styles.sampleChip}
                onPress={() =>
                  setInputText("Urgent: Your SBI bank account will be blocked today! Verify KYC at http://bit.ly/fake-kyc and enter OTP.")
                }
              >
                <Text style={styles.sampleText}>⚠️ Scam Sample</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.sampleChip}
                onPress={() =>
                  setInputText("Your monthly bank statement is ready. You can view it securely through the official banking application.")
                }
              >
                <Text style={styles.sampleText}>✅ Safe Sample</Text>
              </TouchableOpacity>
            </View>
          </>
        ) : (
          <View style={{ alignItems: 'center', marginBottom: 16 }}>
             <Text style={{ marginBottom: 8, color: colors.muted }}>Screenshot selected for OCR analysis.</Text>
             <TouchableOpacity style={styles.sampleChip} onPress={() => setSelectedImageUri(null)}>
               <Text style={styles.sampleText}>Remove Image</Text>
             </TouchableOpacity>
          </View>
        )}

        <Button
          title={analyzing ? "Analyzing..." : (selectedImageUri ? "Analyze Screenshot" : "Analyze Message")}
          onPress={handleAnalyze}
          disabled={analyzing || (!inputText && !selectedImageUri)}
        />
      </View>

      {/* ANALYSIS RESULT CARD */}
      {currentScan && (
        <View style={[styles.card, { borderColor: getRiskColor(currentScan.risk_level), borderWidth: 2 }]}>
          <View style={styles.resultHeader}>
            <View>
              <Text style={styles.resultTitle}>Scam Risk Assessment</Text>
              <Text style={styles.resultSubtitle}>Analyzed by Deterministic Security Engine</Text>
            </View>
            <View style={[styles.riskBadge, { backgroundColor: getRiskBg(currentScan.risk_level) }]}>
              <Text style={[styles.riskBadgeText, { color: getRiskColor(currentScan.risk_level) }]}>
                {currentScan.risk_level}
              </Text>
            </View>
          </View>
          
          {currentScan.input_type === 'image' && currentScan.extracted_text && (
             <View style={[styles.sectionBox, { backgroundColor: '#f3f4f6' }]}>
                <Text style={styles.sectionHeading}>📄 Extracted Text (OCR)</Text>
                <Text style={{ fontSize: 13, color: '#4b5563', fontStyle: 'italic' }}>
                  {currentScan.extracted_text}
                </Text>
                {currentScan.extracted_text.includes("No readable text") && (
                  <Text style={{ color: '#ea580c', fontSize: 12, marginTop: 4 }}>
                    ⚠️ Some text could not be read from this screenshot. Please verify the extracted message.
                  </Text>
                )}
             </View>
          )}

          {/* Risk Gauge */}
          <View style={styles.scoreRow}>
            <View style={styles.scoreBox}>
              <Text style={[styles.scoreNumber, { color: getRiskColor(currentScan.risk_level) }]}>
                {currentScan.risk_score}
              </Text>
              <Text style={styles.scoreDenom}>/ 100</Text>
            </View>
            <View style={styles.summaryBox}>
              <Text style={styles.summaryText}>{currentScan.summary}</Text>
            </View>
          </View>

          {/* Why This Was Flagged */}
          {currentScan.indicators && currentScan.indicators.length > 0 && (
            <View style={styles.sectionBox}>
              <Text style={styles.sectionHeading}>⚠️ Why This Was Flagged ({currentScan.indicators.length} signals)</Text>
              {currentScan.indicators.map((ind: { indicator_type: string; matched_text: string; points: number }, idx: number) => (
                <View key={idx} style={styles.indicatorRow}>
                  <Text style={styles.indicatorDot}>•</Text>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.indicatorType}>
                      {ind.indicator_type.replace(/_/g, " ")}: <Text style={styles.matchedText}>"{ind.matched_text}"</Text>
                    </Text>
                  </View>
                  <Text style={styles.pointsBadge}>+{ind.points} pts</Text>
                </View>
              ))}
            </View>
          )}

          {/* RAG Retrieved Evidence */}
          {currentScan.retrieved_evidence && currentScan.retrieved_evidence.length > 0 && (
            <View style={styles.sectionBox}>
              <Text style={styles.sectionHeading}>🔍 Related Scam Patterns</Text>
              {currentScan.retrieved_evidence.map((evidence, idx: number) => (
                <View key={idx} style={styles.indicatorRow}>
                  <Text style={styles.indicatorDot}>{evidence.is_scam ? "⚠️" : "✅"}</Text>
                  <View style={{ flex: 1 }}>
                    <Text style={[styles.indicatorType, { color: evidence.is_scam ? '#ea580c' : '#16a34a' }]}>
                      {evidence.category}: {evidence.title}
                    </Text>
                  </View>
                </View>
              ))}
            </View>
          )}

          {/* Recommended Actions */}
          <View style={styles.sectionBox}>
            <Text style={styles.sectionHeading}>🛡️ Recommended Safety Actions</Text>
            {currentScan.recommended_actions.map((action: string, idx: number) => (

              <View key={idx} style={styles.actionRow}>
                <Text style={styles.actionCheck}>✓</Text>
                <Text style={styles.actionText}>{action}</Text>
              </View>
            ))}
          </View>

          {/* Ask Saarthi Button */}
          <TouchableOpacity style={styles.saarthiButton} onPress={() => askSaarthiAboutScan(currentScan)}>
            <Text style={styles.saarthiButtonText}>💬 Ask AI Saarthi About This Scan</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* RECENT SCANS HEADER (Part of ListHeaderComponent) */}
      <View style={[styles.card, { paddingBottom: 8, marginBottom: 0, borderBottomWidth: 0, borderBottomLeftRadius: 0, borderBottomRightRadius: 0 }]}>
        <Text style={styles.cardTitle}>Recent Scan History</Text>
        {loadingHistory && <ActivityIndicator size="small" color={colors.purple} style={{ marginVertical: 16 }} />}
        {!loadingHistory && history.length === 0 && (
          <Text style={styles.emptyHistory}>No previous scan analyses found. Analyze a message above to get started.</Text>
        )}
      </View>
    </>
  );

  const listFooter = (
    <View style={[styles.card, { paddingTop: 0, marginTop: 0, borderTopWidth: 0, borderTopLeftRadius: 0, borderTopRightRadius: 0 }]} />
  );

  return (
    <Screen style={styles.container}>
      <FlatList
        data={history}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderHistoryItem}
        ListHeaderComponent={listHeader}
        ListFooterComponent={listFooter}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        initialNumToRender={10}
        maxToRenderPerBatch={10}
        windowSize={5}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f8fafc",
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 40,
  },
  header: {
    alignItems: "center",
    marginBottom: 20,
    marginTop: 8,
  },
  headerIcon: {
    fontSize: 48,
    marginBottom: 8,
  },
  headerTitle: {
    fontSize: 26,
    fontWeight: "800",
    color: colors.ink,
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 14,
    color: colors.muted,
    textAlign: "center",
  },
  card: {
    backgroundColor: "#ffffff",
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: colors.ink,
    marginBottom: 12,
  },
  textInput: {
    backgroundColor: "#f1f5f9",
    borderRadius: 12,
    padding: 12,
    fontSize: 14,
    color: colors.ink,
    textAlignVertical: "top",
    minHeight: 90,
    borderWidth: 1,
    borderColor: "#cbd5e1",
    marginBottom: 12,
  },
  sampleLabel: {
    fontSize: 12,
    fontWeight: "600",
    color: colors.muted,
    marginBottom: 6,
  },
  sampleContainer: {
    flexDirection: "row",
    gap: 8,
    marginBottom: 16,
  },
  sampleChip: {
    backgroundColor: "#e2e8f0",
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
  },
  sampleText: {
    fontSize: 12,
    fontWeight: "600",
    color: colors.ink,
  },
  analyzeButton: {
    backgroundColor: colors.purple,
  },
  resultHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 16,
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: "800",
    color: colors.ink,
  },
  resultSubtitle: {
    fontSize: 12,
    color: colors.muted,
  },
  riskBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  riskBadgeText: {
    fontWeight: "800",
    fontSize: 13,
  },
  scoreRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 16,
    backgroundColor: "#f8fafc",
    padding: 12,
    borderRadius: 12,
    marginBottom: 16,
  },
  scoreBox: {
    alignItems: "baseline",
    flexDirection: "row",
  },
  scoreNumber: {
    fontSize: 36,
    fontWeight: "900",
  },
  scoreDenom: {
    fontSize: 14,
    fontWeight: "700",
    color: colors.muted,
    marginLeft: 2,
  },
  summaryBox: {
    flex: 1,
  },
  summaryText: {
    fontSize: 13,
    color: colors.ink,
    fontWeight: "600",
    lineHeight: 18,
  },
  sectionBox: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: "#e2e8f0",
  },
  sectionHeading: {
    fontSize: 15,
    fontWeight: "700",
    color: colors.ink,
    marginBottom: 8,
  },
  indicatorRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    marginBottom: 6,
  },
  indicatorDot: {
    fontSize: 14,
    color: "#dc2626",
    fontWeight: "bold",
  },
  indicatorType: {
    fontSize: 13,
    fontWeight: "700",
    color: colors.ink,
  },
  matchedText: {
    fontWeight: "400",
    fontStyle: "italic",
    color: colors.muted,
  },
  pointsBadge: {
    fontSize: 11,
    fontWeight: "700",
    color: "#dc2626",
    backgroundColor: "#fee2e2",
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 6,
  },
  actionRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 8,
    marginBottom: 6,
  },
  actionCheck: {
    fontSize: 14,
    color: "#16a34a",
    fontWeight: "bold",
  },
  actionText: {
    fontSize: 13,
    color: colors.ink,
    flex: 1,
    lineHeight: 18,
  },
  saarthiButton: {
    marginTop: 16,
    backgroundColor: colors.lavender,
    borderWidth: 1,
    borderColor: colors.purple + "44",
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: "center",
  },
  saarthiButtonText: {
    color: colors.purple,
    fontWeight: "800",
    fontSize: 14,
  },
  emptyHistory: {
    fontSize: 13,
    color: colors.muted,
    fontStyle: "italic",
    textAlign: "center",
    paddingVertical: 12,
  },
  historyItem: {
    backgroundColor: "#f8fafc",
    padding: 12,
    borderRadius: 10,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  historyTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 4,
  },
  miniRiskBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
  },
  miniRiskText: {
    fontSize: 11,
    fontWeight: "800",
  },
  historyDate: {
    fontSize: 11,
    color: colors.muted,
  },
  historyText: {
    fontSize: 13,
    color: colors.ink,
  },
});
