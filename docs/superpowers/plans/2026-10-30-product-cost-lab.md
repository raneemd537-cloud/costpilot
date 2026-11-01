# Product Cost & Profit Decision Lab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deliver a locally runnable bilingual seller decision lab with deterministic calculations, persistent products/accounts, manual scenarios, history, responsive dashboard, voice input, and honest local advisory behavior.

**Architecture:** Dependency-free Python HTTP/SQLite backend and HTML/CSS/JS frontend. Core calculations live in a separately testable Python module. API enforces user/guest ownership, session and CSRF boundaries. PRD design is in `docs/superpowers/specs/2026-10-30-product-cost-lab-design.md`.

**Tech Stack:** Python standard library, SQLite, semantic HTML, vanilla JavaScript/CSS, browser SpeechRecognition when supported.

## File structure
- `app/calculations.py`: deterministic finance, expense allocation, validation.
- `app/store.py`: SQLite schema, persistence, ownership-scoped data operations.
- `app/server.py`: local HTTP API, auth/session/CSRF, static delivery.
- `web/index.html`, `web/app.js`, `web/styles.css`: bilingual responsive UI and interactions.
- `tests/test_calculations.py`, `tests/test_api.py`: unit and integration tests.
- `README.md`: run instructions, choices, security/privacy limitations.

## Tasks

### 1. Calculation engine
Write failing tests for purchase totals, costs, discount, profit/loss, both percentage denominators, break-even, fixed/percentage targets, allocation and remainder, invalid inputs/edge cases. Implement decimal-cent-safe centralized functions and run tests.

### 2. Persistence and data model
Write tests for SQLite schema and owner-scoped products, expense details, scenarios, and calculation history; implement repository and run tests.

### 3. API, guest identity and accounts
Test guest CRUD, signup/login/logout, password hashing, CSRF, ownership isolation, explicit guest transfer/empty choice, scenario CRUD, history and server validation. Implement HTTP API and run tests.

### 4. Design system and app shell
Implement responsive purple/lavender shell, sidebar/topbar/mobile navigation, RTL/LTR language switch, light/dark themes, dashboard empty/loading states. Check served page and keyboard/focus semantics.

### 5. Product workflow and details
Implement 4-step add/edit flow, voice input review, product cards and large accessible tabbed detail dialog, expenses and currency handling. Keep form state while stepping back.

### 6. Pricing scenarios and activity
Implement manual scenario creation/comparison, calculation history, target basis selection, deterministic suggestion/review UI, and separate currency dashboard summaries/charts.

### 7. Integration, documentation and review
Run unit and API tests, fix findings using RED→GREEN. Check Arabic/English and desktop/mobile UI manually where available. Document run/security/provider limitations and perform a separate final review.

## Review focus
Rounding must reconcile allocated cents. No cross-currency total. Server-side authorization for every record. No scenario writes to calculation history. Speech extraction cannot auto-save/calculate. AI or suggestion copy cannot mutate deterministic outputs or claim demand outcomes.
