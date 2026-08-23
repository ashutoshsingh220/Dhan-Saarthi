import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { useRouter } from "expo-router";
import { Screen } from "@/components/Screen";
import { colors } from "@/constants/theme";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/services/api";
import { FinancialGoal } from "@/types/api";

const CATEGORIES = [
  { id: "emergency_fund", label: "Emergency Fund", icon: "🛡️" },
  { id: "home", label: "Home Purchase", icon: "🏠" },
  { id: "education", label: "Education", icon: "🎓" },
  { id: "vehicle", label: "Vehicle", icon: "🚗" },
  { id: "travel", label: "Travel & Vacation", icon: "✈️" },
  { id: "investment", label: "Wealth & Investment", icon: "📈" },
  { id: "other", label: "Other Goal", icon: "🎯" },
];

export default function SmartPlanningScreen() {
  const { token } = useAuth();
  const router = useRouter();

  const [goals, setGoals] = useState<FinancialGoal[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedGoal, setSelectedGoal] = useState<FinancialGoal | null>(null);

  // Modal states
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [progressModalVisible, setProgressModalVisible] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Create Goal form state
  const [name, setName] = useState("");
  const [category, setCategory] = useState("emergency_fund");
  const [targetAmount, setTargetAmount] = useState("");
  const [currentAmount, setCurrentAmount] = useState("");
  const [targetDate, setTargetDate] = useState("");

  // Progress update form state
  const [addAmount, setAddAmount] = useState("");

  const loadGoals = async () => {
    if (!token) return;
    try {
      setLoading(true);
      const data = await api.getGoals(token);
      setGoals(data);
    } catch (e) {
      setErrorMsg(e instanceof Error ? e.message : "Failed to load financial goals");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGoals();
  }, [token]);

  const handleCreateGoal = async () => {
    if (!token || submitting) return;
    setErrorMsg(null);

    const targetVal = parseFloat(targetAmount);
    const currentVal = currentAmount ? parseFloat(currentAmount) : 0.0;

    if (!name.trim()) return setErrorMsg("Goal name is required");
    if (isNaN(targetVal) || targetVal <= 0) return setErrorMsg("Target amount must be a positive number");
    if (isNaN(currentVal) || currentVal < 0) return setErrorMsg("Current saved amount cannot be negative");
    if (!targetDate || !/^\d{4}-\d{2}-\d{2}$/.test(targetDate)) {
      return setErrorMsg("Please enter a valid date in YYYY-MM-DD format");
    }

    try {
      setSubmitting(true);
      const newGoal = await api.createGoal(
        {
          name: name.trim(),
          category,
          target_amount: targetVal,
          current_amount: currentVal,
          target_date: targetDate,
        },
        token
      );
      setGoals((prev) => [newGoal, ...prev]);
      setCreateModalVisible(false);
      // Reset form
      setName("");
      setTargetAmount("");
      setCurrentAmount("");
      setTargetDate("");
      setSelectedGoal(newGoal);
    } catch (e) {
      setErrorMsg(e instanceof Error ? e.message : "Failed to create financial goal");
    } finally {
      setSubmitting(false);
    }
  };

  const handleAddProgress = async () => {
    if (!token || !selectedGoal || submitting) return;
    setErrorMsg(null);

    const val = parseFloat(addAmount);
    if (isNaN(val) || val <= 0) return setErrorMsg("Contribution amount must be greater than zero");

    try {
      setSubmitting(true);
      const updated = await api.addGoalProgress(selectedGoal.id, val, token);
      setSelectedGoal(updated);
      setGoals((prev) => prev.map((g) => (g.id === updated.id ? updated : g)));
      setProgressModalVisible(false);
      setAddAmount("");
    } catch (e) {
      setErrorMsg(e instanceof Error ? e.message : "Failed to update progress");
    } finally {
      setSubmitting(false);
    }
  };

  const handleRecalculate = async () => {
    if (!token || !selectedGoal || submitting) return;
    try {
      setSubmitting(true);
      const updated = await api.recalculateGoalPlan(selectedGoal.id, token);
      setSelectedGoal(updated);
      setGoals((prev) => prev.map((g) => (g.id === updated.id ? updated : g)));
    } catch (e) {
      setErrorMsg(e instanceof Error ? e.message : "Recalculation failed");
    } finally {
      setSubmitting(false);
    }
  };

  const handleAskSaarthi = () => {
    if (!selectedGoal) return;
    const planInfo = selectedGoal.plan;
    const reqText = planInfo ? `₹${planInfo.monthly_required.toLocaleString("en-IN")}/month` : "N/A";
    const feasText = planInfo ? planInfo.feasibility_status : "N/A";
    const promptMessage = `I want to understand my financial goal plan for '${selectedGoal.name}' (${selectedGoal.category}) better. Target: ₹${selectedGoal.target_amount.toLocaleString("en-IN")}, Current: ₹${selectedGoal.current_amount.toLocaleString("en-IN")}, Target Date: ${selectedGoal.target_date}. Monthly required: ${reqText}, Feasibility status: ${feasText}. Please explain my plan, why it has this feasibility status, and what I can realistically do to improve it based on my stored profile numbers without altering any calculations.`;
    router.push({
      pathname: "/(tabs)/saarthi",
      params: { initialPrompt: promptMessage },
    });
  };


  const renderFeasibilityBadge = (status?: string) => {
    if (status === "FEASIBLE") {
      return (
        <View style={[styles.badge, { backgroundColor: "#D1FADF", borderColor: "#12B76A" }]}>
          <Text style={[styles.badgeText, { color: "#027A48" }]}>FEASIBLE</Text>
        </View>
      );
    } else if (status === "TIGHT") {
      return (
        <View style={[styles.badge, { backgroundColor: "#FEF0C7", borderColor: "#F79009" }]}>
          <Text style={[styles.badgeText, { color: "#B54708" }]}>TIGHT</Text>
        </View>
      );
    } else {
      return (
        <View style={[styles.badge, { backgroundColor: "#FEE4E2", borderColor: "#F04438" }]}>
          <Text style={[styles.badgeText, { color: "#B42318" }]}>AT RISK</Text>
        </View>
      );
    }
  };

  return (
    <Screen style={styles.screen}>
      <ScrollView contentContainerStyle={styles.container}>
        {/* Header */}
        <View style={styles.headerRow}>
          <Pressable style={styles.backBtn} onPress={() => router.back()}>
            <Text style={styles.backBtnText}>← Back</Text>
          </Pressable>
          <Pressable style={styles.createBtnHeader} onPress={() => setCreateModalVisible(true)}>
            <Text style={styles.createBtnHeaderText}>+ New Goal</Text>
          </Pressable>
        </View>

        <View style={styles.titleSection}>
          <Text style={styles.title}>Smart Financial Planning</Text>
          <Text style={styles.subtitle}>Turn your financial goals into deterministic, actionable plans.</Text>
        </View>

        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.purple} />
            <Text style={styles.loadingText}>Calculating your financial plans...</Text>
          </View>
        ) : goals.length === 0 ? (
          /* Empty State */
          <View style={styles.emptyCard}>
            <Text style={styles.emptyIcon}>🎯</Text>
            <Text style={styles.emptyTitle}>Your financial plan starts with a goal.</Text>
            <Text style={styles.emptySub}>
              Set a target for an emergency fund, home purchase, education, or travel. Saarthi will calculate your exact required monthly savings.
            </Text>
            <Pressable style={styles.createFirstBtn} onPress={() => setCreateModalVisible(true)}>
              <Text style={styles.createFirstBtnText}>Create Your First Goal</Text>
            </Pressable>
          </View>
        ) : (
          /* Goals List */
          <View style={styles.goalsListSection}>
            <Text style={styles.sectionHeader}>YOUR ACTIVE GOALS ({goals.length})</Text>
            {goals.map((g) => {
              const progressPct = Math.min(100, Math.round((g.current_amount / g.target_amount) * 100));
              const catObj = CATEGORIES.find((c) => c.id === g.category);

              return (
                <Pressable key={g.id} style={styles.goalCard} onPress={() => setSelectedGoal(g)}>
                  <View style={styles.goalCardHeader}>
                    <View style={styles.goalTitleRow}>
                      <Text style={styles.catIcon}>{catObj?.icon || "🎯"}</Text>
                      <Text style={styles.goalName}>{g.name}</Text>
                    </View>
                    {renderFeasibilityBadge(g.plan?.feasibility_status)}
                  </View>

                  <View style={styles.progressRow}>
                    <Text style={styles.amountText}>
                      ₹{g.current_amount.toLocaleString("en-IN")} / ₹{g.target_amount.toLocaleString("en-IN")}
                    </Text>
                    <Text style={styles.pctText}>{progressPct}% Saved</Text>
                  </View>

                  {/* Progress bar */}
                  <View style={styles.trackBar}>
                    <View style={[styles.fillBar, { width: `${progressPct}%` }]} />
                  </View>

                  {g.plan && (
                    <View style={styles.metaRow}>
                      <Text style={styles.metaText}>Required: ₹{g.plan.monthly_required.toLocaleString("en-IN")}/mo</Text>
                      <Text style={styles.metaText}>Target: {g.target_date}</Text>
                    </View>
                  )}
                </Pressable>
              );
            })}
          </View>
        )}

        {/* Goal Detail Modal */}
        {selectedGoal && (
          <Modal visible={true} animationType="slide" transparent={true}>
            <View style={styles.modalOverlay}>
              <View style={styles.detailCard}>
                <ScrollView contentContainerStyle={{ paddingBottom: 20 }}>
                  <View style={styles.detailHeader}>
                    <Text style={styles.detailTitle}>{selectedGoal.name}</Text>
                    <Pressable onPress={() => setSelectedGoal(null)}>
                      <Text style={styles.closeText}>✕</Text>
                    </Pressable>
                  </View>

                  <View style={styles.badgeLine}>
                    <Text style={styles.catTag}>{selectedGoal.category.toUpperCase()}</Text>
                    {renderFeasibilityBadge(selectedGoal.plan?.feasibility_status)}
                  </View>

                  {/* Cashflow Capacity vs Requirement */}
                  {selectedGoal.plan && (
                    <View style={styles.analysisBox}>
                      <Text style={styles.boxTitle}>DETERMINISTIC CASHFLOW ANALYSIS</Text>
                      <View style={styles.statGrid}>
                        <View style={styles.statItem}>
                          <Text style={styles.statLabel}>Monthly Required</Text>
                          <Text style={styles.statVal}>₹{selectedGoal.plan.monthly_required.toLocaleString("en-IN")}</Text>
                        </View>
                        <View style={styles.statItem}>
                          <Text style={styles.statLabel}>Available Surplus</Text>
                          <Text style={styles.statVal}>₹{selectedGoal.plan.available_monthly_capacity.toLocaleString("en-IN")}</Text>
                        </View>
                      </View>
                      <Text style={styles.recText}>{selectedGoal.plan.recommendation_text}</Text>
                    </View>
                  )}

                  {/* Milestones Checklist */}
                  {selectedGoal.plan?.milestones && selectedGoal.plan.milestones.length > 0 && (
                    <View style={styles.milestoneSection}>
                      <Text style={styles.boxTitle}>PROGRESS CHECKPOINTS & MILESTONES</Text>
                      {selectedGoal.plan.milestones.map((m) => (
                        <View key={m.id} style={styles.milestoneRow}>
                          <Text style={styles.checkIcon}>{m.status === "completed" ? "✅" : "⏳"}</Text>
                          <View style={{ flex: 1 }}>
                            <Text style={styles.mTitle}>{m.title}</Text>
                            <Text style={styles.mMeta}>Target Date: {m.milestone_date} (₹{m.target_amount.toLocaleString("en-IN")})</Text>
                          </View>
                        </View>
                      ))}
                    </View>
                  )}

                  {/* Action Buttons */}
                  <View style={styles.actionGroup}>
                    <Pressable style={styles.primaryAction} onPress={() => setProgressModalVisible(true)}>
                      <Text style={styles.primaryActionText}>+ Add Savings Progress</Text>
                    </Pressable>

                    <Pressable style={styles.secondaryAction} onPress={handleRecalculate} disabled={submitting}>
                      <Text style={styles.secondaryActionText}>Recalculate Plan</Text>
                    </Pressable>

                    <Pressable style={styles.saarthiAction} onPress={handleAskSaarthi}>
                      <Text style={styles.saarthiActionText}>🤖 Ask Saarthi About This Plan</Text>
                    </Pressable>
                  </View>
                </ScrollView>
              </View>
            </View>
          </Modal>
        )}

        {/* Create Goal Modal */}
        <Modal visible={createModalVisible} animationType="fade" transparent={true}>
          <View style={styles.modalOverlay}>
            <View style={styles.formCard}>
              <Text style={styles.formTitle}>Create Financial Goal</Text>
              {errorMsg && <Text style={styles.errorBanner}>{errorMsg}</Text>}

              <Text style={styles.fieldLabel}>Goal Name</Text>
              <TextInput style={styles.input} placeholder="e.g. Home Down Payment" value={name} onChangeText={setName} />

              <Text style={styles.fieldLabel}>Category</Text>
              <View style={styles.catGrid}>
                {CATEGORIES.map((c) => (
                  <Pressable
                    key={c.id}
                    style={[styles.catPill, category === c.id && styles.catPillSelected]}
                    onPress={() => setCategory(c.id)}
                  >
                    <Text style={[styles.catPillText, category === c.id && styles.catPillTextSelected]}>
                      {c.icon} {c.label}
                    </Text>
                  </Pressable>
                ))}
              </View>

              <Text style={styles.fieldLabel}>Target Amount (₹)</Text>
              <TextInput
                style={styles.input}
                placeholder="100000"
                keyboardType="numeric"
                value={targetAmount}
                onChangeText={setTargetAmount}
              />

              <Text style={styles.fieldLabel}>Current Saved Amount (₹)</Text>
              <TextInput
                style={styles.input}
                placeholder="10000"
                keyboardType="numeric"
                value={currentAmount}
                onChangeText={setCurrentAmount}
              />

              <Text style={styles.fieldLabel}>Target Date (YYYY-MM-DD)</Text>
              <TextInput style={styles.input} placeholder="2027-12-31" value={targetDate} onChangeText={setTargetDate} />

              <View style={styles.formActionRow}>
                <Pressable style={styles.cancelBtn} onPress={() => setCreateModalVisible(false)}>
                  <Text style={styles.cancelBtnText}>Cancel</Text>
                </Pressable>
                <Pressable style={styles.submitBtn} onPress={handleCreateGoal} disabled={submitting}>
                  <Text style={styles.submitBtnText}>{submitting ? "Saving..." : "Create Plan"}</Text>
                </Pressable>
              </View>
            </View>
          </View>
        </Modal>

        {/* Add Progress Modal */}
        <Modal visible={progressModalVisible} animationType="fade" transparent={true}>
          <View style={styles.modalOverlay}>
            <View style={styles.formCard}>
              <Text style={styles.formTitle}>Add Savings Progress</Text>
              {errorMsg && <Text style={styles.errorBanner}>{errorMsg}</Text>}

              <Text style={styles.fieldLabel}>Contribution Amount (₹)</Text>
              <TextInput
                style={styles.input}
                placeholder="5000"
                keyboardType="numeric"
                value={addAmount}
                onChangeText={setAddAmount}
              />

              <View style={styles.formActionRow}>
                <Pressable style={styles.cancelBtn} onPress={() => setProgressModalVisible(false)}>
                  <Text style={styles.cancelBtnText}>Cancel</Text>
                </Pressable>
                <Pressable style={styles.submitBtn} onPress={handleAddProgress} disabled={submitting}>
                  <Text style={styles.submitBtnText}>{submitting ? "Updating..." : "Add Savings"}</Text>
                </Pressable>
              </View>
            </View>
          </View>
        </Modal>
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  container: { padding: 16 },
  headerRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 12 },
  backBtn: { paddingVertical: 6, paddingHorizontal: 12 },
  backBtnText: { color: colors.purple, fontWeight: "700", fontSize: 14 },
  createBtnHeader: { backgroundColor: colors.purple, paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20 },
  createBtnHeaderText: { color: "#FFFFFF", fontWeight: "700", fontSize: 13 },
  titleSection: { marginBottom: 20 },
  title: { fontSize: 26, fontWeight: "800", color: colors.ink },
  subtitle: { fontSize: 14, color: colors.muted, marginTop: 4 },
  loadingContainer: { padding: 40, alignItems: "center" },
  loadingText: { marginTop: 12, color: colors.muted },
  emptyCard: { backgroundColor: "#FFFFFF", padding: 24, borderRadius: 20, alignItems: "center", borderWidth: 1, borderColor: colors.border },
  emptyIcon: { fontSize: 48, marginBottom: 12 },
  emptyTitle: { fontSize: 20, fontWeight: "800", color: colors.ink, textAlign: "center", marginBottom: 8 },
  emptySub: { fontSize: 14, color: colors.muted, textAlign: "center", lineHeight: 20, marginBottom: 20 },
  createFirstBtn: { backgroundColor: colors.purple, paddingHorizontal: 24, paddingVertical: 14, borderRadius: 24 },
  createFirstBtnText: { color: "#FFFFFF", fontWeight: "800", fontSize: 15 },
  goalsListSection: { marginTop: 4 },
  sectionHeader: { fontSize: 11, fontWeight: "800", color: colors.purple, letterSpacing: 1, marginBottom: 12 },
  goalCard: { backgroundColor: "#FFFFFF", padding: 16, borderRadius: 16, borderWidth: 1, borderColor: colors.border, marginBottom: 12 },
  goalCardHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 10 },
  goalTitleRow: { flexDirection: "row", alignItems: "center" },
  catIcon: { fontSize: 20, marginRight: 8 },
  goalName: { fontSize: 17, fontWeight: "700", color: colors.ink },
  badge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12, borderWidth: 1 },
  badgeText: { fontSize: 11, fontWeight: "800" },
  progressRow: { flexDirection: "row", justifyContent: "space-between", marginBottom: 6 },
  amountText: { fontSize: 14, fontWeight: "600", color: colors.ink },
  pctText: { fontSize: 14, fontWeight: "700", color: colors.purple },
  trackBar: { height: 8, backgroundColor: colors.lavender, borderRadius: 4, overflow: "hidden", marginBottom: 10 },
  fillBar: { height: "100%", backgroundColor: colors.purple, borderRadius: 4 },
  metaRow: { flexDirection: "row", justifyContent: "space-between" },
  metaText: { fontSize: 12, color: colors.muted },
  modalOverlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.5)", justifyContent: "center", padding: 16 },
  detailCard: { backgroundColor: "#FFFFFF", borderRadius: 24, padding: 20, maxHeight: "85%" },
  detailHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 8 },
  detailTitle: { fontSize: 22, fontWeight: "800", color: colors.ink },
  closeText: { fontSize: 20, color: colors.muted, fontWeight: "700" },
  badgeLine: { flexDirection: "row", alignItems: "center", marginBottom: 16 },
  catTag: { fontSize: 11, fontWeight: "800", color: colors.muted, marginRight: 10 },
  analysisBox: { backgroundColor: colors.lavender, padding: 14, borderRadius: 14, marginBottom: 16 },
  boxTitle: { fontSize: 11, fontWeight: "800", color: colors.purple, letterSpacing: 1, marginBottom: 8 },
  statGrid: { flexDirection: "row", justifyContent: "space-between", marginBottom: 8 },
  statItem: { flex: 1 },
  statLabel: { fontSize: 12, color: colors.muted },
  statVal: { fontSize: 16, fontWeight: "800", color: colors.ink },
  recText: { fontSize: 13, color: colors.ink, lineHeight: 18, fontStyle: "italic" },
  milestoneSection: { marginBottom: 20 },
  milestoneRow: { flexDirection: "row", alignItems: "center", marginBottom: 10 },
  checkIcon: { fontSize: 18, marginRight: 10 },
  mTitle: { fontSize: 14, fontWeight: "700", color: colors.ink },
  mMeta: { fontSize: 12, color: colors.muted },
  actionGroup: { gap: 10 },
  primaryAction: { backgroundColor: colors.purple, paddingVertical: 14, borderRadius: 20, alignItems: "center" },
  primaryActionText: { color: "#FFFFFF", fontWeight: "800", fontSize: 15 },
  secondaryAction: { backgroundColor: colors.lavender, paddingVertical: 12, borderRadius: 20, alignItems: "center", borderWidth: 1, borderColor: colors.purple + "33" },
  secondaryActionText: { color: colors.purple, fontWeight: "700", fontSize: 14 },
  saarthiAction: { backgroundColor: "#F4F3FF", paddingVertical: 12, borderRadius: 20, alignItems: "center", borderWidth: 1, borderColor: colors.purple + "55" },
  saarthiActionText: { color: colors.purple, fontWeight: "800", fontSize: 14 },
  formCard: { backgroundColor: "#FFFFFF", borderRadius: 24, padding: 20 },
  formTitle: { fontSize: 20, fontWeight: "800", color: colors.ink, marginBottom: 12 },
  errorBanner: { color: colors.danger, fontSize: 13, marginBottom: 10, fontWeight: "600" },
  fieldLabel: { fontSize: 12, fontWeight: "700", color: colors.ink, marginBottom: 4, marginTop: 8 },
  input: { borderWidth: 1, borderColor: colors.border, borderRadius: 12, paddingHorizontal: 12, paddingVertical: 10, fontSize: 14, color: colors.ink },
  catGrid: { flexDirection: "row", flexWrap: "wrap", gap: 6, marginVertical: 4 },
  catPill: { paddingHorizontal: 10, paddingVertical: 6, borderRadius: 14, borderWidth: 1, borderColor: colors.border, backgroundColor: "#FFFFFF" },
  catPillSelected: { backgroundColor: colors.purple, borderColor: colors.purple },
  catPillText: { fontSize: 12, fontWeight: "600", color: colors.ink },
  catPillTextSelected: { color: "#FFFFFF" },
  formActionRow: { flexDirection: "row", justifyContent: "flex-end", gap: 12, marginTop: 20 },
  cancelBtn: { paddingHorizontal: 16, paddingVertical: 10, borderRadius: 18 },
  cancelBtnText: { color: colors.muted, fontWeight: "700" },
  submitBtn: { backgroundColor: colors.purple, paddingHorizontal: 20, paddingVertical: 10, borderRadius: 18 },
  submitBtnText: { color: "#FFFFFF", fontWeight: "800" },
});
