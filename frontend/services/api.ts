import {
  AuthResult,
  FinancialGoal,
  GoalCreatePayload,
  GovernmentScheme,
  LearningModule,
  LearningProgressSummary,
  LearningRecommendation,
  MarketAsset,
  MarketOverview,
  PersonalizedRecommendation,
  ProfilePayload,


  ProfileResponse,
  QuizQuestion,
  QuizResult,
  SaarthiChatResponse,
  SaarthiMessage,
  SaarthiSession,
  ScamHistoryResponse,
  ScamScan,
  SchemeCategoryCount,
  SchemeEligibility,
  SchemeRecommendation,
  SupportContextPayload,
  SupportContextResponse,
  Twin,
  User,
} from "@/types/api";


const baseUrl = process.env.EXPO_PUBLIC_API_BASE_URL || "http://localhost:8000/api";

async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  try {
    const response = await fetch(`${baseUrl}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Something went wrong. Please try again.");
    return data as T;
  } catch (error) {
    if (error instanceof Error && error.message !== "Network request failed") throw error;
    throw new Error("Unable to reach Dhan Saarthi. Check your network and API URL.");
  }
}

export const api = {
  register: (full_name: string, email: string, password: string) =>
    request<AuthResult>("/auth/register", { method: "POST", body: JSON.stringify({ full_name, email, password }) }),
  login: (email: string, password: string) =>
    request<AuthResult>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  me: (token: string) => request<{ user: User; onboarding_complete: boolean }>("/auth/me", {}, token),
  getProfile: (token: string) => request<ProfileResponse>("/profile", {}, token),
  saveProfile: (payload: ProfilePayload, token: string) =>
    request<ProfileResponse>("/profile", { method: "PUT", body: JSON.stringify(payload) }, token),
  generateTwin: (token: string) => request<Twin>("/financial-twin/generate", { method: "PUT" }, token),
  getTwin: (token: string) => request<Twin>("/financial-twin", {}, token),
  sendSaarthiMessage: (message: string, session_id?: string, token?: string) =>
    request<SaarthiChatResponse>(
      "/saarthi/chat",
      { method: "POST", body: JSON.stringify({ message, session_id: session_id || null }) },
      token
    ),
  getSaarthiSessions: (token: string) => request<SaarthiSession[]>("/saarthi/sessions", {}, token),
  getSaarthiMessages: (session_id: string, token: string) =>
    request<SaarthiMessage[]>(`/saarthi/sessions/${session_id}/messages`, {}, token),
  createGoal: (payload: GoalCreatePayload, token: string) =>
    request<FinancialGoal>("/planning/goals", { method: "POST", body: JSON.stringify(payload) }, token),
  getGoals: (token: string) => request<FinancialGoal[]>("/planning/goals", {}, token),
  getGoalDetail: (goal_id: string, token: string) => request<FinancialGoal>(`/planning/goals/${goal_id}`, {}, token),
  addGoalProgress: (goal_id: string, amount: number, token: string) =>
    request<FinancialGoal>(`/planning/goals/${goal_id}/progress`, { method: "POST", body: JSON.stringify({ amount }) }, token),
  recalculateGoalPlan: (goal_id: string, token: string) =>
    request<FinancialGoal>(`/planning/goals/${goal_id}/recalculate`, { method: "POST" }, token),
  analyzeScamMessage: (message: string, token: string) =>
    request<ScamScan>("/scam-shield/analyze", { method: "POST", body: JSON.stringify({ message }) }, token),
  getScamHistory: (token: string) => request<ScamHistoryResponse>("/scam-shield/history", {}, token),
  getScamScanDetail: (scan_id: string, token: string) => request<ScamScan>(`/scam-shield/history/${scan_id}`, {}, token),
  deleteScamScan: (scan_id: string, token: string) =>
    request<void>(`/scam-shield/history/${scan_id}`, { method: "DELETE" }, token),
  getLearningModules: (token: string) => request<LearningModule[]>("/learn/modules", {}, token),
  getLearningModuleDetail: (module_id: string, token: string) =>
    request<LearningModule>(`/learn/modules/${module_id}`, {}, token),
  startLearningModule: (module_id: string, token: string) =>
    request<LearningModule>(`/learn/modules/${module_id}/start`, { method: "POST" }, token),
  getLearningQuiz: (module_id: string, token: string) =>
    request<QuizQuestion[]>(`/learn/modules/${module_id}/quiz`, {}, token),
  submitLearningQuiz: (module_id: string, answers: number[], token: string) =>
    request<QuizResult>(`/learn/modules/${module_id}/quiz`, { method: "POST", body: JSON.stringify({ answers }) }, token),
  getLearningProgress: (token: string) => request<LearningProgressSummary>("/learn/progress", {}, token),
  getLearningRecommendations: (token: string) =>
    request<LearningRecommendation[]>("/learn/recommendations", {}, token),
  // --- PROMPT 9: Government Scheme methods ---
  getSchemeCategories: (token?: string) => request<SchemeCategoryCount[]>("/schemes/categories", {}, token),
  getSchemeRecommendations: (token: string) => request<SchemeRecommendation[]>("/schemes/recommendations", {}, token),
  getSchemes: (category?: string, search?: string, token?: string) => {
    const params = new URLSearchParams();
    if (category) params.append("category", category);
    if (search) params.append("search", search);
    const query = params.toString() ? `?${params.toString()}` : "";
    return request<GovernmentScheme[]>(`/schemes${query}`, {}, token);
  },
  getSchemeDetail: (scheme_id: string, token?: string) => request<GovernmentScheme>(`/schemes/${scheme_id}`, {}, token),
  checkSchemeEligibility: (scheme_id: string, token: string) =>
    request<SchemeEligibility>(`/schemes/${scheme_id}/eligibility-check`, { method: "POST" }, token),
  updateSupportContext: (payload: SupportContextPayload, token: string) =>
    request<SupportContextResponse>("/profile/support-context", { method: "PUT", body: JSON.stringify(payload) }, token),
  // --- PROMPT 10: Market Intelligence methods ---
  getMarketOverview: (token?: string, forceRefresh?: boolean) =>
    request<MarketOverview>(`/market/overview${forceRefresh ? "?force_refresh=true" : ""}`, {}, token),
  getAssetDetail: (symbol: string, token?: string) => request<MarketAsset>(`/market/assets/${symbol}`, {}, token),
  refreshMarket: (token: string) => request<MarketOverview>("/market/refresh", { method: "POST" }, token),
  // --- PROMPT 11: Personalized Recommendation methods ---
  getRecommendation: (token: string) => request<PersonalizedRecommendation>("/recommendations", {}, token),
  generateRecommendation: (token: string) => request<PersonalizedRecommendation>("/recommendations/generate", { method: "POST" }, token),
  // --- PROMPT 14: System Orchestration methods ---
  getTodaysBrief: (token: string) => request<any>("/dashboard/brief", {}, token),
  getFinancialSnapshot: (token: string) => request<any>("/dashboard/snapshot", {}, token),
  getSystemHealth: () => request<any>("/system/health", {}),
};




