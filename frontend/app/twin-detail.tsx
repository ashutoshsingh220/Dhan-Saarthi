import { StyleSheet, Text, View } from "react-native";
import { router } from "expo-router";
import { Screen } from "@/components/Screen";
import { Button } from "@/components/Form";
import { colors } from "@/constants/theme";
import { useAuth } from "@/context/AuthContext";

function getScoreCategory(score: number): { category: string; explanation: string; color: string } {
  if (score >= 80) return { category: "Strong Position", explanation: "High stability, solid savings ratio, balanced risk strategy.", color: "#2E7D32" };
  if (score >= 60) return { category: "Good Progress", explanation: "Stable financial foundation with growth potential.", color: colors.purple };
  if (score >= 40) return { category: "Building Foundation", explanation: "Moderate stability. Emergency buffer build-up recommended.", color: "#ED6C02" };
  return { category: "Needs Attention", explanation: "High expense burden. Focus on budget control and cash flow.", color: "#D32F2F" };
}

export default function TwinDetailScreen() {
  const { profile, twin } = useAuth();

  if (!twin || !profile) {
    return (
      <Screen style={styles.center}>
        <Text style={styles.errorText}>No Financial Twin data found.</Text>
        <Button title="Back to Home" onPress={() => router.replace("/(tabs)/" as any)} />
      </Screen>
    );
  }

  const scoreInfo = getScoreCategory(twin.financial_health_score);
  const income = Number(profile.monthly_income);
  const expenses = Number(profile.monthly_expenses);
  const savings = Number(profile.savings);
  const surplus = income - expenses;
  const expenseRatio = income > 0 ? ((expenses / income) * 100).toFixed(1) : "0.0";
  const surplusRatio = income > 0 ? ((surplus / income) * 100).toFixed(1) : "0.0";
  const bufferMonths = expenses > 0 ? (savings / expenses).toFixed(1) : "0.0";

  return (
    <Screen>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.kicker}>INTELLIGENCE LAYER</Text>
        <Text style={styles.title}>Your Financial Twin</Text>
        <Text style={styles.subtitle}>
          A continuously evolving digital representation of your financial situation.
        </Text>
      </View>

      {/* Primary Health Score Card */}
      <View style={styles.card}>
        <View style={styles.rowBetween}>
          <Text style={styles.cardLabel}>HEALTH SCORE</Text>
          <View style={[styles.badge, { backgroundColor: scoreInfo.color + "1A" }]}>
            <Text style={[styles.badgeText, { color: scoreInfo.color }]}>{scoreInfo.category}</Text>
          </View>
        </View>
        <View style={styles.scoreRow}>
          <Text style={styles.scoreBig}>{twin.financial_health_score}</Text>
          <Text style={styles.scoreMax}>/ 100</Text>
        </View>
        <Text style={styles.cardDesc}>{scoreInfo.explanation}</Text>
      </View>

      {/* Financial Summary from Backend */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Financial Analysis Summary</Text>
        <View style={styles.summaryBox}>
          <Text style={styles.summaryText}>{twin.financial_summary}</Text>
        </View>
      </View>

      {/* Financial Cashflow & Buffer Metrics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Cashflow & Buffer Metrics</Text>
        <View style={styles.metricRow}>
          <View style={styles.metricCell}>
            <Text style={styles.metricLabel}>Monthly Income</Text>
            <Text style={styles.metricValue}>₹{income.toLocaleString("en-IN")}</Text>
          </View>
          <View style={styles.metricCell}>
            <Text style={styles.metricLabel}>Monthly Expenses</Text>
            <Text style={styles.metricValue}>₹{expenses.toLocaleString("en-IN")}</Text>
          </View>
        </View>

        <View style={styles.metricRow}>
          <View style={styles.metricCell}>
            <Text style={styles.metricLabel}>Monthly Surplus</Text>
            <Text style={[styles.metricValue, { color: surplus >= 0 ? colors.purple : "#D32F2F" }]}>
              ₹{surplus.toLocaleString("en-IN")} ({surplusRatio}%)
            </Text>
          </View>
          <View style={styles.metricCell}>
            <Text style={styles.metricLabel}>Expense Ratio</Text>
            <Text style={styles.metricValue}>{expenseRatio}%</Text>
          </View>
        </View>

        <View style={styles.metricRow}>
          <View style={styles.metricCell}>
            <Text style={styles.metricLabel}>Savings Buffer</Text>
            <Text style={styles.metricValue}>₹{savings.toLocaleString("en-IN")}</Text>
          </View>
          <View style={styles.metricCell}>
            <Text style={styles.metricLabel}>Buffer Capacity</Text>
            <Text style={styles.metricValue}>{bufferMonths} months</Text>
          </View>
        </View>
      </View>

      {/* Financial Strategy & Preference */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Goal & Strategy Alignment</Text>
        <View style={styles.detailBox}>
          <View style={styles.detailItem}>
            <Text style={styles.detailLabel}>Primary Financial Goal</Text>
            <Text style={styles.detailValue}>{profile.financial_goal}</Text>
          </View>
          <View style={styles.detailItem}>
            <Text style={styles.detailLabel}>Stated Risk Preference</Text>
            <Text style={styles.detailValue}>
              {profile.risk_preference.charAt(0).toUpperCase() + profile.risk_preference.slice(1)} (Assessed: {twin.risk_level})
            </Text>
          </View>
          <View style={styles.detailItem}>
            <Text style={styles.detailLabel}>Occupation / City</Text>
            <Text style={styles.detailValue}>
              {profile.occupation}{profile.city ? `, ${profile.city}` : ""}
            </Text>
          </View>
        </View>
      </View>

      {/* Disclaimer */}
      <View style={styles.disclaimerBox}>
        <Text style={styles.disclaimerTitle}>PROTOTYPE NOTICE</Text>
        <Text style={styles.disclaimerText}>
          This Financial Twin score is a deterministic prototype based on your self-reported profile data. It provides automated financial insights for planning purposes and does not constitute formal financial advice.
        </Text>
      </View>

      <View style={{ marginBottom: 30 }}>
        <Button title="Return to Dashboard" onPress={() => router.push("/(tabs)/" as any)} />
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  center: {
    justifyContent: "center",
    alignItems: "center",
  },
  errorText: {
    fontSize: 16,
    color: colors.muted,
    marginBottom: 16,
  },
  header: {
    marginTop: 8,
    marginBottom: 20,
  },
  kicker: {
    fontSize: 11,
    fontWeight: "800",
    color: colors.purple,
    letterSpacing: 1.2,
    marginBottom: 4,
  },
  title: {
    fontSize: 28,
    fontWeight: "800",
    color: colors.ink,
  },
  subtitle: {
    fontSize: 14,
    color: colors.muted,
    marginTop: 4,
    lineHeight: 20,
  },
  card: {
    backgroundColor: "#FFFFFF",
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 24,
  },
  rowBetween: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  cardLabel: {
    fontSize: 12,
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
  scoreBig: {
    fontSize: 52,
    fontWeight: "800",
    color: colors.purple,
  },
  scoreMax: {
    fontSize: 20,
    fontWeight: "600",
    color: colors.muted,
    marginLeft: 6,
  },
  cardDesc: {
    fontSize: 14,
    color: colors.muted,
    marginTop: 8,
    lineHeight: 20,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "800",
    color: colors.ink,
    marginBottom: 12,
  },
  summaryBox: {
    backgroundColor: colors.lavender,
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.purple + "22",
  },
  summaryText: {
    fontSize: 14,
    color: colors.ink,
    lineHeight: 22,
  },
  metricRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 10,
  },
  metricCell: {
    width: "48%",
    backgroundColor: "#FFFFFF",
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: colors.border,
  },
  metricLabel: {
    fontSize: 12,
    color: colors.muted,
  },
  metricValue: {
    fontSize: 16,
    fontWeight: "800",
    color: colors.ink,
    marginTop: 4,
  },
  detailBox: {
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.border,
  },
  detailItem: {
    marginBottom: 12,
  },
  detailLabel: {
    fontSize: 12,
    color: colors.muted,
  },
  detailValue: {
    fontSize: 15,
    fontWeight: "700",
    color: colors.ink,
    marginTop: 2,
  },
  disclaimerBox: {
    backgroundColor: "#F5F5F5",
    padding: 16,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: "#E0E0E0",
    marginBottom: 24,
  },
  disclaimerTitle: {
    fontSize: 11,
    fontWeight: "800",
    color: colors.muted,
    letterSpacing: 1,
    marginBottom: 4,
  },
  disclaimerText: {
    fontSize: 12,
    color: colors.muted,
    lineHeight: 18,
  },
});
