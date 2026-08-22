import React, { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Modal,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import * as SecureStore from "expo-secure-store";
import { Button } from "@/components/Form";
import { Screen } from "@/components/Screen";
import { colors } from "@/constants/theme";
import { api } from "@/services/api";
import { LearningModule, QuizQuestion, QuizResult } from "@/types/api";

export default function LearnDetailScreen() {
  const params = useLocalSearchParams<{ moduleId?: string }>();
  const moduleId = params.moduleId || "savings-basics";

  const [moduleData, setModuleData] = useState<LearningModule | null>(null);
  const [loading, setLoading] = useState(true);

  // Quiz Modal State
  const [quizVisible, setQuizVisible] = useState(false);
  const [quizQuestions, setQuizQuestions] = useState<QuizQuestion[]>([]);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number>>({});
  const [submittingQuiz, setSubmittingQuiz] = useState(false);
  const [quizResult, setQuizResult] = useState<QuizResult | null>(null);

  useEffect(() => {
    fetchModuleDetail();
  }, [moduleId]);

  const fetchModuleDetail = async () => {
    try {
      setLoading(true);
      const token = await SecureStore.getItemAsync("user_token");
      if (!token) return;
      const data = await api.getLearningModuleDetail(moduleId, token);
      setModuleData(data);
      // Auto-start module if not started
      if (data.status === "NOT_STARTED") {
        await api.startLearningModule(moduleId, token);
      }
    } catch (err) {
      console.warn("Failed to fetch module detail", err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenQuiz = async () => {
    try {
      const token = await SecureStore.getItemAsync("user_token");
      if (!token) return;
      const questions = await api.getLearningQuiz(moduleId, token);
      setQuizQuestions(questions);
      setSelectedAnswers({});
      setQuizResult(null);
      setQuizVisible(true);
    } catch (err: any) {
      Alert.alert("Quiz Error", err.message || "Failed to load quiz questions.");
    }
  };

  const handleSelectAnswer = (qIdx: number, oIdx: number) => {
    setSelectedAnswers((prev) => ({ ...prev, [qIdx]: oIdx }));
  };

  const handleSubmitQuiz = async () => {
    if (Object.keys(selectedAnswers).length < quizQuestions.length) {
      Alert.alert("Incomplete Quiz", "Please answer all questions before submitting.");
      return;
    }

    try {
      setSubmittingQuiz(true);
      const token = await SecureStore.getItemAsync("user_token");
      if (!token) return;

      const answersArray = quizQuestions.map((_, idx) => selectedAnswers[idx]);
      const result = await api.submitLearningQuiz(moduleId, answersArray, token);
      setQuizResult(result);
      // Refresh module detail to reflect completed status
      fetchModuleDetail();
    } catch (err: any) {
      Alert.alert("Submission Failed", err.message || "Failed to submit quiz.");
    } finally {
      setSubmittingQuiz(false);
    }
  };

  const askSaarthiAboutTopic = () => {
    if (!moduleData) return;
    const promptMessage = `Can you explain the key concepts of '${moduleData.title}' in simple, easy-to-understand terms?`;
    router.push({
      pathname: "/(tabs)/saarthi",
      params: { initialPrompt: promptMessage },
    });
  };

  if (loading) {
    return (
      <Screen style={styles.center}>
        <ActivityIndicator size="large" color={colors.purple} />
        <Text style={styles.loadingText}>Loading lesson content...</Text>
      </Screen>
    );
  }

  if (!moduleData) {
    return (
      <Screen style={styles.center}>
        <Text style={styles.errorText}>Module not found.</Text>
        <Button title="Back to Learn" onPress={() => router.back()} />
      </Screen>
    );
  }

  return (
    <Screen style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* HEADER BADGES */}
        <View style={styles.topRow}>
          <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
            <Text style={styles.backText}>← Back</Text>
          </TouchableOpacity>
          <View style={styles.statusBadge}>
            <Text
              style={[
                styles.statusText,
                moduleData.status === "COMPLETED" ? styles.completedText : styles.inProgressText,
              ]}
            >
              {moduleData.status === "COMPLETED"
                ? `✓ Completed (${moduleData.quiz_score?.toFixed(0)}%)`
                : "In Progress"}
            </Text>
          </View>
        </View>

        <Text style={styles.category}>{moduleData.category.toUpperCase()} • {moduleData.estimated_minutes} MIN READ</Text>
        <Text style={styles.title}>{moduleData.title}</Text>
        <Text style={styles.description}>{moduleData.description}</Text>

        {/* LESSON SECTIONS */}
        {moduleData.lesson_content?.sections?.map((sec, idx) => (
          <View key={idx} style={styles.sectionCard}>
            <Text style={styles.sectionHeading}>{sec.heading}</Text>
            <Text style={styles.sectionBody}>{sec.body}</Text>
          </View>
        ))}

        {/* KEY TAKEAWAYS */}
        {moduleData.lesson_content?.key_takeaways && (
          <View style={styles.takeawayCard}>
            <Text style={styles.takeawayTitle}>💡 Key Takeaways</Text>
            {moduleData.lesson_content.key_takeaways.map((item, idx) => (
              <View key={idx} style={styles.takeawayRow}>
                <Text style={styles.takeawayDot}>•</Text>
                <Text style={styles.takeawayText}>{item}</Text>
              </View>
            ))}
          </View>
        )}

        {/* ACTION BUTTONS */}
        <View style={styles.actionContainer}>
          <TouchableOpacity style={styles.saarthiBtn} onPress={askSaarthiAboutTopic}>
            <Text style={styles.saarthiBtnText}>💬 Ask AI Saarthi to Explain Topic</Text>
          </TouchableOpacity>

          <Button
            title={
              moduleData.status === "COMPLETED"
                ? "📝 Retake Knowledge Check Quiz"
                : "📝 Take Knowledge Check Quiz"
            }
            onPress={handleOpenQuiz}
          />
        </View>
      </ScrollView>

      {/* QUIZ MODAL */}
      <Modal visible={quizVisible} animationType="slide" transparent={false}>
        <Screen style={styles.modalContainer}>
          <ScrollView contentContainerStyle={styles.scrollContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Knowledge Check</Text>
              <TouchableOpacity onPress={() => setQuizVisible(false)}>
                <Text style={styles.closeText}>✕ Close</Text>
              </TouchableOpacity>
            </View>
            <Text style={styles.modalSubtitle}>{moduleData.title}</Text>

            {quizResult ? (
              /* QUIZ RESULT VIEW */
              <View style={styles.resultBox}>
                <Text style={styles.resultIcon}>{quizResult.score_percentage >= 60 ? "🎉" : "💡"}</Text>
                <Text style={styles.resultScore}>
                  {quizResult.correct_count} / {quizResult.total_questions} Correct ({quizResult.score_percentage}%)
                </Text>
                <Text style={styles.resultFeedback}>{quizResult.feedback}</Text>
                <View style={{ marginTop: 20 }}>
                  <Button title="Finish & Return to Lesson" onPress={() => setQuizVisible(false)} />
                </View>
              </View>
            ) : (
              /* QUIZ QUESTION FORM */
              <View>
                {quizQuestions.map((q, qIdx) => (
                  <View key={q.id} style={styles.questionCard}>
                    <Text style={styles.questionText}>
                      {qIdx + 1}. {q.question}
                    </Text>
                    {q.options.map((opt, oIdx) => {
                      const isSelected = selectedAnswers[qIdx] === oIdx;
                      return (
                        <TouchableOpacity
                          key={oIdx}
                          style={[styles.optionChip, isSelected && styles.optionChipSelected]}
                          onPress={() => handleSelectAnswer(qIdx, oIdx)}
                        >
                          <View style={[styles.radioCircle, isSelected && styles.radioCircleSelected]} />
                          <Text style={[styles.optionText, isSelected && styles.optionTextSelected]}>
                            {opt}
                          </Text>
                        </TouchableOpacity>
                      );
                    })}
                  </View>
                ))}

                <Button
                  title={submittingQuiz ? "Evaluating..." : "Submit Quiz"}
                  onPress={handleSubmitQuiz}
                  disabled={submittingQuiz}
                />
              </View>
            )}
          </ScrollView>
        </Screen>
      </Modal>
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f8fafc",
  },
  center: {
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
    color: colors.muted,
  },
  errorText: {
    fontSize: 16,
    color: colors.ink,
    marginBottom: 16,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 40,
  },
  topRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 16,
  },
  backButton: {
    paddingVertical: 6,
    paddingHorizontal: 12,
    backgroundColor: "#e2e8f0",
    borderRadius: 8,
  },
  backText: {
    fontSize: 13,
    fontWeight: "700",
    color: colors.ink,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    backgroundColor: "#f1f5f9",
  },
  statusText: {
    fontSize: 12,
    fontWeight: "800",
  },
  completedText: {
    color: "#16a34a",
  },
  inProgressText: {
    color: colors.purple,
  },
  category: {
    fontSize: 12,
    fontWeight: "800",
    color: colors.purple,
    letterSpacing: 1.1,
    marginBottom: 4,
  },
  title: {
    fontSize: 26,
    fontWeight: "800",
    color: colors.ink,
    marginBottom: 8,
  },
  description: {
    fontSize: 15,
    color: colors.muted,
    lineHeight: 22,
    marginBottom: 20,
  },
  sectionCard: {
    backgroundColor: "#ffffff",
    borderRadius: 14,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  sectionHeading: {
    fontSize: 17,
    fontWeight: "700",
    color: colors.ink,
    marginBottom: 8,
  },
  sectionBody: {
    fontSize: 14,
    color: "#334155",
    lineHeight: 22,
  },
  takeawayCard: {
    backgroundColor: "#f0fdf4",
    borderRadius: 14,
    padding: 16,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: "#bbf7d0",
  },
  takeawayTitle: {
    fontSize: 16,
    fontWeight: "800",
    color: "#15803d",
    marginBottom: 10,
  },
  takeawayRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    marginBottom: 6,
    gap: 6,
  },
  takeawayDot: {
    color: "#15803d",
    fontSize: 14,
    fontWeight: "bold",
  },
  takeawayText: {
    fontSize: 13,
    color: "#166534",
    flex: 1,
    lineHeight: 18,
  },
  actionContainer: {
    gap: 12,
    marginTop: 8,
  },
  saarthiBtn: {
    backgroundColor: colors.lavender,
    borderWidth: 1,
    borderColor: colors.purple + "44",
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
  },
  saarthiBtnText: {
    color: colors.purple,
    fontWeight: "800",
    fontSize: 14,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: "#ffffff",
  },
  modalHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 4,
    marginTop: 8,
  },
  modalTitle: {
    fontSize: 22,
    fontWeight: "800",
    color: colors.ink,
  },
  closeText: {
    fontSize: 14,
    fontWeight: "700",
    color: colors.muted,
  },
  modalSubtitle: {
    fontSize: 14,
    color: colors.purple,
    fontWeight: "700",
    marginBottom: 20,
  },
  questionCard: {
    backgroundColor: "#f8fafc",
    borderRadius: 14,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  questionText: {
    fontSize: 15,
    fontWeight: "700",
    color: colors.ink,
    marginBottom: 12,
    lineHeight: 20,
  },
  optionChip: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#ffffff",
    padding: 12,
    borderRadius: 10,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: "#cbd5e1",
    gap: 10,
  },
  optionChipSelected: {
    borderColor: colors.purple,
    backgroundColor: colors.lavender + "44",
  },
  radioCircle: {
    width: 18,
    height: 18,
    borderRadius: 9,
    borderWidth: 2,
    borderColor: "#94a3b8",
  },
  radioCircleSelected: {
    borderColor: colors.purple,
    backgroundColor: colors.purple,
  },
  optionText: {
    fontSize: 13,
    color: colors.ink,
    flex: 1,
  },
  optionTextSelected: {
    fontWeight: "700",
    color: colors.purple,
  },
  resultBox: {
    alignItems: "center",
    backgroundColor: "#f8fafc",
    borderRadius: 16,
    padding: 24,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    marginTop: 20,
  },
  resultIcon: {
    fontSize: 56,
    marginBottom: 12,
  },
  resultScore: {
    fontSize: 22,
    fontWeight: "800",
    color: colors.ink,
    marginBottom: 8,
  },
  resultFeedback: {
    fontSize: 14,
    color: colors.muted,
    textAlign: "center",
    lineHeight: 20,
  },
});
