# Dhan Saarthi — Project Specification

## Purpose and problem

Dhan Saarthi is an AI-powered personal financial life companion for people who need clearer, more accessible, and more personalized help managing their financial lives. A hackathon prototype must demonstrate a connected end-to-end journey, rather than a collection of static financial-tool screens.

## Core concept: Financial Twin

The Financial Twin is the central intelligence layer. It represents a user's financial profile from their income, expenses, savings, investments, goals, risk profile, and financial behaviour/patterns. It will power personalized explanations, insights, guidance, planning support, learning, safety, and accessibility across the product.

## Capability domains

The project has exactly these six major domains:

1. **Financial Twin** — income/expense profiling, goal mapping, risk assessment, financial health score, and behavioural insights.
2. **AI Saarthi** — personalized, context-aware guidance through voice and text, multilingual interaction, and clear explanations.
3. **Financial Literacy** — simple AI-driven explanations, contextual walkthroughs, tips, and personalized learning.
4. **Smart Planning** — goal tracking, savings/spending analysis, life-event planning, and personalized recommendations.
5. **Scam Shield** — scam/fraud detection, QR/document verification workflows, risk scoring, indicators, alerts, explanations, and safe-action guidance.
6. **Inclusive Finance** — voice-first interaction, regional languages, accessibility, simple explanations, and community-oriented support.

No additional major capability domains may be introduced.

## Intended user journey

App launch → branding → experience selection (standard or voice-first) → language preference → privacy and consent → login/demo authentication → financial-profile onboarding → financial review → Financial Twin generation → Financial Twin dashboard → personalized exploration of the six capability domains.

## Approved technology stack

- Frontend: React Native, Expo, TypeScript
- Backend: Python, FastAPI, Uvicorn, Pydantic, SQLAlchemy
- Database: PostgreSQL
- AI/GenAI: Gemini API through a backend-owned orchestration layer
- ML: scikit-learn and XGBoost only where genuinely useful
- OCR: OpenCV and Tesseract OCR
- Speech: Faster Whisper, Silero VAD where needed, Piper TTS
- Security: JWT, secure REST APIs, password hashing, environment-variable secrets
- Development: VS Code, Git, GitHub

## Explicit non-goals for this foundation

- No Firebase or Firebase Authentication.
- No Flutter or second backend framework.
- No full Financial Twin, Scam Shield, speech, OCR, Gemini, or ML implementation in Prompt 0.
- No hard-coded authenticated user details in frontend screens.
- No scattered database access in API route handlers.
- No unrelated major product modules.

## Hackathon priorities

Build reliable vertical feature slices that work from UI through API and persistence to rendered output. Prioritize a coherent, demonstrable user journey; local frontend/backend connectivity; clear user value; and honest, verifiable implementation status.
