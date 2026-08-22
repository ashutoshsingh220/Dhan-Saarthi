# Architecture

## Frontend

`frontend/` will contain one React Native + Expo + TypeScript app. Screens must call a centralized API client; API URLs must never be embedded throughout UI screens. State, form validation, shared UI components, services, hooks, and types will be organized within the frontend project after initialization.

The backend URL is configured through an Expo public environment variable. A physical device must use the development machine's LAN IP or another reachable host—not `localhost`; Android emulator and iOS simulator networking must be configured appropriately for their environment.

## Backend

`backend/` will contain one Python FastAPI service started with Uvicorn. It will use a maintainable separation of API routes, Pydantic schemas, services/business logic, database models, and core configuration/security. Route handlers must remain thin.

## Database

PostgreSQL is the target system of record. SQLAlchemy will own database access through sessions/repositories or service-layer abstractions; routes must not issue ad hoc database access. The schema is intentionally not designed in Prompt 0.

## Authentication

The prototype will use backend-managed identities, password hashing, and JWT access tokens. User identity and user data remain backend-owned. Refresh tokens are optional only if a verified need arises. Firebase is prohibited.

## API communication and CORS

REST APIs use the implemented `/api` prefix and JSON, alongside the unprotected `GET /health` endpoint. The Expo Router frontend has one centralized API client reading `EXPO_PUBLIC_API_BASE_URL` and stores only the JWT in Expo SecureStore. Backend CORS uses an explicit development allow-list sourced from environment configuration—never a production-wide wildcard for credentialed traffic.

## AI/ML, speech, and OCR boundaries

Gemini, ML models, speech processing, and OCR are backend-only integrations behind service interfaces. Clients do not receive provider secrets or call private providers directly. None of these integrations are implemented in Prompt 0.

## Local development flow

1. Start PostgreSQL and create the local `dhan_saarthi` database.
2. Run FastAPI locally with configuration from `backend/.env`.
3. Start Expo locally with `frontend/.env` pointing to the reachable backend URL.
4. Verify each vertical slice through both API and app rendering before advancing.

## High-level data flow

```text
React Native / Expo UI
  → centralized API client
  → FastAPI route
  → service / business logic
  → SQLAlchemy + PostgreSQL and (later) provider adapters
  → typed JSON response
  → frontend state and rendered UI
```
