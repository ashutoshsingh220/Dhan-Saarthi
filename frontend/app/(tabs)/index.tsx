import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  RefreshControl,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { router } from "expo-router";
import { Button } from "@/components/Form";
import { Screen } from "@/components/Screen";
import { colors } from "@/constants/theme";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/i18n/LanguageContext";
import { AccessibilityModeBanner } from "@/components/accessibility/AccessibilityModeBanner";
import { AccessibleQuickActions } from "@/components/accessibility/AccessibleQuickActions";
import { BrandLogo } from "@/components/branding/BrandLogo";
import { DomainIconBadge, DomainId } from "@/components/branding/DomainIconBadge";
import { api } from "@/services/api";

import { speechSynthesis } from "@/services/voice/speechSynthesis";


function getGreeting(name?: string, lang: "en" | "hi" = "en"): string {
  const hour = new Date().getHours();
  const firstName = name ? name.split(" ")[0] : "";

  if (lang === "hi") {
    let timeGreeting = "शुभ प्रभात (Good Morning)";
    if (hour >= 12 && hour < 17) timeGreeting = "शुभ दोपहर (Good Afternoon)";
    if (hour >= 17) timeGreeting = "शुभ संध्या (Good Evening)";
    return firstName ? `${timeGreeting}, ${firstName}` : timeGreeting;
  }

  let timeGreeting = "Good Morning";
  if (hour >= 12 && hour < 17) timeGreeting = "Good Afternoon";
  if (hour >= 17) timeGreeting = "Good Evening";
  return firstName ? `${timeGreeting}, ${firstName}` : timeGreeting;
}

function getScoreCategory(score: number): { category: string; explanation: string; color: string } {
  if (score >= 80) {
    return {
      category: "Strong Position",
      explanation: "You have an excellent financial foundation. Keep optimizing investments and goal progress.",
      color: "#2E7D32",
    };
  }
  if (score >= 60) {
    return {
      category: "Good Progress",
      explanation: "You have a stable foundation. Improving savings consistency could strengthen your position further.",
      color: colors.purple,
    };
  }
  if (score >= 40) {
    return {
      category: "Building Foundation",
      explanation: "Your financial profile shows positive steps. Focus on building an emergency buffer.",
      color: "#ED6C02",
    };
  }
  return {
    category: "Needs Attention",
    explanation: "High expense ratios or low buffers detected. Prioritize reducing debt and building savings.",
    color: "#D32F2F",
  };
}

function getDeterministicInsight(income: number, expenses: number, savings: number, goal: string): string {
  const surplus = income - expenses;
  const bufferMonths = expenses > 0 ? (savings / expenses).toFixed(1) : "0";

  if (surplus <= 0) {
    return "Your expenses exceed your monthly income. Focus immediately on eliminating non-essential spending.";
  }
  if (parseFloat(bufferMonths) < 3.0) {
    return `Your liquid savings cover ${bufferMonths} months of expenses. We recommend directing part of your ₹${surplus.toLocaleString("en-IN")} surplus to reach a 3-month emergency buffer.`;
  }
  return `Your Financial Twin recommends maintaining a consistent savings routine of ₹${surplus.toLocaleString("en-IN")}/month to reach "${goal}".`;
}

export default function HomeDashboard() {
  const { token, user, profile, twin, loading, refreshState } = useAuth();
  const { language, t } = useLanguage();
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [brief, setBrief] = useState<any>(null);

  const fetchOrchestrationData = async () => {
    if (!token) return;
    try {
      const briefData = await api.getTodaysBrief(token);
      setBrief(briefData);
    } catch (e) {
      console.warn("Orchestration brief fetch warning:", e);
    }
  };

  useEffect(() => {
    fetchOrchestrationData();
  }, [token]);

  const onRefresh = async () => {
    setRefreshing(true);
    setError(null);
    try {
      await Promise.all([refreshState(), fetchOrchestrationData()]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to refresh dashboard data");
    } finally {
      setRefreshing(false);
    }
  };

  if (loading && !refreshing) {
    return (
      <Screen style={styles.center}>
        <ActivityIndicator size="large" color={colors.purple} />
        <Text style={styles.loadingText}>Fetching your Financial Twin...</Text>
      </Screen>
    );
  }

  if (error || !twin || !user) {
    return (
      <Screen style={styles.center}>
        <Text style={styles.errorTitle}>Unable to load Dashboard</Text>
        <Text style={styles.errorMessage}>{error || "Your Financial Twin data is currently unavailable."}</Text>
        <Button title="Retry Loading" onPress={onRefresh} />
      </Screen>
    );
  }

  const scoreInfo = getScoreCategory(twin.financial_health_score);
  const income = profile ? Number(profile.monthly_income) : 0;
  const expenses = profile ? Number(profile.monthly_expenses) : 0;
  const savings = profile ? Number(profile.savings) : 0;
  const surplus = income - expenses;
  const goal = profile?.financial_goal || "Financial Growth";
  const risk = profile?.risk_preference || twin.risk_level || "Moderate";

  const insightText = getDeterministicInsight(income, expenses, savings, goal);

  const capabilityDomains = [
    {
      id: "saarthi",
      title: t("nav.saarthi"),
      desc: "Ask questions about your finances.",
      icon: "🤖",
      action: () => router.push("/(tabs)/saarthi" as any),
    },
    {
      id: "learn",
      title: t("nav.learn"),
      desc: "Learn financial concepts clearly.",
      icon: "📚",
      action: () => router.push("/(tabs)/learn" as any),
    },
    {
      id: "recommendations",
      title: t("recommendation.title"),
      desc: "Tailored monthly surplus & priority guidance.",
      icon: "🧭",
      action: () => router.push("/domain/recommendations" as any),
    },
    {
      id: "planning",
      title: t("planning.title"),
      desc: "Turn your goals into action.",
      icon: "🎯",
      action: () => router.push("/domain/planning" as any),
    },

    {
      id: "market",
      title: "Market Intelligence",
      desc: "Live Market Pulse, Nifty, Sensex & Gold.",
      icon: "📈",
      action: () => router.push("/domain/market-intelligence" as any),
    },
    {
      id: "schemes",
      title: t("schemes.title"),
      desc: "Farmer & Small Business Government Schemes.",
      icon: "🌾",
      action: () => router.push("/domain/schemes" as any),
    },
    {
      id: "scam",
      title: t("scam.title"),
      desc: "Analyze suspicious messages.",
      icon: "🛡️",
      action: () => router.push("/domain/scam-shield" as any),
    },
    {
      id: "twin",
      title: t("dashboard.twin_title"),
      desc: "Understand your evolving financial picture.",
      icon: "🧬",
      action: () => router.push("/twin-detail" as any),
    },
  ];

  return (

    <Screen refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.purple} />}>
      {/* A. PERSONALIZED HEADER */}
      <View style={styles.header}>
        <View style={{ marginBottom: 6 }}>
          <BrandLogo variant="compact" style={{ alignSelf: "flex-start" }} />
        </View>
        <Text style={styles.greeting}>{getGreeting(user.full_name, language)}</Text>
        <Text style={styles.statusLine}>
          {language === "hi" ? "आपकी वित्तीय स्थिति अधिक स्पष्ट हो रही है।" : "Your financial picture is becoming clearer."}
        </Text>
      </View>


      {/* ACCESSIBILITY BANNER & QUICK ACTIONS */}
      <AccessibilityModeBanner />
      <AccessibleQuickActions />

      {/* PROMPT 14 PART C: TOP FINANCIAL PRIORITY CARD */}
      {brief && brief.top_priority && (
        <View style={styles.priorityCard}>
          <View style={styles.priorityHeaderRow}>
            <Text style={styles.priorityKicker}>⚡ YOUR TOP FINANCIAL PRIORITY</Text>
            <View style={styles.priorityBadge}>
              <Text style={styles.priorityBadgeText}>{brief.top_priority.priority_level}</Text>
            </View>
          </View>
          <Text style={styles.priorityTitle}>{brief.top_priority.reason}</Text>
          <Text style={styles.priorityActionDesc}>{brief.top_priority.recommended_next_action}</Text>
          <View style={styles.priorityBtnRow}>
            <TouchableOpacity
              style={styles.priorityBtnPrimary}
              onPress={() => router.push((brief.top_priority.action_route || "/domain/recommendations") as any)}
            >
              <Text style={styles.priorityBtnPrimaryText}>Take Action ➡️</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.priorityBtnSecondary}
              onPress={() => router.push({ pathname: "/(tabs)/saarthi", params: { initialPrompt: brief.top_priority.reason } } as any)}
            >
              <Text style={styles.priorityBtnSecondaryText}>Ask Saarthi 🤖</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      {/* PROMPT 14 PART B: TODAY'S FINANCIAL BRIEF CARD */}
      {brief && (
        <View style={styles.briefCard}>
          <View style={styles.briefHeaderRow}>
            <Text style={styles.briefTitle}>📰 Today's Financial Brief</Text>
            <TouchableOpacity
              style={styles.listenBtn}
              onPress={() => speechSynthesis.speak(brief.summary_sentence + ". " + (brief.bullet_points || []).join(". "))}
            >
              <Text style={styles.listenBtnText}>🔊 Listen</Text>
            </TouchableOpacity>
          </View>
          <Text style={styles.briefSummary}>{brief.summary_sentence}</Text>
          <View style={styles.bulletList}>
            {(brief.bullet_points || []).map((pt: string, idx: number) => (
              <Text key={idx} style={styles.bulletPoint}>• {pt}</Text>
            ))}
          </View>
          <TouchableOpacity
            style={styles.askBriefBtn}
            onPress={() => router.push({ pathname: "/(tabs)/saarthi", params: { initialPrompt: "Explain today's financial brief to me." } } as any)}
          >
            <Text style={styles.askBriefBtnText}>Ask AI Saarthi to Explain Brief 💬</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* B. FINANCIAL HEALTH CARD */}
      <Pressable
        style={styles.healthCard}
        onPress={() => router.push("/twin-detail" as any)}
        accessibilityRole="button"
        accessibilityLabel={`Financial Health Score ${twin.financial_health_score} out of 100, ${scoreInfo.category}`}
        accessibilityHint="Tap to view full Financial Twin breakdown"
      >
        <View style={styles.cardHeaderRow}>
          <Text style={styles.cardKicker}>CENTRAL FINANCIAL TWIN</Text>
          <View style={[styles.badge, { backgroundColor: scoreInfo.color + "1A" }]}>
            <Text style={[styles.badgeText, { color: scoreInfo.color }]}>{scoreInfo.category}</Text>
          </View>
        </View>

        <View style={styles.scoreRow}>
          <Text style={styles.scoreNumber}>{twin.financial_health_score}</Text>
          <Text style={styles.scoreMax}>/ 100</Text>
        </View>

        <Text style={styles.scoreTitle}>{t("dashboard.health_title")}</Text>
        <Text style={styles.healthExplanation}>{scoreInfo.explanation}</Text>

        <View style={styles.cardFooter}>
          <Text style={styles.cardActionText}>View Complete Twin Details →</Text>
        </View>
      </Pressable>

      {/* C. FINANCIAL TWIN SNAPSHOT */}
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Profile Snapshot</Text>
      </View>

      <View style={styles.snapshotGrid}>
        <View
          style={styles.snapshotItem}
          accessibilityLabel={`${t("dashboard.surplus")}: ₹${surplus.toLocaleString("en-IN")}`}
        >
          <Text style={styles.snapshotLabel}>{t("dashboard.surplus")}</Text>
          <Text style={[styles.snapshotValue, { color: surplus >= 0 ? colors.purple : "#D32F2F" }]}>
            ₹{surplus.toLocaleString("en-IN")}
          </Text>
        </View>
        <View
          style={styles.snapshotItem}
          accessibilityLabel={`${t("dashboard.savings")}: ₹${savings.toLocaleString("en-IN")}`}
        >
          <Text style={styles.snapshotLabel}>{t("dashboard.savings")}</Text>
          <Text style={styles.snapshotValue}>₹{savings.toLocaleString("en-IN")}</Text>
        </View>
        <View
          style={styles.snapshotItem}
          accessibilityLabel={`Primary Goal: ${goal}`}
        >
          <Text style={styles.snapshotLabel}>Primary Goal</Text>
          <Text style={styles.snapshotValueSmall} numberOfLines={1}>
            {goal}
          </Text>
        </View>
        <View
          style={styles.snapshotItem}
          accessibilityLabel={`Risk Preference: ${risk}`}
        >
          <Text style={styles.snapshotLabel}>Risk Preference</Text>
          <Text style={styles.snapshotValueSmall}>{risk.charAt(0).toUpperCase() + risk.slice(1)}</Text>
        </View>
      </View>

      {/* D. AI INSIGHT CARD */}
      <View
        style={styles.insightCard}
        accessibilityLabel={`AI Financial Twin Insight: ${insightText}`}
      >
        <View style={styles.insightHeader}>
          <Text style={styles.insightIcon}>💡</Text>
          <Text style={styles.insightTitle}>{t("dashboard.ai_insight")}</Text>
        </View>
        <Text style={styles.insightText}>{insightText}</Text>
      </View>

      {/* E. CAPABILITY DOMAIN ENTRY POINTS */}
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>{t("more.capability_domains")}</Text>
        <Text style={styles.sectionSubtitle}>Six connected tools powered by your Financial Twin</Text>
      </View>

      <View style={styles.domainGrid}>
        {capabilityDomains.map((domain) => (
          <Pressable
            key={domain.id}
            style={styles.domainCard}
            onPress={domain.action}
            accessibilityRole="button"
            accessibilityLabel={`${domain.title}, ${domain.desc}`}
          >
            <View style={{ marginBottom: 10 }}>
              <DomainIconBadge domain={domain.id as DomainId} size="medium" />
            </View>
            <Text style={styles.domainTitle}>{domain.title}</Text>
            <Text style={styles.domainDesc}>{domain.desc}</Text>
          </Pressable>
        ))}
      </View>

    </Screen>
  );
}

const styles = StyleSheet.create({
  center: {
    justifyContent: "center",
    alignItems: "center",
  },
  loadingText: {
    marginTop: 16,
    color: colors.muted,
    fontSize: 15,
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: colors.ink,
    marginBottom: 8,
  },
  errorMessage: {
    color: colors.muted,
    textAlign: "center",
    marginBottom: 24,
  },
  header: {
    marginTop: 8,
    marginBottom: 20,
  },
  greeting: {
    fontSize: 26,
    fontWeight: "800",
    color: colors.ink,
  },
  statusLine: {
    fontSize: 15,
    color: colors.muted,
    marginTop: 4,
  },
  healthCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 24,
  },
  cardHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  cardKicker: {
    fontSize: 11,
    fontWeight: "800",
    color: colors.purple,
    letterSpacing: 1,
  },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: "700",
  },
  scoreRow: {
    flexDirection: "row",
    alignItems: "baseline",
    marginTop: 12,
  },
  scoreNumber: {
    fontSize: 48,
    fontWeight: "800",
    color: colors.purple,
  },
  scoreMax: {
    fontSize: 20,
    fontWeight: "600",
    color: colors.muted,
    marginLeft: 6,
  },
  scoreTitle: {
    fontSize: 14,
    fontWeight: "600",
    color: colors.ink,
    marginTop: 2,
  },
  healthExplanation: {
    fontSize: 14,
    color: colors.muted,
    lineHeight: 20,
    marginTop: 10,
  },
  cardFooter: {
    marginTop: 16,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  cardActionText: {
    fontSize: 14,
    fontWeight: "700",
    color: colors.purple,
  },
  sectionHeader: {
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "800",
    color: colors.ink,
  },
  sectionSubtitle: {
    fontSize: 13,
    color: colors.muted,
    marginTop: 2,
  },
  snapshotGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
    marginBottom: 20,
  },
  snapshotItem: {
    width: "48%",
    backgroundColor: "#FFFFFF",
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 12,
  },
  snapshotLabel: {
    fontSize: 12,
    color: colors.muted,
    fontWeight: "500",
  },
  snapshotValue: {
    fontSize: 18,
    fontWeight: "800",
    color: colors.ink,
    marginTop: 4,
  },
  snapshotValueSmall: {
    fontSize: 15,
    fontWeight: "700",
    color: colors.ink,
    marginTop: 4,
  },
  insightCard: {
    backgroundColor: colors.lavender,
    borderRadius: 16,
    padding: 16,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: colors.purple + "22",
  },
  insightHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 6,
  },
  insightIcon: {
    fontSize: 18,
    marginRight: 8,
  },
  insightTitle: {
    fontSize: 15,
    fontWeight: "800",
    color: colors.purple,
  },
  insightText: {
    fontSize: 14,
    color: colors.ink,
    lineHeight: 20,
  },
  domainGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
    marginBottom: 20,
  },
  domainCard: {
    width: "48%",
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 12,
  },
  domainIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  domainTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: colors.ink,
    marginBottom: 4,
  },
  domainDesc: {
    fontSize: 12,
    color: colors.muted,
    lineHeight: 16,
  },
  priorityCard: {
    backgroundColor: "#FEF2F2",
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: "#EF4444",
  },
  priorityHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  priorityKicker: {
    fontSize: 12,
    fontWeight: "900",
    color: "#DC2626",
    letterSpacing: 0.5,
  },
  priorityBadge: {
    backgroundColor: "#DC2626",
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
  },
  priorityBadgeText: {
    color: "#FFFFFF",
    fontSize: 10,
    fontWeight: "900",
  },
  priorityTitle: {
    fontSize: 16,
    fontWeight: "800",
    color: "#7F1D1D",
    marginBottom: 6,
  },
  priorityActionDesc: {
    fontSize: 14,
    color: "#991B1B",
    lineHeight: 20,
    marginBottom: 12,
  },
  priorityBtnRow: {
    flexDirection: "row",
    gap: 8,
  },
  priorityBtnPrimary: {
    backgroundColor: "#DC2626",
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 10,
    minHeight: 44,
    justifyContent: "center",
  },
  priorityBtnPrimaryText: {
    color: "#FFFFFF",
    fontWeight: "800",
    fontSize: 13,
  },
  priorityBtnSecondary: {
    backgroundColor: "#FFFFFF",
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: 10,
    borderWidth: 1.5,
    borderColor: "#DC2626",
    minHeight: 44,
    justifyContent: "center",
  },
  priorityBtnSecondaryText: {
    color: "#DC2626",
    fontWeight: "800",
    fontSize: 13,
  },
  briefCard: {
    backgroundColor: "#F0F9FF",
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1.5,
    borderColor: "#0284C7",
  },
  briefHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  briefTitle: {
    fontSize: 16,
    fontWeight: "800",
    color: "#0369A1",
  },
  listenBtn: {
    backgroundColor: "#E0F2FE",
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  listenBtnText: {
    color: "#0284C7",
    fontWeight: "800",
    fontSize: 12,
  },
  briefSummary: {
    fontSize: 14,
    fontWeight: "700",
    color: "#0F172A",
    marginBottom: 10,
  },
  bulletList: {
    marginBottom: 12,
    gap: 4,
  },
  bulletPoint: {
    fontSize: 13,
    color: "#334155",
    lineHeight: 18,
  },
  askBriefBtn: {
    backgroundColor: "#0284C7",
    paddingVertical: 10,
    borderRadius: 10,
    alignItems: "center",
    minHeight: 44,
    justifyContent: "center",
  },
  askBriefBtnText: {
    color: "#FFFFFF",
    fontWeight: "800",
    fontSize: 13,
  },
});

