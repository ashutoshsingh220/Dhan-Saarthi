# UI Specification

## Brand direction

Use the Dhan Saarthi identity: premium but simple, deep-purple-led, professional financial product design, with white or very light backgrounds. Preserve and organize an existing logo asset if one is later found; do not redesign or replace it with an AI-generated asset.

## Visual system

- Color: deep purple primary actions, light neutral surfaces, restrained supporting accents, readable high-contrast text.
- Typography: modern, legible, scalable type with a clear hierarchy; prioritize plain-language financial content.
- Components: rounded cards, generous spacing, clear labels, obvious status/risk states, and minimal clutter.
- Navigation: mobile-first, task-oriented, and centered on the Financial Twin dashboard after onboarding.

## Reference screens

- Branding, experience selection, standard/voice-first onboarding, language preference, login, privacy/consent
- Financial profile onboarding, personal/income/expense capture, review, generation/progress, Financial Twin dashboard, score, insights
- Scam Shield QR/SMS/WhatsApp/document inputs and analysis report

These are design references only. Build the React Native UI from scratch; do not import or depend on Stitch-generated code.

## Accessibility expectations

Support screen readers, sensible touch targets, visible focus/state feedback where applicable, readable contrast, simple language, scalable text, and a path toward voice-first and regional-language experiences.

## Implementation principles

UI screens must render real state from the frontend's centralized API/client layer or clearly labelled local form state during a vertical slice. Do not ship disconnected mock screens as proof of a completed feature.
