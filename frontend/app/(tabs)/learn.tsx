import React, { useCallback, useState } from "react";
import {
  ActivityIndicator,
  Modal,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { useFocusEffect } from "expo-router";
import * as SecureStore from "expo-secure-store";
import LearnDetailScreen from "@/app/domain/learn-detail";
import { Screen } from "@/components/Screen";
import { colors } from "@/constants/theme";
import { api } from "@/services/api";
import {
  LearningModule,
  LearningProgressSummary,
  LearningRecommendation,
} from "@/types/api";

export default function LearnTab() {
  const [modules, setModules] = useState<LearningModule[]>([]);
  const [progressSummary, setProgressSummary] = useState<LearningProgressSummary | null>(null);
  const [recommendations, setRecommendations] = useState<LearningRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Active module view modal
  const [selectedModuleId, setSelectedModuleId] = useState<string | null>(null);

  useFocusEffect(
    useCallback(() => {
      loadData();
    }, [])
  );

  const loadData = async () => {
    try {
      setLoading(true);
      const token = await SecureStore.getItemAsync("user_token");
      if (!token) return;

      const [mods, prog, recs] = await Promise.all([
        api.getLearningModules(token),
        api.getLearningProgress(token),
        api.getLearningRecommendations(token),
      ]);

      setModules(mods);
      setProgressSummary(prog);
      setRecommendations(recs);
    } catch (err) {
      console.warn("Failed to load financial literacy data", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "COMPLETED":
        return "#16a34a";
      case "IN_PROGRESS":
        return colors.purple;
      case "NOT_STARTED":
      default:
        return "#64748b";
    }
  };

  const getStatusBg = (status: string) => {
    switch (status) {
      case "COMPLETED":
        return "#f0fdf4";
      case "IN_PROGRESS":
        return colors.lavender;
      case "NOT_STARTED":
      default:
        return "#f1f5f9";
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "Basics":
        return "💰";
      case "Budgeting":
        return "📊";
      case "Credit":
        return "💳";
      case "Safety":
        return "🛡️";
      case "Investing":
        return "📈";
      case "Goals":
        return "🎯";
      default:
        return "📚";
    }
  };

  return (
    <Screen style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {/* HEADER */}
        <View style={styles.header}>
          <Text style={styles.headerIcon}>📚</Text>
          <Text style={styles.headerTitle}>Learn & Grow</Text>
          <Text style={styles.headerSubtitle}>Build stronger financial habits, one step at a time.</Text>
        </View>

        {/* PROGRESS SUMMARY CARD */}
        {progressSummary && (
          <View style={styles.progressCard}>
            <View style={styles.progressTop}>
              <View>
                <Text style={styles.progressTitle}>Overall Learning Progress</Text>
                <Text style={styles.progressCount}>
                  {progressSummary.completed_modules} of {progressSummary.total_modules} Modules Completed
                </Text>
              </View>
              <Text style={styles.progressPct}>{progressSummary.completion_percentage}%</Text>
            </View>

            {/* Progress Bar */}
            <View style={styles.progressBarTrack}>
              <View
                style={[
                  styles.progressBarFill,
                  { width: `${Math.min(100, progressSummary.completion_percentage)}%` },
                ]}
              />
            </View>
          </View>
        )}

        {/* RECOMMENDED FOR YOU */}
        {recommendations.length > 0 && (
          <View style={styles.sectionContainer}>
            <Text style={styles.sectionTitle}>🎯 Recommended For You</Text>
            {recommendations.map((rec) => (
              <TouchableOpacity
                key={rec.module_id}
                style={styles.recCard}
                onPress={() => setSelectedModuleId(rec.module_id)}
              >
                <View style={styles.recTop}>
                  <Text style={styles.recTitle}>{rec.title}</Text>
                  <Text style={styles.recTime}>⏱ {rec.estimated_minutes} min</Text>
                </View>
                <Text style={styles.recReason}>{rec.reason}</Text>
                <View style={styles.recBtnRow}>
                  <Text style={styles.recBtnText}>Start Lesson →</Text>
                </View>
              </TouchableOpacity>
            ))}
          </View>
        )}

        {/* ALL LEARNING MODULES CATALOGUE */}
        <View style={styles.sectionContainer}>
          <Text style={styles.sectionTitle}>📖 All Financial Literacy Modules</Text>
          {loading && !refreshing ? (
            <ActivityIndicator size="small" color={colors.purple} style={{ marginVertical: 20 }} />
          ) : (
            modules.map((m) => (
              <TouchableOpacity
                key={m.module_id}
                style={styles.moduleCard}
                onPress={() => setSelectedModuleId(m.module_id)}
              >
                <View style={styles.moduleLeft}>
                  <Text style={styles.moduleIcon}>{getCategoryIcon(m.category)}</Text>
                  <View style={{ flex: 1 }}>
                    <View style={styles.moduleTagRow}>
                      <Text style={styles.moduleCategory}>{m.category.toUpperCase()}</Text>
                      <Text style={styles.moduleDot}>•</Text>
                      <Text style={styles.moduleMeta}>{m.difficulty} • {m.estimated_minutes} min</Text>
                    </View>
                    <Text style={styles.moduleTitle}>{m.title}</Text>
                    <Text style={styles.moduleDesc} numberOfLines={2}>
                      {m.description}
                    </Text>
                  </View>
                </View>

                <View style={styles.moduleRight}>
                  <View style={[styles.statusBadge, { backgroundColor: getStatusBg(m.status) }]}>
                    <Text style={[styles.statusText, { color: getStatusColor(m.status) }]}>
                      {m.status === "COMPLETED"
                        ? `✓ ${m.quiz_score?.toFixed(0)}%`
                        : m.status === "IN_PROGRESS"
                        ? "In Progress"
                        : "Start"}
                    </Text>
                  </View>
                </View>
              </TouchableOpacity>
            ))
          )}
        </View>
      </ScrollView>

      {/* MODULE DETAIL MODAL */}
      {selectedModuleId && (
        <Modal visible={!!selectedModuleId} animationType="slide">
          <Screen style={{ flex: 1 }}>
            {/* Wrap detail view with ability to close modal */}
            <View style={styles.modalHeaderClose}>
              <TouchableOpacity onPress={() => { setSelectedModuleId(null); loadData(); }}>
                <Text style={styles.modalCloseText}>✕ Close Lesson</Text>
              </TouchableOpacity>
            </View>
            <LearnDetailScreen />
          </Screen>
        </Modal>
      )}
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
  progressCard: {
    backgroundColor: "#ffffff",
    borderRadius: 16,
    padding: 16,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  progressTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  progressTitle: {
    fontSize: 16,
    fontWeight: "800",
    color: colors.ink,
  },
  progressCount: {
    fontSize: 13,
    color: colors.muted,
    marginTop: 2,
  },
  progressPct: {
    fontSize: 22,
    fontWeight: "900",
    color: colors.purple,
  },
  progressBarTrack: {
    height: 10,
    backgroundColor: "#f1f5f9",
    borderRadius: 5,
    overflow: "hidden",
  },
  progressBarFill: {
    height: "100%",
    backgroundColor: colors.purple,
    borderRadius: 5,
  },
  sectionContainer: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "800",
    color: colors.ink,
    marginBottom: 12,
  },
  recCard: {
    backgroundColor: colors.lavender + "33",
    borderRadius: 14,
    padding: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: colors.purple + "33",
  },
  recTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 4,
  },
  recTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: colors.ink,
  },
  recTime: {
    fontSize: 12,
    fontWeight: "600",
    color: colors.purple,
  },
  recReason: {
    fontSize: 13,
    color: colors.muted,
    marginBottom: 10,
    lineHeight: 18,
  },
  recBtnRow: {
    alignSelf: "flex-start",
  },
  recBtnText: {
    fontSize: 13,
    fontWeight: "800",
    color: colors.purple,
  },
  moduleCard: {
    backgroundColor: "#ffffff",
    borderRadius: 14,
    padding: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  moduleLeft: {
    flexDirection: "row",
    alignItems: "flex-start",
    flex: 1,
    gap: 12,
  },
  moduleIcon: {
    fontSize: 28,
    marginTop: 2,
  },
  moduleTagRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    marginBottom: 2,
  },
  moduleCategory: {
    fontSize: 11,
    fontWeight: "800",
    color: colors.purple,
  },
  moduleDot: {
    fontSize: 11,
    color: colors.muted,
  },
  moduleMeta: {
    fontSize: 11,
    color: colors.muted,
  },
  moduleTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: colors.ink,
    marginBottom: 2,
  },
  moduleDesc: {
    fontSize: 12,
    color: colors.muted,
    lineHeight: 16,
  },
  moduleRight: {
    marginLeft: 8,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: "800",
  },
  modalHeaderClose: {
    padding: 12,
    backgroundColor: "#ffffff",
    borderBottomWidth: 1,
    borderBottomColor: "#e2e8f0",
    alignItems: "flex-end",
  },
  modalCloseText: {
    fontSize: 14,
    fontWeight: "800",
    color: colors.purple,
  },
});
