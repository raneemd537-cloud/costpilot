# Product Cost & Profit Decision Lab — Design

## Intent
Build a bilingual, responsive seller tool for cost calculation, product management, saved pricing scenarios, and calculation history. The supplied PRD is authoritative; financial results come only from deterministic code.

## Goals and constraints
- Support guest use and optional accounts, persistent storage, isolated records, editable products, and explicit guest-data transfer choice.
- Support per-product currency; never aggregate across currencies. Support direct and order-shared expenses with explicit, data-appropriate quantity/value/weight allocation. Customer-paid delivery is excluded from seller costs. Supplier shipping has no special rule.
- Show total cost, whole-quantity profit/loss, margin on revenue, return on cost, break-even, and fixed/percentage target prices. Make percentage target basis explicit and selectable (margin on revenue or markup on cost).
- Arabic/English with correct direction, Cairo Arabic type, light/dark themes, responsive dashboard and navigation, product detail dialog tabs, four-step entry, voice review, manual scenarios, history, charts, and user-triggered improvement suggestions.
- No auto-generated scenarios, auto-applied changes, unapproved currency conversion, or fabricated missing speech values.

## Approaches
1. Managed cloud SaaS (hosted frontend/API/database and paid speech/AI). Best production operations, but requires accounts, secrets, costs, and external services the user has not provided.
2. Local Python standard-library server + SQLite + dependency-free web UI (selected implementation). Runs without installs or service credentials, supports real server persistence/authentication and can be reviewed locally. Speech uses browser Web Speech when available; provider variability and lack of a configured AI service limit voice/AI capabilities. Keep integration seams documented.
3. Browser-only app using local storage. Simplest, but no real accounts or server-side isolation and weak multi-device persistence; rejected against the PRD.

## Architecture and decisions
- Python 3.11+ standard-library HTTP server, SQLite repository, scrypt password hashes, opaque server-side sessions, HttpOnly/SameSite cookies, CSRF token, and same-origin JSON API. SQLite file is local application data and is not served as a static asset.
- Static HTML/CSS/JavaScript frontend, no third-party runtime dependencies. CSS custom properties support themes; logical properties and `dir` support RTL/LTR.
- Central calculation module owns all arithmetic, input validation, expense allocation, target prices, and rounding. Money is represented internally as integer minor units where possible; weights/ratios use decimal arithmetic. Two-decimal display.
- Initial currency choices: USD, EUR, GBP, ILS, JOD, SAR, AED, EGP. This is an implementation choice, not a user-approved list; no conversion.
- Target percentage basis is user-selectable; UI names both interpretations. Scenarios persist as mutable saved records (no immutable edit history). Calculation history is a separate append-only record.
- Voice: browser SpeechRecognition / webkitSpeechRecognition where present, Arabic and English selectable recognition with review before calculation. Explain browser support and remote processing variability. No recording is retained. Mixed-language quality cannot be guaranteed by the browser API.
- AI: deterministic local review and suggestion calculations only until a real provider and credentials are configured; no UI claim of LLM analysis. Preserve a server-side adapter seam; never allow external text to set financial numbers.
- Skills used: Superpowers using-superpowers, brainstorming (user explicitly asked to start and avoid conversation, so proceed on PRD), writing-plans, test-driven-development, executing-plans, verification-before-completion, and systematic-debugging as needed. No suitable specialized UI/security/database skill was present in the supplied skill catalog; use OWASP guidance for auth/session decisions.

## Security, privacy, operations
- Validate request sizes, JSON types, money/ranges, ownership on every record operation, and same-origin mutating requests. Parameterized SQL, password hashing with per-user salt and scrypt, session rotation, CSRF protection, and generic login failures.
- Guest data has a random guest identity cookie and local SQLite ownership; account transfer is an explicit choice at registration.
- AI is optional and user-triggered per review. When enabled, the server sends a minimal financial summary to the OpenAI Responses API with `store: false`; the UI names the provider/data transfer and requests confirmation every time. Product name, category, and account identity are omitted. This does not promise zero retention; API project data controls still apply. The API key remains in server environment only. Speech may be processed by the browser's provider as already disclosed.
- Bind local development server to loopback by default. Production hosting needs HTTPS, backup operations, rate limiting, and a hardened deployment before public exposure.

## Acceptance outline
Unit-test formulas, input boundaries, allocations/remainders and currencies. Exercise API authentication, guest migration, ownership, CRUD, scenarios, history, validation. Check frontend translations/direction, forms, modal, themes, voice fallback, and responsive states. Document unverified external-service and deployment constraints.
