---
name: dhan-saarthi-development
description: Operational rules, technical standards, layout guidelines, and prompt milestones for continuing development on Dhan Saarthi.
---

# Dhan Saarthi Development Skill

## Overview

This skill defines the locked architecture, development workflow, and verified milestone state of the **Dhan Saarthi** application — an AI-powered financial companion built around a **Financial Twin**.

## Active Workspace Root
`D:\projects\Dhan_Saarthi\Saarthi`

## Locked Stack (NON-NEGOTIABLE)

- **Frontend**: React Native, Expo SDK 52, TypeScript, Expo Router (file-based navigation in `app/`), `expo-secure-store`, `expo-speech`.
- **Backend**: Python 3.11, FastAPI, Uvicorn, SQLAlchemy 2.0.
- **Database**: PostgreSQL (production/local), SQLite (pytest isolation).
- **Authentication**: Backend JWT (`python-jose`, `passlib[bcrypt]`).
- **AI Provider**: Google Gemini API via official `google-genai` SDK (backend-only `GEMINI_API_KEY`).
- **Prohibited Tech**: Firebase, Flutter, raw SQL string queries, client-side auth bypasses, client-calculated financial metrics or quiz scores.

## Verified Milestone Progress

- **Prompt 1 (Verified Complete)**: FastAPI foundation, PostgreSQL schemas (`users`, `user_profiles`, `financial_twins`), JWT auth, profile onboarding, deterministic financial health score generator.
- **Prompt 2 (Verified Complete)**: Expo Router shell, 4 bottom tabs (`Home`, `Saarthi`, `Learn`, `More`), Home Dashboard, Financial Twin Detail View, 6 capability domain entry points, session restoration.
- **Prompt 3 (Verified Complete)**: AI Saarthi chat backend provider (`GeminiClient`), financial context builder (`ContextBuilder`), conversation memory models (`ChatSession`, `ChatMessage`), session ownership isolation (`403/404`), interactive React Native AI chat UI (`app/(tabs)/saarthi.tsx`).
- **Prompt 4 (Verified Complete)**: Smart Financial Planning (Goal-based deterministic planning engine, `FinancialGoal`, `FinancialPlan`, `FinancialPlanMilestone` models, CRUD & progress APIs, feasibility classification (`FEASIBLE`, `TIGHT`, `AT_RISK`), AI Saarthi plan explanation, interactive Smart Planning screen `app/domain/planning.tsx`).
- **Prompt 5 (Verified Complete)**: Scam Shield (Deterministic rule-based scam detection engine, `ScamScan`, `ScamIndicator` models, risk scoring [0-100], risk levels [`LOW`, `MODERATE`, `HIGH`, `CRITICAL`], multi-indicator escalation bonus, false positive controls, deterministic recommendations, APIs [`/api/scam-shield/analyze`, `/history`, `/history/{id}`], AI Saarthi scan explanation, interactive Scam Shield screen `app/domain/scam-shield.tsx`).
- **Prompt 6 (Verified Complete)**: Financial Literacy Engine (Idempotent 6-topic catalogue seeding, `LearningModule`, `UserLearningProgress` models, deterministic personalized recommendation engine, backend-evaluated multiple choice quiz engine with hidden answers, progress percentage tracking, APIs [`/api/learn/modules`, `/modules/{id}`, `/start`, `/quiz`, `/progress`, `/recommendations`], AI Saarthi concept explanation integration, interactive Learn screen `app/(tabs)/learn.tsx` & `app/domain/learn-detail.tsx`).
- **Prompt 7 (Verified Complete)**: Multilingual Support, Accessibility Foundation & Basic Voice Interaction (Centralized i18n translation architecture `i18n/LanguageContext.tsx` supporting English & Hindi, persistent `user_language` & `voice_assistance_enabled` storage, backend profile language sync, Web Speech API & speech sample shortcut Voice Input component `components/VoiceInput.tsx`, Text-To-Speech audio output using `expo-speech` with 🔊 Listen / ⏹ Stop controls on AI chat bubbles, voice assistance toggle & language switcher in `app/(tabs)/more.tsx`, explicit React Native accessibility properties `accessibilityLabel`, `accessibilityHint`, `accessibilityRole`, and high-contrast color-independent visual badges).
- **Prompt 14 (Verified Complete)**: Full System Integration, End-to-End Orchestration & Production Readiness (`UserFinancialIntelligenceService`, `FinancialPriorityOrchestrator`, 13-tier Master Context Orchestration with 15,000 char budget cap, Intelligence Dashboard, system health API).
- **Prompt 8A (Verified Complete)**: Fix User Financial Profile + Universal Ask Saarthi Integration (DOB removed from active onboarding; Age 18-120 used; `total_savings` & `monthly_savings` tracked separately; Financial Twin emergency buffer calculated from Total Savings; Smart Planning goal current amount isolated; Universal Ask Saarthi contextual handoff using `initialPrompt` across all 6 domains with `consumedPromptRef` duplicate prevention).

## Current Test Status & Verification Commands

- Backend pytest suite: `python -m pytest tests/ -v` (`105/105 PASSED`)
- Frontend TypeScript check: `npx tsc --noEmit` (`0 ERRORS`)
- Expo configuration: `npx expo config --json` (`VALID SDK 52`)
- E2E Live Verification: `python prompt8a_live_test.py` (`11/11 PASSED`)

## Next Recommended Milestone

**PROMPT 8B / NEXT PROMPT STEP**
