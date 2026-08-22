# API Contract

## Status

Prompt 1 establishes the contracts below. The backend uses `/api` (not `/api/v1`) because that is the implemented route prefix required by Prompt 1.

## Conventions

- Base path: `/api`
- Implemented endpoint prefix: `/api`
- Content type: `application/json` for JSON request/response bodies.
- Naming: JSON uses `snake_case`, matching Pydantic models.
- Successful responses return endpoint-specific JSON objects or arrays with HTTP 2xx status codes.
- Protected endpoints use `Authorization: Bearer <access_token>`.
- Error body convention:

```json
{
  "detail": "Human-readable explanation"
}
```

FastAPI validation errors may include its standard structured `detail` array.

## Implemented endpoints

### `GET /health`

Purpose: report whether the API process is available during local development.

Success response (`200 OK`):

```json
{
  "status": "ok"
}
```

This endpoint has no authentication requirement or request body.

### Authentication

- `POST /api/auth/register` — `{full_name, email, password}`. Returns `201` and `{access_token, token_type, user, onboarding_complete}`; duplicate email returns `409`.
- `POST /api/auth/login` — `{email, password}`. Returns the same token/session payload; invalid credentials return `401`.
- `GET /api/auth/me` — bearer-protected. Returns the current user and `onboarding_complete`.

### Profile

- `GET /api/profile` — bearer-protected. Returns the user's profile or `404` before onboarding.
- `PUT /api/profile` — bearer-protected. Upserts age, optional gender/city, occupation, monthly income/expenses, savings, goal, risk preference, language, and accessibility mode.

### Financial Twin

- `GET /api/financial-twin` — bearer-protected. Returns the saved prototype twin or `404`.
- `PUT /api/financial-twin/generate` — bearer-protected. Creates or refreshes the deterministic prototype score after a profile exists; returns `400` without a profile.

## Future module placeholders

- Authentication
- Financial profile and Financial Twin
- AI Saarthi
- Financial Literacy
- Smart Planning
- Scam Shield
- Inclusive Finance

Do not add contracts here until their vertical slice is implemented or deliberately established.
