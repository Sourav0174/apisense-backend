<div align="center">

# APISense

**Know what your APIs are doing — before your users tell you.**

APISense is an AI-assisted API observability platform for modern backend developers. Monitor performance, analyze request logs, detect failures, and get actionable insights with minimal setup.

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.139-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-4169E1?logo=postgresql&logoColor=white)](https://neon.tech/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-migrations-6BA81E)](https://alembic.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![License](https://img.shields.io/badge/License-Unlicensed-lightgrey)](#license)

</div>

---

## Dashboard Preview

<div align="center">
  <img src="public/readme/dashboard.png" alt="APISense Dashboard Preview" width="100%" />
</div>

---

## Why APISense?

Modern backend teams ship APIs fast, but fly blind once they're live:

- Failures surface through **user complaints**, not monitoring.
- Logs are scattered across providers with no unified view.
- Existing observability tools are **heavyweight, expensive, or built for infrastructure — not API behavior**.

APISense gives developers a lightweight, drop-in way to see exactly what their APIs are doing — request patterns, failures, and performance — with a setup that takes minutes, not days.

---

## Features

- ✅ JWT Authentication
- ✅ Email Verification
- ✅ Password Reset
- ✅ Refresh Token Rotation
- 🔜 Projects
- 🔜 API Keys
- 🔜 Python SDK
- 🔜 Telemetry Ingestion
- 🔜 Dashboard & Request Logs
- 🔜 Endpoint Analytics

---

## Architecture Overview

```mermaid
flowchart TD
    A[Python Application] --> B[APISense Python SDK]
    B --> C[Ingestion API]
    C --> D[FastAPI Backend]
    D --> E[(PostgreSQL)]
    D --> F[Dashboard]
```

---

## Tech Stack

### Backend

| Technology             | Purpose                              |
| ---------------------- | ------------------------------------ |
| FastAPI                | High-performance async API framework |
| Python 3.13            | Core language                        |
| PostgreSQL (Neon)      | Primary database                     |
| SQLAlchemy 2.x (async) | ORM                                  |
| Alembic                | Database migrations                  |

### Authentication

| Technology             | Purpose                      |
| ---------------------- | ---------------------------- |
| JWT                    | Access token authentication  |
| Refresh Token Rotation | Secure, revocable sessions   |
| Argon2                 | Password hashing             |
| Brevo                  | Transactional email delivery |

### Frontend _(planned)_

| Technology    | Purpose            |
| ------------- | ------------------ |
| Next.js       | React framework    |
| React         | UI library         |
| TypeScript    | Type safety        |
| Tailwind CSS  | Styling            |
| shadcn/ui     | Component library  |
| Framer Motion | Animation          |
| Recharts      | Data visualization |

### Deployment

| Technology      | Purpose                     |
| --------------- | --------------------------- |
| Docker          | Containerization            |
| Neon PostgreSQL | Managed serverless Postgres |

---

## Project Structure

```
apisense-backend/
├── alembic/                    # Database migrations
│   └── versions/
├── app/
│   ├── api/                    # Routers — request validation & responses
│   │   ├── auth.py
│   │   ├── deps.py
│   │   ├── exception_handlers.py
│   │   └── health.py
│   ├── core/                   # Configuration & security primitives
│   │   ├── config.py
│   │   └── security.py
│   ├── db/                     # Models, repositories, session management
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── base.py
│   │   └── session.py
│   ├── schemas/                 # Pydantic request/response models
│   ├── services/                 # Business logic
│   └── main.py                   # Application entry point
├── public/readme/                # README assets
├── requirements.txt
└── alembic.ini
```

Follows a strict **Router → Service → Repository → Database** architecture, keeping request handling, business logic, and persistence cleanly separated.

---

## Getting Started

### Prerequisites

- Python 3.13+
- A PostgreSQL database (e.g. [Neon](https://neon.tech/))
- A [Brevo](https://www.brevo.com/) account for transactional email

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-org>/apisense-backend.git
cd apisense-backend

# Create and activate a virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Then edit .env with your own database URL, secret key, and API credentials
```

### Run database migrations

```bash
alembic upgrade head
```

### Start the development server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

---

## Environment Variables

```bash
APP_NAME=APISense API
APP_ENV=development
SECRET_KEY=

DATABASE_URL=postgresql://user:password@ep-example-12345.us-east-2.aws.neon.tech/dbname?sslmode=require

# JWT
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080

# SQLAlchemy connection pool (optional, defaults shown)
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_RECYCLE=300
DB_POOL_PRE_PING=true
DB_ECHO=false

# Brevo transactional email
BREVO_API_KEY=
EMAIL_FROM=noreply@example.com
EMAIL_FROM_NAME=APISense
APP_BASE_URL=http://localhost:3000

# Token expiry (optional, defaults shown)
EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS=24
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES=30
```

[`.env.example`](.env.example) is committed to Git as a documented template with placeholder values. `.env` is gitignored and holds your local secrets — copy the example file and fill in your own credentials; never commit it.

---

## Authentication Features

APISense ships with a production-grade authentication system:

- **JWT Authentication** — stateless access tokens for API requests.
- **Email Verification** — hashed, time-limited verification tokens sent via Brevo.
- **Password Reset** — secure, hashed, single-use reset tokens.
- **Refresh Token Rotation** — DB-backed, revocable refresh tokens with rotation on every use, plus logout and logout-all support.

All tokens are hashed before persistence — nothing sensitive is ever stored in plain text.

---

## Roadmap

- [x] User Authentication
- [x] Email Verification
- [x] Password Reset
- [x] Refresh Token Rotation
- [ ] Projects
- [ ] API Keys
- [ ] Google OAuth
- [ ] Python SDK
- [ ] Telemetry Ingestion
- [ ] API Dashboard
- [ ] Request Logs
- [ ] Endpoint Analytics
- [ ] AI Insights

---

## Contributing

APISense is under active development. Contributions, issues, and feature suggestions are welcome — please open an issue to discuss significant changes before submitting a pull request.

---

## License

No license has been set for this project yet. All rights reserved unless otherwise stated.
