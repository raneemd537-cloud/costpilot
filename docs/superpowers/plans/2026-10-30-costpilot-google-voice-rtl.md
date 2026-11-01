# CostPilot Google, Voice, and RTL Update Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Rebrand the app to CostPilot, offer secure Google account creation/sign-in, improve Arabic fullscreen layout, and make voice entry predictable and accessible.

**Architecture:** Keep the existing Python/SQLite and vanilla JavaScript architecture. Add server-side Google OAuth authorization-code + PKCE with one-time state bound to a short-lived HttpOnly cookie; use verified Google email/subject for account identity. Keep speech recognition browser-local to the current feature and ensure stop/error/close cleanup. Use logical CSS positioning for RTL/fullscreen.

**Technology:** Python stdlib HTTP server, SQLite, vanilla HTML/CSS/JS, Web Speech API, Google OAuth 2.0 endpoints.

## Tasks

- [ ] Add store tests for Google identity creation, repeat sign-in, guest transfer, and identity conflict; implement schema migration and transactional store method.
- [ ] Add OAuth route tests for unconfigured setup, state mismatch, and configured authorization redirect; implement secure Google start/callback, verified userinfo check, PKCE, and env documentation.
- [ ] Add localized Google sign-in UI and callback feedback; update branding to CostPilot.
- [ ] Improve voice recognition lifecycle, transcript accumulation, language changes, error feedback, stop, and dialog-close cleanup.
- [ ] Correct logical RTL/fullscreen layout and verify desktop/mobile English/Arabic layouts.
- [ ] Run focused and full test suites, syntax checks, and live browser checks.
