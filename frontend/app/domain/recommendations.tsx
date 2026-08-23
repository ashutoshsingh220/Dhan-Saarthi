import React, { useEffect, useState } from "react";
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { router } from "expo-router";
import { Screen } from "@/components/Screen";
import { colors } from "@/constants/theme";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/i18n/LanguageContext";
import { api } from "@/services/api";
import type { PersonalizedRecommendation } from "@/types/api";

export default function RecommendationsScreen() {
  const { token } = useAuth();
  const { t } = useLanguage();

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [recommendation, setRecommendation] = useState<PersonalizedRecommendation | null>(null);

  useEffect(() => {
    loadData();
  }, [token]);

  const loadData = async (showLoader = true) => {
    if (!token) {
      setLoading(false);
      return;
    }
    if (showLoader) setLoading(true);
    try {
      const res = await api.getRecommendation(token);
      setRecommendation(res);
    } catch (err) {
      console.warn("Failed to load recommendation data", err);
    } finally {
      if (showLoader) setLoading(false);
      setRefreshing(false);
    }
  };

  const handlePullRefresh = () => {
    setRefreshing(true);
    if (token) {
      api.generateRecommendation(token)
        .then((res) => setRecommendation(res))
        .catch((err) => console.warn(err))
        .finally(() => setRefreshing(false));
    }
  };

  const handleAskSaarthi = () => {
    const query = "Explain my top financial priority and monthly surplus allocation guidance to me in simple terms.";
    router.push({
      pathname: "/(tabs)/saarthi" as any,
      params: { initialPrompt: query },
    });
  };


  const getCompletenessStyle = (status: string) => {
    switch (status) {
      case "COMPLETE": return { bg: "#dcfce7", text: "#15803d" };
      case "PARTIAL": return { bg: "#fef3c7", text: "#b45309" };
      default: return { bg: "#fee2e2", text: "#b91c1c" };
    }
  };

  const getFeasibilityStyle = (status: string) => {
    switch (status) {
      case "FEASIBLE": return { bg: "#dcfce7", text: "#15803d" };
      case "TIGHT": return { bg: "#fef3c7", text: "#b45309" };
      case "AT_RISK": return { bg: "#fee2e2", text: "#b91c1c" };
      default: return { bg: "#f3f4f6", text: "#4b5563" };
    }
  };

  return (
    <Screen
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={handlePullRefresh} tintColor={colors.purple} />
      }
    >
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={{ paddingBottom: 40 }}>
        {/* HEADER */}
        <View style={styles.header}>
          <Text style={styles.title}>🧭 {t("recommendation.title")}</Text>
          <Text style={styles.subtitle}>{t("recommendation.subtitle")}</Text>
        </View>

        {loading && !refreshing ? (
          <ActivityIndicator size="large" color={colors.purple} style={{ marginVertical: 40 }} />
        ) : recommendation ? (
          <>
            {/* DATA COMPLETENESS BADGE */}
            <View style={styles.completenessBox}>
              <View style={styles.completenessHeader}>
                <Text style={styles.completenessLabel}>Data Completeness Status:</Text>
                <View style={[styles.badge, { backgroundColor: getCompletenessStyle(recommendation.data_completeness).bg }]}>
                  <Text style={[styles.badgeText, { color: getCompletenessStyle(recommendation.data_completeness).text }]}>
                    ● {recommendation.data_completeness}
                  </Text>
                </View>
              </View>
              <Text style={styles.completenessNote}>{recommendation.data_completeness_note}</Text>
            </View>

            {/* TOP PRIORITY CARD */}
            <View style={styles.topPriorityCard}>
              <Text style={styles.priorityKicker}>{t("recommendation.top_priority")}</Text>
              <Text style={styles.priorityTitle}>{recommendation.top_priority.title}</Text>
              
              <View style={styles.priorityBadgesRow}>
                <View style={styles.catBadge}>
                  <Text style={styles.catBadgeText}>{recommendation.top_priority.category}</Text>
                </View>
                <View style={[styles.prioLevelBadge, { backgroundColor: recommendation.top_priority.priority_level === "HIGH" ? "#fee2e2" : "#fef3c7" }]}>
                  <Text style={[styles.prioLevelText, { color: recommendation.top_priority.priority_level === "HIGH" ? "#b91c1c" : "#b45309" }]}>
                    {recommendation.top_priority.priority_level} PRIORITY
                  </Text>
                </View>
              </View>

              <Text style={styles.sectionSubhead}>{t("recommendation.why_matters")}:</Text>
              <Text style={styles.reasonText}>{recommendation.top_priority.reason}</Text>

              <Text style={styles.sectionSubhead}>Suggested Action:</Text>
              <Text style={styles.actionText}>{recommendation.top_priority.action_guidance}</Text>
            </View>

            {/* MONTHLY FINANCIAL CAPACITY */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>💰 {t("recommendation.monthly_capacity")}</Text>
              
              <View style={styles.capacityGrid}>
                <View style={styles.capacityItem}>
                  <Text style={styles.capacityLabel}>{t("recommendation.income")}</Text>
                  <Text style={styles.capacityValue}>₹{recommendation.monthly_capacity.income.toLocaleString("en-IN")}</Text>
                </View>
                <View style={styles.capacityItem}>
                  <Text style={styles.capacityLabel}>{t("recommendation.expenses")}</Text>
                  <Text style={styles.capacityValue}>₹{recommendation.monthly_capacity.expenses.toLocaleString("en-IN")}</Text>
                </View>
                <View style={styles.capacityItem}>
                  <Text style={styles.capacityLabel}>{t("recommendation.surplus")}</Text>
                  <Text style={[styles.capacityValue, { color: colors.purple }]}>₹{recommendation.monthly_capacity.surplus.toLocaleString("en-IN")}</Text>
                </View>
                <View style={styles.capacityItem}>
                  <Text style={styles.capacityLabel}>{t("recommendation.flexibility")}</Text>
                  <Text style={[styles.capacityValue, { color: "#16a34a" }]}>₹{recommendation.monthly_capacity.unallocated_flexibility.toLocaleString("en-IN")}</Text>
                </View>
              </View>
            </View>

            {/* SUGGESTED MONTHLY GUIDANCE RANGES */}
            {recommendation.allocation_guidance.length > 0 && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>📊 {t("recommendation.guidance_ranges")}</Text>
                <Text style={styles.helperText}>Guidance ranges preserve flexibility and avoid rigid 100% allocation.</Text>

                {recommendation.allocation_guidance.map((item, idx) => (
                  <View key={idx} style={styles.guidanceCard}>
                    <View style={styles.guidanceHeader}>
                      <Text style={styles.guidanceCat}>{item.category}</Text>
                      <Text style={styles.guidanceRange}>
                        ₹{item.suggested_range_min.toLocaleString("en-IN")} – ₹{item.suggested_range_max.toLocaleString("en-IN")} / mo
                      </Text>
                    </View>
                    <Text style={styles.guidanceReason}>{item.reason}</Text>
                  </View>
                ))}
              </View>
            )}

            {/* GOAL CONSIDERATIONS */}
            {recommendation.goal_considerations.length > 0 && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>🎯 {t("recommendation.goals")}</Text>

                {recommendation.goal_considerations.map((g) => (
                  <View key={g.goal_id} style={styles.goalCard}>
                    <View style={styles.goalHeaderRow}>
                      <Text style={styles.goalTitle}>{g.goal_name}</Text>
                      <View style={[styles.badge, { backgroundColor: getFeasibilityStyle(g.feasibility_status).bg }]}>
                        <Text style={[styles.badgeText, { color: getFeasibilityStyle(g.feasibility_status).text }]}>
                          {g.feasibility_status}
                        </Text>
                      </View>
                    </View>
                    <Text style={styles.goalRequired}>Required Monthly Contribution: ₹{g.monthly_required.toLocaleString("en-IN")}</Text>
                    <Text style={styles.goalNote}>{g.guidance_note}</Text>
                  </View>
                ))}
              </View>
            )}

            {/* MARKET CONTEXT AWARENESS */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>📈 {t("recommendation.market_context")}</Text>
              
              <View style={styles.marketBox}>
                <View style={styles.marketMetaRow}>
                  <Text style={styles.marketPulseText}>Market Pulse: {recommendation.market_context_summary.pulse}</Text>
                  <Text style={styles.marketFreshnessText}>Freshness: {recommendation.market_context_summary.freshness}</Text>
                </View>
                <Text style={styles.marketWarning}>{recommendation.market_context_summary.warning_note}</Text>
              </View>
            </View>

            {/* ASK AI SAARTHI BUTTON */}
            <TouchableOpacity
              style={styles.askBtn}
              onPress={handleAskSaarthi}
              accessibilityRole="button"
              accessibilityLabel={t("recommendation.ask_saarthi")}
            >
              <Text style={styles.askBtnText}>🤖 {t("recommendation.ask_saarthi")}</Text>
            </TouchableOpacity>

            {/* DISCLAIMER */}
            <View style={styles.disclaimerBox}>
              <Text style={styles.disclaimerTitle}>⚠️ Financial Safety Notice</Text>
              <Text style={styles.disclaimerBody}>{recommendation.disclaimer}</Text>
            </View>
          </>
        ) : (
          <View style={styles.errorBox}>
            <Text style={styles.errorText}>Unable to load recommendations.</Text>
            <TouchableOpacity style={styles.retryBtn} onPress={() => loadData(true)}>
              <Text style={styles.retryText}>Retry</Text>
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  header: { marginTop: 12, marginBottom: 16 },
  title: { fontSize: 26, fontWeight: "800", color: colors.ink },
  subtitle: { fontSize: 14, color: colors.muted, marginTop: 4 },

  completenessBox: { backgroundColor: "#f8fafc", borderRadius: 14, padding: 12, borderWidth: 1, borderColor: "#e2e8f0", marginBottom: 16 },
  completenessHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 4 },
  completenessLabel: { fontSize: 13, fontWeight: "700", color: colors.ink },
  badge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 10 },
  badgeText: { fontSize: 11, fontWeight: "800" },
  completenessNote: { fontSize: 12, color: colors.muted, lineHeight: 16 },

  topPriorityCard: { backgroundColor: "#ffffff", borderRadius: 16, padding: 16, borderWidth: 2, borderColor: colors.purple, marginBottom: 20 },
  priorityKicker: { fontSize: 11, fontWeight: "800", color: colors.purple, letterSpacing: 0.5, marginBottom: 4 },
  priorityTitle: { fontSize: 20, fontWeight: "800", color: colors.ink, marginBottom: 8 },
  priorityBadgesRow: { flexDirection: "row", gap: 8, marginBottom: 12 },
  catBadge: { backgroundColor: colors.lavender, paddingHorizontal: 8, paddingVertical: 4, borderRadius: 8 },
  catBadgeText: { fontSize: 11, fontWeight: "700", color: colors.purple },
  prioLevelBadge: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 8 },
  prioLevelText: { fontSize: 11, fontWeight: "800" },
  sectionSubhead: { fontSize: 13, fontWeight: "800", color: colors.ink, marginTop: 6, marginBottom: 2 },
  reasonText: { fontSize: 14, color: colors.ink, lineHeight: 20 },
  actionText: { fontSize: 14, color: colors.muted, lineHeight: 20 },

  section: { marginBottom: 20 },
  sectionTitle: { fontSize: 18, fontWeight: "800", color: colors.ink, marginBottom: 8 },
  helperText: { fontSize: 12, color: colors.muted, marginBottom: 10 },

  capacityGrid: { flexDirection: "row", flexWrap: "wrap", gap: 10 },
  capacityItem: { width: "48%", backgroundColor: "#ffffff", borderRadius: 12, padding: 12, borderWidth: 1, borderColor: colors.border },
  capacityLabel: { fontSize: 12, color: colors.muted, fontWeight: "600" },
  capacityValue: { fontSize: 16, fontWeight: "800", color: colors.ink, marginTop: 4 },

  guidanceCard: { backgroundColor: "#ffffff", borderRadius: 12, padding: 14, borderWidth: 1, borderColor: colors.border, marginBottom: 10 },
  guidanceHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 4 },
  guidanceCat: { fontSize: 14, fontWeight: "800", color: colors.ink },
  guidanceRange: { fontSize: 13, fontWeight: "800", color: colors.purple },
  guidanceReason: { fontSize: 13, color: colors.muted, lineHeight: 18 },

  goalCard: { backgroundColor: "#ffffff", borderRadius: 12, padding: 14, borderWidth: 1, borderColor: colors.border, marginBottom: 10 },
  goalHeaderRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 4 },
  goalTitle: { fontSize: 15, fontWeight: "800", color: colors.ink },
  goalRequired: { fontSize: 13, fontWeight: "700", color: colors.purple, marginBottom: 4 },
  goalNote: { fontSize: 13, color: colors.muted, lineHeight: 18 },

  marketBox: { backgroundColor: "#f8fafc", borderRadius: 12, padding: 14, borderWidth: 1, borderColor: "#e2e8f0" },
  marketMetaRow: { flexDirection: "row", justifyContent: "space-between", marginBottom: 6 },
  marketPulseText: { fontSize: 13, fontWeight: "800", color: colors.ink },
  marketFreshnessText: { fontSize: 12, fontWeight: "700", color: colors.muted },
  marketWarning: { fontSize: 13, color: colors.ink, lineHeight: 18 },

  askBtn: { backgroundColor: colors.lavender, paddingVertical: 14, borderRadius: 14, alignItems: "center", marginVertical: 10 },
  askBtnText: { color: colors.purple, fontWeight: "800", fontSize: 15 },

  disclaimerBox: { backgroundColor: "#fffbe6", borderRadius: 12, padding: 12, borderWidth: 1, borderColor: "#ffe58f", marginTop: 10 },
  disclaimerTitle: { fontSize: 12, fontWeight: "800", color: "#855900", marginBottom: 4 },
  disclaimerBody: { fontSize: 11, color: "#855900", lineHeight: 16 },

  errorBox: { marginVertical: 40, alignItems: "center" },
  errorText: { fontSize: 15, color: colors.muted, marginBottom: 16 },
  retryBtn: { backgroundColor: colors.purple, paddingHorizontal: 20, paddingVertical: 10, borderRadius: 10 },
  retryText: { color: "#fff", fontWeight: "700" },
});
