import pathlib

code = """import React, { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
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
import type { MarketAsset, MarketOverview } from "@/types/api";

function formatTimestamp(isoStr: string): string {
  try {
    const d = new Date(isoStr);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return isoStr;
  }
}

export default function MarketIntelligenceScreen() {
  const { token } = useAuth();
  const { t } = useLanguage();

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [overview, setOverview] = useState<MarketOverview | null>(null);
  const [explainLevel, setExplainLevel] = useState<"SIMPLE" | "BALANCED" | "DETAILED">("SIMPLE");

  useEffect(() => {
    loadData();
    // Background auto-refresh every 60 seconds minimum
    const interval = setInterval(() => {
      loadData(false, false);
    }, 60000);
    return () => clearInterval(interval);
  }, [token]);

  const loadData = async (forceRefresh = false, showLoader = true) => {
    if (showLoader) setLoading(true);
    try {
      const res = await api.getMarketOverview(token || undefined, forceRefresh);
      setOverview(res);
      if (res.explanation_level) {
        setExplainLevel(res.explanation_level);
      }
    } catch (err) {
      console.warn("Failed to load market overview", err);
    } finally {
      if (showLoader) setLoading(false);
      setRefreshing(false);
    }
  };

  const handlePullRefresh = () => {
    setRefreshing(true);
    loadData(true, false);
  };

  const handleAskSaarthi = (assetSymbol?: string) => {
    const query = assetSymbol
      ? `Explain today's movement for ${assetSymbol} and what a beginner should understand about it.`
      : "Explain today's Indian market trends and market pulse to me simply.";
    const pathName = "/(" + "tabs)/saarthi";
    router.push({
      pathname: pathName as any,
      params: { initialQuery: query },
    });
  };

  const getDirectionColor = (dir: string) => {
    if (dir === "UP") return "#16a34a";
    if (dir === "DOWN") return "#dc2626";
    return colors.muted;
  };

  const getDirectionIcon = (dir: string) => {
    if (dir === "UP") return "▲";
    if (dir === "DOWN") return "▼";
    return "➖";
  };

  const getPulseBadgeStyle = (pulse: string) => {
    switch (pulse) {
      case "POSITIVE": return { bg: "#dcfce7", text: "#15803d" };
      case "NEGATIVE": return { bg: "#fee2e2", text: "#b91c1c" };
      case "CALM": return { bg: "#f3f4f6", text: "#4b5563" };
      default: return { bg: "#fef3c7", text: "#b45309" };
    }
  };

  const getFreshnessStyle = (freshness: string) => {
    switch (freshness) {
      case "LIVE": return { bg: "#dcfce7", text: "#15803d" };
      case "CACHED": return { bg: "#e0f2fe", text: "#0369a1" };
      case "STALE": return { bg: "#fef3c7", text: "#b45309" };
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
          <Text style={styles.title}>📈 {t("market.title")}</Text>
          <Text style={styles.subtitle}>{t("market.subtitle")}</Text>
        </View>

        {loading && !refreshing ? (
          <ActivityIndicator size="large" color={colors.purple} style={{ marginVertical: 40 }} />
        ) : overview ? (
          <>
            {/* MARKET PULSE BANNER */}
            <View style={styles.pulseCard}>
              <View style={styles.pulseHeaderRow}>
                <View style={[styles.pulseBadge, { backgroundColor: getPulseBadgeStyle(overview.market_pulse).bg }]}>
                  <Text style={[styles.pulseBadgeText, { color: getPulseBadgeStyle(overview.market_pulse).text }]}>
                    {t(`market.pulse_${overview.market_pulse.toLowerCase()}`)}
                  </Text>
                </View>

                <View style={[styles.freshnessBadge, { backgroundColor: getFreshnessStyle(overview.freshness).bg }]}>
                  <Text style={[styles.freshnessBadgeText, { color: getFreshnessStyle(overview.freshness).text }]}>
                    ● {t(`market.freshness_${overview.freshness.toLowerCase()}`)}
                  </Text>
                </View>
              </View>

              <Text style={styles.pulseSummary}>{overview.pulse_summary}</Text>

              <View style={styles.metaRow}>
                <Text style={styles.metaText}>
                  {t("market.last_updated")}: {formatTimestamp(overview.fetched_at)}
                </Text>
                <Text style={styles.metaText}>Source: {overview.source}</Text>
              </View>
            </View>

            {/* TRACKED MARKETS & ASSETS GRID */}
            <View style={styles.section}>
              <View style={styles.sectionHeaderRow}>
                <Text style={styles.sectionTitle}>📊 {t("market.tracked_assets")}</Text>
                <TouchableOpacity
                  onPress={() => loadData(true, true)}
                  accessibilityRole="button"
                  accessibilityLabel="Refresh market data"
                >
                  <Text style={styles.refreshBtnText}>🔄 Refresh</Text>
                </TouchableOpacity>
              </View>

              <View style={styles.assetGrid}>
                {overview.tracked_assets.map((asset: MarketAsset) => {
                  const dirColor = getDirectionColor(asset.direction);
                  const dirIcon = getDirectionIcon(asset.direction);
                  return (
                    <TouchableOpacity
                      key={asset.symbol}
                      style={styles.assetCard}
                      onPress={() => handleAskSaarthi(asset.symbol)}
                      accessibilityRole="button"
                      accessibilityLabel={`${asset.display_name}, ${asset.current_price} ${asset.currency}, ${asset.percentage_change}% ${asset.direction}`}
                    >
                      <View style={styles.assetTopRow}>
                        <Text style={styles.assetSymbol}>{asset.display_name}</Text>
                        <View style={[styles.statusBadge, asset.market_status === "OPEN" ? styles.statusOpen : styles.statusClosed]}>
                          <Text style={styles.statusText}>{asset.market_status}</Text>
                        </View>
                      </View>

                      <Text style={styles.assetPrice}>
                        ₹{asset.current_price.toLocaleString("en-IN")}
                      </Text>

                      <View style={styles.assetChangeRow}>
                        <Text style={[styles.changeText, { color: dirColor }]}>
                          {dirIcon} {asset.absolute_change > 0 ? "+" : ""}{asset.absolute_change} ({asset.percentage_change > 0 ? "+" : ""}{asset.percentage_change}%)
                        </Text>
                      </View>
                    </TouchableOpacity>
                  );
                })}
              </View>
            </View>

            {/* EXPLANATION LEVEL TOGGLE */}
            <View style={styles.levelCard}>
              <Text style={styles.levelLabel}>💡 {t("market.explanation_level")}:</Text>
              <View style={styles.levelRow}>
                {(["SIMPLE", "BALANCED", "DETAILED"] as const).map((lvl) => (
                  <Pressable
                    key={lvl}
                    style={[styles.levelBtn, explainLevel === lvl && styles.levelBtnActive]}
                    onPress={() => setExplainLevel(lvl)}
                    accessibilityRole="button"
                    accessibilityState={{ selected: explainLevel === lvl }}
                  >
                    <Text style={[styles.levelBtnText, explainLevel === lvl && styles.levelBtnTextActive]}>
                      {lvl.charAt(0) + lvl.slice(1).toLowerCase()}
                    </Text>
                  </Pressable>
                ))}
              </View>
            </View>

            {/* TODAY'S MARKET INSIGHTS */}
            {overview.insights.length > 0 && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>🧠 {t("market.insights_title")}</Text>

                {overview.insights.map((insight, idx) => (
                  <View key={idx} style={styles.insightCard}>
                    <Text style={styles.insightTitle}>• {insight.title}</Text>
                    <Text style={styles.insightObs}>{insight.observation}</Text>
                    <View style={styles.noteBox}>
                      <Text style={styles.noteTitle}>🎓 Educational Note:</Text>
                      <Text style={styles.noteBody}>{insight.educational_note}</Text>
                    </View>
                  </View>
                ))}
              </View>
            )}

            {/* ASK AI SAARTHI PRE-FILL BUTTON */}
            <TouchableOpacity
              style={styles.askSaarthiBtn}
              onPress={() => handleAskSaarthi()}
              accessibilityRole="button"
              accessibilityLabel={t("market.ask_saarthi")}
            >
              <Text style={styles.askSaarthiText}>🤖 {t("market.ask_saarthi")}</Text>
            </TouchableOpacity>

            {/* FINANCIAL SAFETY DISCLAIMER */}
            <View style={styles.disclaimerBox}>
              <Text style={styles.disclaimerTitle}>⚠️ Financial Safety & Data Notice</Text>
              <Text style={styles.disclaimerBody}>{overview.disclaimer}</Text>
            </View>
          </>
        ) : (
          <View style={styles.errorBox}>
            <Text style={styles.errorText}>Live market data is temporarily unavailable.</Text>
            <TouchableOpacity style={styles.retryBtn} onPress={() => loadData(true, true)}>
              <Text style={styles.retryText}>Retry Loading</Text>
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

  pulseCard: { backgroundColor: "#ffffff", borderRadius: 16, padding: 16, borderWidth: 1, borderColor: colors.border, marginBottom: 20 },
  pulseHeaderRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 10 },
  pulseBadge: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 16 },
  pulseBadgeText: { fontSize: 13, fontWeight: "800" },
  freshnessBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
  freshnessBadgeText: { fontSize: 11, fontWeight: "800" },
  pulseSummary: { fontSize: 15, fontWeight: "700", color: colors.ink, lineHeight: 22, marginBottom: 12 },
  metaRow: { flexDirection: "row", justifyContent: "space-between", borderTopWidth: 1, borderTopColor: "#f1f5f9", paddingTop: 8 },
  metaText: { fontSize: 11, color: colors.muted, fontWeight: "600" },

  section: { marginBottom: 20 },
  sectionHeaderRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 12 },
  sectionTitle: { fontSize: 18, fontWeight: "800", color: colors.ink },
  refreshBtnText: { fontSize: 13, color: colors.purple, fontWeight: "700" },

  assetGrid: { flexDirection: "row", flexWrap: "wrap", gap: 10 },
  assetCard: { width: "48%", backgroundColor: "#ffffff", borderRadius: 14, padding: 14, borderWidth: 1, borderColor: colors.border },
  assetTopRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 6 },
  assetSymbol: { fontSize: 13, fontWeight: "800", color: colors.ink, flex: 1 },
  statusBadge: { paddingHorizontal: 6, paddingVertical: 2, borderRadius: 8 },
  statusOpen: { backgroundColor: "#dcfce7" },
  statusClosed: { backgroundColor: "#f3f4f6" },
  statusText: { fontSize: 9, fontWeight: "800", color: colors.ink },
  assetPrice: { fontSize: 17, fontWeight: "800", color: colors.ink, marginVertical: 4 },
  assetChangeRow: { marginTop: 2 },
  changeText: { fontSize: 12, fontWeight: "700" },

  levelCard: { backgroundColor: "#f8fafc", borderRadius: 14, padding: 12, borderWidth: 1, borderColor: "#e2e8f0", marginBottom: 20 },
  levelLabel: { fontSize: 13, fontWeight: "800", color: colors.ink, marginBottom: 8 },
  levelRow: { flexDirection: "row", gap: 8 },
  levelBtn: { flex: 1, paddingVertical: 8, borderRadius: 10, borderWidth: 1, borderColor: colors.border, alignItems: "center", backgroundColor: "#fff" },
  levelBtnActive: { backgroundColor: colors.purple, borderColor: colors.purple },
  levelBtnText: { fontSize: 12, fontWeight: "700", color: colors.ink },
  levelBtnTextActive: { color: "#fff" },

  insightCard: { backgroundColor: "#ffffff", borderRadius: 14, padding: 14, borderWidth: 1, borderColor: colors.border, marginBottom: 12 },
  insightTitle: { fontSize: 15, fontWeight: "800", color: colors.ink, marginBottom: 4 },
  insightObs: { fontSize: 14, color: colors.ink, lineHeight: 20, marginBottom: 8 },
  noteBox: { backgroundColor: "#f8fafc", borderRadius: 10, padding: 10, borderWidth: 1, borderColor: "#e2e8f0" },
  noteTitle: { fontSize: 12, fontWeight: "800", color: colors.purple, marginBottom: 2 },
  noteBody: { fontSize: 13, color: colors.muted, lineHeight: 18 },

  askSaarthiBtn: { backgroundColor: colors.lavender, paddingVertical: 14, borderRadius: 14, alignItems: "center", marginVertical: 10 },
  askSaarthiText: { color: colors.purple, fontWeight: "800", fontSize: 15 },

  disclaimerBox: { backgroundColor: "#fffbe6", borderRadius: 12, padding: 12, borderWidth: 1, borderColor: "#ffe58f", marginTop: 10 },
  disclaimerTitle: { fontSize: 12, fontWeight: "800", color: "#855900", marginBottom: 4 },
  disclaimerBody: { fontSize: 11, color: "#855900", lineHeight: 16 },

  errorBox: { marginVertical: 40, alignItems: "center" },
  errorText: { fontSize: 15, color: colors.muted, marginBottom: 16 },
  retryBtn: { backgroundColor: colors.purple, paddingHorizontal: 20, paddingVertical: 10, borderRadius: 10 },
  retryText: { color: "#fff", fontWeight: "700" },
});
"""

pathlib.Path("D:/projects/Dhan_Saarthi/Saarthi/frontend/app/domain/market-intelligence.tsx").write_text(code, encoding="utf-8")
print("Successfully generated market-intelligence.tsx")
