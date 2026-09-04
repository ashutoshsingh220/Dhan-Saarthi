<p align="center">
  <img src="frontend/assets/branding/dhan-saarthi-logo.png" alt="Dhan Saarthi Official Logo" width="360"/>
</p>

# ⚡ Dhan Saarthi (धन सारथी)

> **"Financial clarity for everyone. Deterministic intelligence. AI empathy."**

**Dhan Saarthi** is an end-to-end agentic financial companion system that unifies authoritative deterministic financial calculations, multi-modal scam detection (OCR + RAG), personalized government scheme discovery, and live market intelligence into a single, accessible mobile experience. It is designed to bridge the financial literacy gap across India with native **Multilingual Support**:

1. **English (`en`)**
2. **हिन्दी — Hindi (`hi`)**
3. **Hinglish (`hi-en`)**

---

## 🏛️ System Component Separation

To maintain architectural clarity and prevent AI hallucinations in financial math, our codebase enforces a strict separation between deterministic engines and generative AI orchestrators:

| Component | Layer | Verified Implementation in Repository |
| :--- | :--- | :--- |
| **FINANCIAL TWIN ENGINE** | Core Financial Logic | `backend/app/services/twin_service.py`<br>Calculates a transparent Financial Health Score (0-100) using deterministic algorithms, evaluating surplus ratios, liquid savings buffer months, and expense ratios. |
| **SCAM SHIELD (OCR + RAG)** | Security & Fraud Prevention | `backend/app/services/scam_service.py`, `backend/app/api/routes.py`<br>Ingests user screenshots, extracts text via optimized OpenCV + PyTesseract pipelines, and validates against a RAG knowledge base of banking alerts using Gemini vectors. |
| **SCHEME DISCOVERY** | Government Policy Engine | `backend/app/services/scheme_service.py`<br>Rule-based evaluation matching user demographics (urban/rural, farmer, gender) to 10+ verified government schemes (PM-KISAN, PMMY Mudra, etc.). |
| **SAARTHI AI ORCHESTRATOR** | Conversational Intelligence | `backend/app/services/context_builder.py`, `backend/app/providers/gemini_client.py`<br>Orchestrates the LLM context by injecting the user's live Financial Twin state, ensuring the AI companion gives hyper-personalized, mathematically grounded advice. |
| **ACCESSIBILITY LAYER** | Voice & Visual UI | `frontend/context/AccessibilityContext.tsx`, `frontend/services/voice/speechSynthesis.ts`<br>5 distinctive accessibility profiles (`VISUAL_ASSIST`, `LOW_LITERACY`, `ELDERLY`, etc.), dynamic font scaling, and Web Speech API polyfills for voice-first navigation. |
| **LIVE MARKET PULSE** | Market Intelligence | `backend/app/services/market_intelligence_service.py`<br>Fetches live NIFTY 50, SENSEX, and GOLD data with 300s TTL caching and robust fallback mechanisms to prevent rate-limit failures. |

---

## 📐 Pipeline Architecture

```text
Dhan Saarthi — End-to-End Intelligence Pipeline

                         ┌───────────────────────────┐
                         │       USER / BUYER        │
                         │                           │
                         │ "Is this SMS asking for   │
                         │  my UPI PIN a scam?"      │
                         │    [+ Uploads Image]      │
                         └─────────────┬─────────────┘
                                       │
                                       │ (1) Request + Image Payload
                                       ▼
    ╔═════════════════════════════════════════════════════════════════╗
    ║                  FASTAPI BACKEND ORCHESTRATOR                   ║
    ║                                                                 ║
    ║  • JWT Authentication Validation                                ║
    ║  • Rate Limiting (60 req / min)                                 ║
    ║  • Request Routing                                              ║
    ╚═════════════════════════════════════════════════════════════════╝
                                       │
               ┌───────────────────────┼───────────────────────┐
               │                       │                       │
               ▼ (2a) Scam Check       ▼ (2b) Twin Sync        ▼ (2c) Market Data
     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
     │   SCAM SHIELD   │     │ FINANCIAL TWIN  │     │  MARKET ENGINE  │
     │  (OCR + RAG)    │     │  (Score 0-100)  │     │   (Live Data)   │
     └────────┬────────┘     └────────┬────────┘     └────────┬────────┘
              │                       │                       │
              └───────────────────────┼───────────────────────┘
                                      │
                                      │ (3) Deterministic Data Aggregation
                                      ▼
    ╔═════════════════════════════════════════════════════════════════╗
    ║                   MASTER CONTEXT BUILDER                        ║
    ║                                                                 ║
    ║   Aggregated State:                                             ║
    ║   • Twin Status: 65/100 (Good Progress), 1.5mo Buffer           ║
    ║   • Scam Output: [HIGH RISK] Suspicious domain matched          ║
    ║   • User Profile: Visual Assist Mode, Language: Hindi           ║
    ║                                                                 ║
    ║   ─── SERVER-SIDE AI GUARDRAIL INJECTION ─────────────────────  ║
    ║   Rule 1: Never invent numbers, strictly use Twin data.         ║
    ║   Rule 2: Respond in the user's preferred language natively.    ║
    ╚═════════════════════════════════════════════════════════════════╝
                                      │
                                      │ (4) Hydrated Context Payload
                                      ▼
    ╔═════════════════════════════════════════════════════════════════╗
    ║                  GEMINI 1.5 PRO / FLASH ENGINE                  ║
    ║                                                                 ║
    ║  • Generates empathetic, actionable response based ONLY on      ║
    ║    the deterministic context provided.                          ║
    ╚═════════════════════════════════════════════════════════════════╝
                                      │
                                      │ (5) Response Stream
                                      ▼
                         ┌───────────────────────────┐
                         │   CLIENT PRESENTATION     │
                         │                           │
                         │ • Accessible UI Render    │
                         │ • Voice Synthesis (TTS)   │
                         └───────────────────────────┘
```

---

## 🔥 Core Capabilities & Technical Highlights

### 1. 🛡️ Scam Shield (Advanced Pipeline)
- **Screenshot OCR:** We utilize an optimized OpenCV pipeline (Grayscale, CLAHE Contrast, Denoising, Otsu Thresholding) alongside PyTesseract to accurately extract text from low-quality user screenshots.
- **RAG Knowledge Base:** Employs Gemini vectors (`text-embedding-004`) to match extracted text dynamically against an in-memory knowledge base of verified legitimate banking alerts and known phishing templates.

### 2. 📉 Scalable, High-Performance Infrastructure
- **Query Optimization:** Strict SQLAlchemy `joinedload()` implementation prevents N+1 explosive database queries on heavily relational data.
- **Pagination & Throttling:** API is secured with IP-based rate limiting and cursor-based pagination on heavy data pipelines (like chat history).
- **Frontend Memory Integrity:** The React Native UI utilizes strict `FlatList` component architectures for rendering UI grids, preserving device memory across lower-end mobile hardware.

### 3. 🔒 Mandatory Data Privacy & Security
The onboarding pipeline is strictly gated by an explicit consent and legal privacy agreement before processing user demographics. 

---

## 🛠️ Tech Stack

| Component | Technology | Description |
|---|---|---|
| **Mobile Frontend** | React Native (Expo SDK 52) | Cross-platform iOS, Android & Web app |
| **Language** | TypeScript | Strict Mode enabled |
| **Routing** | Expo Router | File-based typed routes |
| **Backend API** | Python 3.11 & FastAPI | High-performance async REST framework |
| **Database** | PostgreSQL / SQLite | SQLAlchemy 2.0 ORM |
| **AI LLM & Embeddings**| Google Gemini Pro | Orchestration & RAG retrieval |
| **Testing** | Pytest | Full backend unit/integration testing suite |

---

## 🚀 Quick Start & Local Setup

### Backend Setup
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Start Backend API Server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*API Documentation will be live at `http://localhost:8000/docs`.*

### Frontend Setup
```powershell
cd ../frontend
npm install

# Start Expo App
npx expo start
```
*Scan QR code via Expo Go App or press `w` to run on Web.*
