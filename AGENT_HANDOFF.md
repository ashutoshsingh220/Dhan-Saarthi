# Agent Handoff Instructions

## Current State

Prompt 8A (Fix User Financial Profile + Universal Ask Saarthi Integration) is **COMPLETED AND VERIFIED**.

## What Was Implemented in Prompt 8A

1. **Age-Only Profile Onboarding & Date of Birth Removal**:
   - Removed DOB from active onboarding flow.
   - Profile collects and validates `Age` (numeric, 18-120).
   - Stored in `user_profiles.age`. `user_profiles.date_of_birth` remains as nullable for backward compatibility.
2. **Total Savings vs. Monthly Savings Separation**:
   - `UserProfile` model and Pydantic schemas updated with `total_savings` (accumulated savings to date) and `monthly_savings` (typical monthly savings).
   - Onboarding (`onboarding.tsx`) and Profile Settings (`more.tsx`) collect and display both fields distinctly.
3. **Financial Twin Score Engine Calibration**:
   - Refactored `calculate_initial_twin` in `backend/app/services/twin.py`.
   - Liquid emergency buffer months computed from `total_savings / monthly_expenses`.
   - Ongoing cashflow rating computed from `monthly_savings` and `surplus`.
4. **Smart Goal Planning Protection**:
   - Smart Planning treats `total_savings` as background context and never auto-allocates accumulated savings to goal balances.
5. **Universal Ask Saarthi Handoff & Auto-Send**:
   - Implemented standardized `initialPrompt` search parameter across all feature modules (`planning.tsx`, `scam-shield.tsx`, `schemes.tsx`, `learn-detail.tsx`, `recommendations.tsx`, `market-intelligence.tsx`, `index.tsx`).
   - Added `consumedPromptRef` to `frontend/app/(tabs)/saarthi.tsx` to automatically trigger contextual chat queries upon navigation while preventing duplicate auto-sends on component rerenders.

## Verification Performed

- Pytest test suite: `105/105 PASSED` (100%)
- TypeScript check (`npx tsc --noEmit`): `0 ERRORS`
- Expo config validation: `SDK 52 VALID`
- Live E2E test: `prompt8a_live_test.py` (`11/11 PASSED`)
