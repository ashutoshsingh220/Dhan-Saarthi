# API Contract

## Status

Prompts 1, 2, 3, 4, 5, 6, and 7 establish the contracts below. The backend uses `/api` prefix.

## Conventions

- Base path: `/api`
- Implemented endpoint prefix: `/api`
- Content type: `application/json` for JSON request/response bodies.
- Naming: JSON uses `snake_case`, matching Pydantic models.
- Successful responses return endpoint-specific JSON objects or arrays with HTTP 2xx status codes.
- Protected endpoints use `Authorization: Bearer <access_token>`.
- Error body convention: `{"detail": "Human-readable explanation"}`.

## Implemented endpoints

### `GET /health`
- Purpose: report API server health.
- Success response (`200 OK`): `{"status": "ok"}`.

### Authentication
- `POST /api/auth/register` — `{full_name, email, password}` -> `201` `{access_token, token_type, user, onboarding_complete}`; duplicate email returns `409`.
- `POST /api/auth/login` — `{email, password}` -> `200` token/session payload; invalid credentials return `401`.
- `GET /api/auth/me` — bearer-protected. Returns current user object and `onboarding_complete`.

### Profile
- `GET /api/profile` — bearer-protected. Returns user profile or `404` before onboarding.
- `PUT /api/profile` — bearer-protected. Upserts profile fields including `age` (18-120), `monthly_income`, `monthly_expenses`, `monthly_savings`, `total_savings`, `financial_goal`, `risk_preference`, `preferred_language` (`"English"` or `"Hindi"`).


### Financial Twin
- `GET /api/financial-twin` — bearer-protected. Returns saved prototype twin or `404`.
- `PUT /api/financial-twin/generate` — bearer-protected. Creates or refreshes deterministic prototype score.

### AI Saarthi Chat (Prompts 3 & 7 Multilingual Aware)
- `POST /api/saarthi/chat` — bearer-protected. `{ "message": "string", "session_id": "optional UUID" }`. ContextBuilder includes `preferred_language` (`"English"` or `"Hindi"`) and responds in English or natural Hindi / Hinglish while preserving exact calculated metrics. Returns `200` `{ "session_id": "UUID", "message_id": 12, "response": "string", "created_at": "ISO timestamp" }`.
- `POST /api/saarthi/chat/stream` — bearer-protected. `{ "message": "string", "session_id": "optional UUID" }`. High-performance SSE streaming assistant response. Returns HTTP 200 `text/event-stream` yielding text chunks and persisting full conversation into database.
- `GET /api/saarthi/sessions` — bearer-protected. Returns authenticated user's chat sessions.

- `GET /api/saarthi/sessions/{session_id}/messages` — bearer-protected. Returns message history for an owned session (`403/404` if not owned).

### Smart Financial Planning (Prompt 4)
- `POST /api/planning/goals` — bearer-protected. `{ "name": "string", "category": "emergency_fund|education|travel|home|vehicle|investment|other", "target_amount": 100000, "current_amount": 10000, "target_date": "YYYY-MM-DD" }`. Returns `201` `GoalDetailResponse`.
- `GET /api/planning/goals` — bearer-protected. Returns array of `GoalDetailResponse` for authenticated user.
- `GET /api/planning/goals/{goal_id}` — bearer-protected. Returns single goal detail (`403/404` if not owned).
- `PUT /api/planning/goals/{goal_id}` — bearer-protected. Updates goal details and recalculates plan (`403/404` if not owned).
- `POST /api/planning/goals/{goal_id}/progress` — bearer-protected. `{ "amount": 5000 }`. Adds progress contribution (`403/404` if not owned).
- `POST /api/planning/goals/{goal_id}/recalculate` — bearer-protected. Recalculates plan against current Financial Twin.

### Scam Shield (Prompt 5)
- `POST /api/scam-shield/analyze` — bearer-protected. `{ "message": "string (min 5 chars)" }`. Returns `201` `ScamScanResponse` with deterministic `risk_score`, `risk_level`, `summary`, `indicators`, and `recommended_actions`.
- `GET /api/scam-shield/history` — bearer-protected. Returns `ScamHistoryResponse` containing array of authenticated user's scans (newest first).
- `GET /api/scam-shield/history/{scan_id}` — bearer-protected. Returns single `ScamScanResponse` by UUID (`403/404` if not owned).
- `DELETE /api/scam-shield/history/{scan_id}` — bearer-protected. Deletes single scam scan record (`204 No Content`, `403/404` if not owned).

### Financial Literacy Engine (Prompt 6)
- `GET /api/learn/modules` — bearer-protected. Returns array of `LearningModuleResponse` with user's progress status (`NOT_STARTED`, `IN_PROGRESS`, `COMPLETED`).
- `GET /api/learn/modules/{module_id}` — bearer-protected. Returns module details and lesson content.
- `POST /api/learn/modules/{module_id}/start` — bearer-protected. Marks module status as `IN_PROGRESS`.
- `GET /api/learn/modules/{module_id}/quiz` — bearer-protected. Returns list of `QuizQuestionPublic` (correct answers hidden).
- `POST /api/learn/modules/{module_id}/quiz` — bearer-protected. `{ "answers": [1, 1, 2] }`. Evaluates answers, records score, updates status to `COMPLETED` if $\ge 60\%$, and returns `QuizResultResponse`.
- `GET /api/learn/progress` — bearer-protected. Returns `LearningProgressSummaryResponse` (`total_modules`, `completed_modules`, `in_progress_modules`, `completion_percentage`).
- `GET /api/learn/recommendations` — bearer-protected. Returns array of `LearningRecommendationResponse`.

### Government Scheme Support (Prompt 9)
- `GET /api/schemes/categories` — Returns array of `SchemeCategoryCount` with scheme counts per category.
- `GET /api/schemes/recommendations` — bearer-protected. Returns array of `SchemeRecommendationResponse` ranked into relevance tiers.
- `GET /api/schemes` — Catalog listing with optional `category` and `search` query parameters.
- `GET /api/schemes/{scheme_id}` — Returns `GovernmentSchemePublic` for a scheme by UUID or ID.
- `POST /api/schemes/{scheme_id}/eligibility-check` — bearer-protected. Evaluates deterministic eligibility status and match reasons.
- `PUT /api/profile/support-context` — bearer-protected. Updates support profile (`state`, `district`, `rural_or_urban`, `farming_interest`, `business_interest`, `farm_activity`, `business_stage`, `business_sector`).

### Live Market Intelligence (Prompt 10)
- `GET /api/market/overview` — Optional bearer auth. Returns `MarketOverviewResponse` containing `market_pulse`, `pulse_summary`, `freshness` state (`LIVE`, `CACHED`, `STALE`, `UNAVAILABLE`), `source`, `tracked_assets` (NIFTY 50, SENSEX, GOLD, SILVER, USD/INR), `insights`, and `disclaimer`.
- `GET /api/market/assets/{symbol}` — Optional bearer auth. Returns `MarketAssetSchema` for a specific asset symbol (`NIFTY50`, `SENSEX`, `GOLD`, `SILVER`, `USDINR`).
- `POST /api/market/refresh` — bearer-protected. Forces market snapshot refresh and returns fresh `MarketOverviewResponse`.

### Personalized Financial Recommendations (Prompt 11)
- `GET /api/recommendations` — bearer-protected. Returns latest `PersonalizedRecommendationResponse` containing `data_completeness`, `top_priority`, `financial_priorities`, `emergency_buffer_analysis`, `monthly_capacity`, `allocation_guidance` ranges, `goal_considerations`, `market_context_summary`, `risk_profile`, `educational_notes`, and `disclaimer`.
- `POST /api/recommendations/generate` — bearer-protected. Generates fresh deterministic recommendation snapshot and returns `PersonalizedRecommendationResponse`.

### System Integration & Orchestration (Prompt 14)
- `GET /api/dashboard/brief` — bearer-protected. Returns Today's Financial Brief (`greeting`, `summary_sentence`, `bullet_points`, `top_priority`, `explanation_level`, `accessibility_profile`, `language`).
- `GET /api/dashboard/snapshot` — bearer-protected. Returns unified `UserFinancialIntelligenceSnapshot` (`generated_at`, `profile_completeness`, `financial_twin`, `top_financial_priority`, `recommendations`, `goals`, `market_context`, `government_support`, `literacy`, `scam_safety`, `accessibility`, `personalization`).
- `GET /api/system/health` — Returns system diagnostic status (`status`, `database`, `gemini`, `market_provider`, `market_cache`, `voice_mode`, `timestamp`).



