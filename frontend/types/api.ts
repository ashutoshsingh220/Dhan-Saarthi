export type User = { id: number; full_name: string; email: string; preferred_language: string; accessibility_mode: string };
export type AuthResult = { access_token: string; token_type: string; user: User; onboarding_complete: boolean };
export type Twin = { id: number; financial_health_score: number; risk_level: string; financial_summary: string; last_updated: string };

// --- PROMPT 8: Personalization enum types ---
export type EducationLevel =
  | "PRIMARY_OR_BELOW"
  | "SECONDARY"
  | "HIGHER_SECONDARY"
  | "DIPLOMA"
  | "UNDERGRADUATE"
  | "POSTGRADUATE"
  | "DOCTORATE"
  | "OTHER"
  | "PREFER_NOT_TO_SAY";

export type FinancialKnowledgeLevel = "BEGINNER" | "BASIC" | "INTERMEDIATE" | "ADVANCED";

export type ExplanationLevel = "SIMPLE" | "BALANCED" | "DETAILED";

export type OccupationStatus =
  | "STUDENT"
  | "SALARIED"
  | "SELF_EMPLOYED"
  | "BUSINESS_OWNER"
  | "FARMER"
  | "HOMEMAKER"
  | "RETIRED"
  | "UNEMPLOYED"
  | "OTHER"
  | "PREFER_NOT_TO_SAY";

export type PersonalizationSummary = {
  derived_age?: number | null;
  education_level?: EducationLevel | null;
  financial_knowledge_level?: FinancialKnowledgeLevel | null;
  preferred_explanation_level?: ExplanationLevel | null;
  occupation_status?: OccupationStatus | null;
};

export type ProfilePayload = {
  age: number;
  gender?: string;
  occupation: string;
  city?: string;
  monthly_income: number;
  monthly_expenses: number;
  savings: number;
  total_savings?: number;
  monthly_savings?: number;
  financial_goal: string;
  risk_preference: "low" | "moderate" | "high";
  preferred_language: string;
  accessibility_mode: "standard" | "voice_first";

  // Legal Consent & Privacy fields
  consent_given?: boolean;
  consent_given_at?: string | null;

  // PROMPT 8 personalization fields (all optional)
  date_of_birth?: string | null;
  education_level?: EducationLevel | null;
  financial_knowledge_level?: FinancialKnowledgeLevel | null;
  preferred_explanation_level?: ExplanationLevel | null;
  occupation_status?: OccupationStatus | null;
};


export type ProfileResponse = ProfilePayload & {
  id: number;
  user_id: number;
  created_at: string;
  updated_at: string;
  derived_age?: number | null;
};


export type SaarthiChatResponse = { session_id: string; message_id: number; response: string; created_at: string };
export type SaarthiSession = { session_id: string; title: string; updated_at: string };
export type SaarthiMessage = { id: number; role: "user" | "model"; content: string; created_at: string };

export type FinancialPlanMilestone = {
  id: number;
  title: string;
  milestone_date: string;
  target_amount: number;
  status: "pending" | "completed";
  completed_at?: string;
};

export type FinancialPlan = {
  id: number;
  monthly_required: number;
  recommended_monthly_contribution: number;
  available_monthly_capacity: number;
  feasibility_status: "FEASIBLE" | "TIGHT" | "AT_RISK";
  feasibility_percentage: number;
  estimated_completion_date: string;
  recommendation_text: string;
  milestones: FinancialPlanMilestone[];
};

export type FinancialGoal = {
  id: string;
  name: string;
  category: string;
  target_amount: number;
  current_amount: number;
  target_date: string;
  status: "active" | "completed" | "paused";
  created_at: string;
  updated_at: string;
  plan?: FinancialPlan;
};

export type GoalCreatePayload = {
  name: string;
  category: string;
  target_amount: number;
  current_amount: number;
  target_date: string;
};

export type ScamIndicator = {
  indicator_type: string;
  matched_text: string;
  severity: "low" | "medium" | "high" | "critical";
  points: number;
};

export type ScamScan = {
  id: string;
  input_text: string;
  input_type?: string;
  extracted_text?: string;
  risk_score: number;
  risk_level: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  summary: string;
  recommended_actions: string[];
  retrieved_evidence?: {
    id: string;
    category: string;
    title: string;
    description: string;
    example: string;
    risk_indicators: string[];
    recommended_action: string;
    is_scam: boolean;
  }[];
  indicators: ScamIndicator[];
  created_at: string;
};

export type ScamAnalyzePayload = {
  message: string;
};

export type ScamHistoryResponse = {
  scans: ScamScan[];
  total_count: number;
};

export type LearningLessonContent = {
  sections: { heading: string; body: string }[];
  key_takeaways: string[];
};

export type LearningModule = {
  module_id: string;
  title: string;
  description: string;
  category: string;
  difficulty: "Beginner" | "Intermediate" | "Advanced";
  estimated_minutes: number;
  lesson_content: LearningLessonContent;
  status: "NOT_STARTED" | "IN_PROGRESS" | "COMPLETED";
  completed_at?: string | null;
  quiz_score?: number | null;
};

export type LearningProgressSummary = {
  total_modules: number;
  completed_modules: number;
  in_progress_modules: number;
  completion_percentage: number;
};

export type LearningRecommendation = {
  module_id: string;
  title: string;
  description: string;
  reason: string;
  estimated_minutes: number;
};

export type QuizQuestion = {
  id: string;
  question: string;
  options: string[];
};

export type QuizResult = {
  score_percentage: number;
  correct_count: number;
  total_questions: number;
  status: "NOT_STARTED" | "IN_PROGRESS" | "COMPLETED";
  feedback: string;
};

// --- PROMPT 9: Government Scheme Discovery types ---
export type GovernmentScheme = {
  id: number;
  scheme_id: string;
  name: string;
  short_name: string;
  category: string;
  tags: string[];
  target_groups: string;
  description: string;
  benefits_summary: string;
  benefit_type: string;
  official_authority: string;
  official_url: string;
  application_url?: string | null;
  status: string;
  geographic_scope: string;
  states_supported: string[];
  eligibility_rules: Record<string, any>;
  required_documents: string[];
  how_to_apply: string[];
  important_notes?: string | null;
  source_last_verified_at: string;
};

export type SchemeCategoryCount = {
  category_id: string;
  category_name: string;
  count: number;
};

export type SchemeEligibility = {
  scheme_id: string;
  scheme_name: string;
  relevance_status: "HIGHLY_RELEVANT" | "RELEVANT" | "EXPLORE" | "NEEDS_MORE_INFORMATION";
  eligibility_status: "LIKELY_RELEVANT" | "POTENTIALLY_ELIGIBLE" | "NEEDS_MORE_INFORMATION" | "NOT_CURRENTLY_MATCHED";
  relevance_score: number;
  match_reasons: string[];
  missing_information: string[];
  disclaimer: string;
  official_url: string;
};

export type SchemeRecommendation = {
  scheme: GovernmentScheme;
  relevance_rank: "HIGHLY_RELEVANT" | "RELEVANT" | "EXPLORE" | "NEEDS_MORE_INFORMATION";
  relevance_score: number;
  why_recommended: string;
  what_to_verify_next: string[];
  official_source_url: string;
};

export type SupportContextPayload = {
  state?: string | null;
  district?: string | null;
  rural_or_urban?: "RURAL" | "URBAN" | "SEMI_URBAN" | null;
  farming_interest?: boolean | null;
  business_interest?: boolean | null;
  farm_activity?: string | null;
  business_stage?: string | null;
  business_sector?: string | null;
  business_registration_status?: string | null;
};

export type SupportContextResponse = {
  state?: string | null;
  district?: string | null;
  rural_or_urban?: string | null;
  farming_interest: boolean;
  business_interest: boolean;
  farm_activity?: string | null;
  business_stage?: string | null;
  business_sector?: string | null;
  business_registration_status?: string | null;
};

// --- PROMPT 10: Market Intelligence types ---
export type DirectionType = "UP" | "DOWN" | "FLAT" | "UNAVAILABLE";
export type FreshnessType = "LIVE" | "CACHED" | "STALE" | "UNAVAILABLE";
export type PulseType = "POSITIVE" | "NEGATIVE" | "MIXED" | "CALM" | "UNAVAILABLE";

export type MarketAsset = {
  symbol: string;
  display_name: string;
  asset_type: string;
  current_price: number;
  currency: string;
  absolute_change: number;
  percentage_change: number;
  direction: DirectionType;
  market_status: "OPEN" | "CLOSED" | "PRE_MARKET" | "POST_MARKET" | "UNKNOWN";
  updated_at: string;
  source: string;
};

export type MarketInsight = {
  title: string;
  observation: string;
  educational_note: string;
};

export type MarketOverview = {
  market_pulse: PulseType;
  pulse_summary: string;
  freshness: FreshnessType;
  is_stale: boolean;
  fetched_at: string;
  source: string;
  tracked_assets: MarketAsset[];
  insights: MarketInsight[];
  explanation_level: "SIMPLE" | "BALANCED" | "DETAILED";
  disclaimer: string;
};

// --- PROMPT 11: Personalized Financial Recommendation types ---
export type PriorityItem = {
  title: string;
  category: string;
  priority_level: "HIGH" | "MEDIUM" | "LOW";
  reason: string;
  action_guidance: string;
  data_basis: string[];
};

export type AllocationGuidanceItem = {
  category: string;
  suggested_range_min: number;
  suggested_range_max: number;
  reason: string;
};

export type GoalConsiderationItem = {
  goal_id: string;
  goal_name: string;
  feasibility_status: string;
  monthly_required: number;
  guidance_note: string;
};

export type EmergencyBufferAnalysis = {
  monthly_expenses: number;
  current_savings: number;
  coverage_months: number;
  status: "CRITICAL_BUFFER" | "LOW_BUFFER" | "MODERATE_BUFFER" | "STRONG_BUFFER" | "INSUFFICIENT_DATA";
  target_recommended_savings: number;
  explanation: string;
};

export type PersonalizedRecommendation = {
  recommendation_id: string;
  generated_at: string;
  data_completeness: "COMPLETE" | "PARTIAL" | "INSUFFICIENT";
  data_completeness_note: string;
  recommendation_status: string;
  monthly_capacity: {
    income: number;
    expenses: number;
    surplus: number;
    unallocated_flexibility: number;
  };
  top_priority: PriorityItem;
  financial_priorities: PriorityItem[];
  emergency_buffer_analysis: EmergencyBufferAnalysis;
  allocation_guidance: AllocationGuidanceItem[];
  goal_considerations: GoalConsiderationItem[];
  market_context_summary: {
    pulse: string;
    freshness: string;
    source: string;
    warning_note: string;
  };
  risk_profile: {
    preference: string;
    guidance_note: string;
  };
  educational_notes: string[];
  disclaimer: string;
};



