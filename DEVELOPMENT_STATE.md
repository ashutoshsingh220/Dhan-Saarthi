# Development State

## Current phase

**PROMPT 8A — FIX USER FINANCIAL PROFILE + UNIVERSAL ASK SAARTHI INTEGRATION (COMPLETED AND VERIFIED)**

## Completed work

- **Task A (Age Only & DOB Removal)**: Removed Date of Birth from active onboarding flow. User onboarding and profile settings now collect and validate `Age` (numeric, 18-120). Database column `user_profiles.date_of_birth` remains for legacy compatibility, but age is stored directly in `user_profiles.age`.
- **Task B (Total Savings vs. Monthly Savings)**: Extended `UserProfile` model and profile schemas with `total_savings` (accumulated wealth so far) and `monthly_savings` (typical monthly savings). Added `total_savings` and `monthly_savings` inputs to `onboarding.tsx` and `more.tsx`.
- **Task C (Financial Twin Score Engine Calibration)**: Refactored `calculate_initial_twin` in `backend/app/services/twin.py` to calculate liquid emergency buffer months from `total_savings / monthly_expenses` and evaluate ongoing cashflow capacity from `monthly_savings` / `surplus`.
- **Task D (Smart Planning Isolation)**: Confirmed Smart Goal Planning treats `total_savings` as background context and never auto-allocates accumulated savings to goal balances.
- **Task E (Universal Ask Saarthi Handoff)**: Implemented standardized `initialPrompt` handoff across all 6 feature domains (Smart Planning, Scam Shield, Government Schemes, Financial Literacy, Recommendations, and Home Dashboard).
- **Auto-Send & Duplicate Prevention**: Implemented `consumedPromptRef` in `frontend/app/(tabs)/saarthi.tsx` to automatically trigger chat queries upon navigation while preventing duplicate sends on component rerenders.
- **Automated Verification**:
  - Live E2E script: `python prompt8a_live_test.py` (`11/11 PASSED`).
  - Full backend test suite: `pytest tests/` (`105/105 PASSED`).
  - Frontend TypeScript compiler: `npx tsc --noEmit` (`0 ERRORS`).
  - Expo configuration validation: (`SDK 52 VALID`).

## Work currently in progress

None; Prompt 8A is fully implemented and verified.

## Verified working components

- User Financial Profile: Age (18-120), Monthly Income, Monthly Expenses, Monthly Savings, Total Savings, Primary Goal, Risk Preference.
- Financial Twin: Deterministic score (0-100), risk level, liquid emergency buffer months based on Total Savings.
- Universal Ask Saarthi: One real AI Saarthi 24/7 chat screen with contextual prompt handoff and duplicate prevention across all modules.
- Backend Pytest test suite: `105/105 PASSED`.
- Live E2E test script: `python prompt8a_live_test.py` (`11/11 PASSED`).
- Frontend compilation: `npx tsc --noEmit` (`0 ERRORS`).
