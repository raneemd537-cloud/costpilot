# ProfitPilot — Product Cost & Profit Decision Lab

ProfitPilot is a bilingual (Arabic/English) web application for product cost calculation, pricing decisions, and profit analysis.

It helps users understand the full cost of their products, calculate profit or loss, and compare different pricing scenarios through a simple, responsive interface.

The application supports local development with Python and SQLite, as well as PostgreSQL and Docker-based deployment.

---

## Features

### 1. Financial Calculations & Pricing

- **Product Cost Calculation:** Calculate purchase costs, direct expenses, and allocated shared expenses.
- **Profit & Loss Analysis:** Calculate total cost, revenue, net profit or loss, profit margin, and return on cost.
- **Break-Even Analysis:** Calculate the selling price required to cover product costs.
- **Target Profit Pricing:** Calculate the selling price needed to achieve a target profit.
- **Discount Calculation:** Calculate the final selling price and financial results after discounts.
- **Shared Expense Allocation:** Distribute shared expenses by quantity, purchase value, or weight.
- **Scenario Planning:** Create and compare different pricing scenarios for products.
- **Multi-Currency Support:** Supports USD, EUR, GBP, ILS, JOD, SAR, AED, and EGP. Different currencies are handled separately without automatic conversion.

### 2. User Experience

- **Arabic and English:** Bilingual interface with RTL support for Arabic and LTR support for English.
- **Responsive Design:** Supports desktop and mobile screens.
- **Light and Dark Themes:** Users can switch between visual themes.
- **Guest Access:** Users can start using the application without creating an account.
- **Registered Accounts:** Users can register and log in.
- **Guest Data Migration:** Users can choose to transfer guest data when creating an account.
- **Voice Input (Optional):** Supports browser-based speech recognition where available. Extracted information can be reviewed before submission.

### 3. Authentication & Security

- Password hashing using salted `scrypt`.
- Secure session token handling.
- HttpOnly and SameSite session cookies.
- CSRF protection for modifying API requests.
- Content Security Policy (CSP).
- Security headers, including:
  - `X-Content-Type-Options`
  - `X-Frame-Options`
  - `Referrer-Policy`
- Rate limiting for authentication and API requests.
- Password reset using single-use tokens with a limited validity period.
- Optional HTTPS cookie protection using `DECISION_LAB_SECURE_COOKIE=1`.
- Optional reverse proxy support using `DECISION_LAB_TRUST_PROXY=1`.

### 4. Database & Operations

- **SQLite:** Default database for local development.
- **PostgreSQL:** Supported through the `DATABASE_URL` environment variable.
- **Database Migration:** Includes a script for migrating SQLite data to PostgreSQL.
- **Database Backups:** Includes an SQLite backup script with automatic retention cleanup.
- **Health Check:** The `/health` endpoint returns application health information.
- **Docker Support:** Includes a Dockerfile for container-based deployment.

### 5. Optional Integrations

The following integrations require additional configuration:

- **SMTP:** For sending password reset emails.
- **Google OAuth:** For Google sign-in, when configured.
- **OpenAI API:** For optional AI-powered financial reviews.

The application can run locally without configuring these external services.

---

## Installation & Local Setup

### Requirements

- Python 3.11 or newer.
- Git.

### 1. Clone the repository

```bash
git clone https://github.com/raneemd537-cloud/costpilot.git
cd costpilot
```

### 2. Install dependencies

Install the project's Python dependencies:

```bash
python -m pip install -r requirements.txt
```

SQLite is included with Python and does not require a separate database installation.

### 3. Run the application

```bash
python -m app.server
```

Open the following address in your browser:

http://127.0.0.1:8765

---

## Running Tests

Install pytest if it is not already available:

```bash
python -m pip install pytest
```

Run the automated test suite:

```bash
python -m pytest tests/ -v
```

The test suite covers financial calculations, database operations, API behavior, authentication, and production-related functionality.

---

## Environment Configuration

The project includes an `.env.example` file as a configuration reference.

Set environment variables in your deployment environment as needed.

| Variable | Description |
|---|---|
| `DECISION_LAB_HOST` | Server bind address. Use `0.0.0.0` when required by a container or hosting platform. |
| `DECISION_LAB_PORT` | Server listening port. |
| `DECISION_LAB_DATA` | Directory used for local application data. |
| `DATABASE_URL` | PostgreSQL connection URL. If configured, the application uses PostgreSQL instead of SQLite. |
| `DECISION_LAB_TRUST_PROXY` | Set to `1` when using a trusted reverse proxy. |
| `DECISION_LAB_SECURE_COOKIE` | Set to `1` when serving the application over HTTPS. |
| `APP_BASE_URL` | Public application URL, used when generating password reset links. |
| `SMTP_HOST` | SMTP server hostname for email delivery. |
| `SMTP_PORT` | SMTP server port. |
| `SMTP_USER` | SMTP account username. |
| `SMTP_PASSWORD` | SMTP account password or application credential. |
| `SMTP_FROM` | Sender address for outgoing emails. |
| `GOOGLE_CLIENT_ID` | Optional Google OAuth client ID. |
| `GOOGLE_CLIENT_SECRET` | Optional Google OAuth client secret. |
| `GOOGLE_REDIRECT_URI` | Optional Google OAuth callback URL. |
| `OPENAI_API_KEY` | Optional OpenAI API key for AI features. |
| `DECISION_LAB_AI_MODEL` | Optional AI model configuration. |

**Important:** Never commit passwords, API keys, database credentials, or other secrets to GitHub.

External integrations such as SMTP, Google OAuth, and OpenAI require valid configuration before they can be used.

---

## Database Management

### SQLite Backups

Run the backup script:

```bash
python scripts/backup.py
```

The script creates an SQLite database backup and removes old backups according to its retention settings.

### SQLite to PostgreSQL Migration

To migrate an existing SQLite database to PostgreSQL:

1. Configure the `DATABASE_URL` environment variable with your PostgreSQL connection URL.
2. Run:

```bash
python scripts/migrate_sqlite_to_pg.py
```

Review the migration output and verify the migrated data before using the PostgreSQL database.

---

## Docker Deployment

Build the Docker image:

```bash
docker build -t profitpilot .
```

Run the container:

```bash
docker run -d -p 8765:8765 --name profitpilot profitpilot
```

For persistent data, configure a suitable volume and database location according to the container configuration.

Check the health endpoint:

```bash
curl http://127.0.0.1:8765/health
```

---

## Project Structure

```text
costpilot/
├── app/
│   ├── server.py
│   ├── store.py
│   ├── calculations.py
│   ├── ai.py
│   ├── email.py
│   └── ratelimit.py
├── scripts/
│   ├── backup.py
│   └── migrate_sqlite_to_pg.py
├── tests/
├── web/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## Project Status

ProfitPilot includes financial calculation tools, product scenario planning, bilingual user interface support, authentication, database support, and deployment-related features.

The application can be run locally for development and testing. Deployment requires configuring the appropriate database, environment variables, and external services for the selected hosting platform.
