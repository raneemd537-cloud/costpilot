# CostPilot — Product Cost & Profit Decision Lab

A local bilingual (Arabic/English) product-cost and pricing workspace. It uses a dependency-free Python HTTP server, SQLite, and a responsive HTML/CSS/JavaScript interface.

## Run it

Use Python 3.11 or newer:

```powershell
python -m app.server
```

Then open [http://127.0.0.1:8765](http://127.0.0.1:8765). On this machine, if `python` is not on PATH, run:

```powershell
& 'C:\Users\khatib\anaconda3\python.exe' -m app.server
```

The app binds to loopback only. SQLite data is stored in `.decision-lab/decision-lab.sqlite3` under the current directory. Set `DECISION_LAB_DATA` to use another data folder, or `DECISION_LAB_PORT` to choose another port. Do not expose this local server to the public internet.

## Google account sign-in

Google sign-in uses the server-side authorization-code flow with PKCE, a one-time state cookie, and Google's verified userinfo response. Create a Google OAuth client of type Web application and register the exact redirect URI below. These variables must be set in the server environment; the Google client secret is never sent to the browser.

```powershell
$env:GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com"
$env:GOOGLE_CLIENT_SECRET = "your-client-secret"
$env:GOOGLE_REDIRECT_URI = "http://localhost:8765/auth/google/callback"
python -m app.server
```

For an HTTPS deployment, register its exact HTTPS callback and set `DECISION_LAB_SECURE_COOKIE=1`. The current server is designed for local loopback use and should not be exposed publicly without a production deployment review.

## Financial rules

- Whole-quantity profit/loss = discounted unit selling price × quantity − total cost.
- Margin = profit ÷ revenue. Return on cost = profit ÷ total cost. A zero denominator displays as unavailable.
- Break-even unit price = total cost ÷ quantity.
- Break-even is shown as the original unit price before discount. The entered discount is included; at a 100% discount no finite break-even price exists.
- A fixed-profit target price accounts for discount and the full target amount.
- A percentage target explicitly selects margin on revenue or markup on cost.
- Shared expenses split by quantity, purchase value, or weight. The largest-remainder cent allocation reconciles to the original amount. Mixed currencies cannot share an expense.
- Customer-paid delivery is excluded. Supplier shipping has no special rule; it may only be entered as an explicitly allocated general expense.
- Initial currencies: USD, EUR, GBP, ILS, JOD, SAR, AED, EGP. No conversion is performed.

## Stack and security choices

- Python standard-library HTTP and SQLite avoid package installs and keep the local app self-contained.
- Passwords use salted `scrypt` (N=2^17, r=8, p=1). Session cookies are HttpOnly and SameSite=Lax; only a SHA-256 verifier of the random session cookie is persisted. Mutating API calls require a per-session CSRF token. SQL uses placeholders, and all product, scenario, shared-cost, and history operations are owner-scoped.
- Request bodies are limited to 256 KiB. The server sets a restrictive same-origin Content Security Policy and security headers.
- The local server has no production TLS, rate limiting, automated backups, password recovery, or hosting hardening. Use loopback only; review and implement those controls before deployment.
- Guest data stays in the local SQLite database. Account creation explicitly offers transfer or a separate empty account.
- Cairo and DM Sans are requested from Google Fonts, with local system fallbacks if the service is unavailable.

## Speech and AI

- Voice input uses the browser Web Speech Recognition API when available, currently with Arabic or English selected from the app language. Speech results only populate reviewable fields. Nothing is saved or calculated until the user confirms the form. Browser support and mixed-language recognition quality vary; code-switching is not guaranteed. Some browsers send audio to their speech service. Recordings are not retained by this app.
- “Suggest profit improvements” is a user-triggered, local arithmetic comparison with stated assumptions; it does not predict demand and never edits prices. An optional AI financial review uses OpenAI's Responses API only after a per-request confirmation. It sends the product's currency, costs, quantity, expenses, price, discount, and deterministic results; it omits product name/category and account identity. AI commentary cannot change calculations. The response request uses `store: false`, but this is not a promise of zero retention; data handling also depends on the OpenAI project and organization settings. Review the provider's current data controls before enabling.
- AI review is off unless `OPENAI_API_KEY` is configured in the server environment. The key remains server-side. Optional `DECISION_LAB_AI_MODEL` defaults to `gpt-5.4-mini`. In PowerShell, set these in the same terminal before launching the server:

```powershell
$env:OPENAI_API_KEY = "your-project-key"
$env:DECISION_LAB_AI_MODEL = "gpt-5.4-mini"
python -m app.server
```

The UI displays the consent prompt on each review. No real provider call is made by automated tests. API usage can incur charges.

## Skills and verification

Used Superpowers workflows: using-superpowers, brainstorming (the detailed PRD authorized proceeding without a clarification round), writing-plans, test-driven-development, executing-plans, and verification-before-completion. No dedicated UI, database, or security skill was available in the provided Skills list. OWASP password-storage and session-management guidance informed the auth/session controls.

Run the automated suite:

```powershell
& 'C:\Users\khatib\anaconda3\python.exe' -m unittest discover -v
```

The suite covers calculation formulas and edge cases, cent-reconciled expense allocation, SQLite persistence, guest transfer, owner separation, CSRF, product calculations, scenarios, activity history, mixed-currency rejection, and mocked AI request behavior without an external call.
