# Dependency & Requirements Documentation

This project uses multiple requirement files for different environments.

## Files Overview

| File | Purpose |
|------|---------|
| `requirements.txt` | Core runtime dependencies for local development and production |
| `requirements-dev.txt` | Development tools (testing, linting, debug toolbar) |
| `requirements-prod.txt` | Production extras (database URL helper, Sentry) |
| `.env.example` | Template for environment variables — copy to `.env` |

## requirements.txt (Core)

- **Django** — Web framework (MTV pattern, ORM, admin, auth)
- **python-decouple** — Load settings from `.env`
- **Pillow** — Image uploads (avatars, FAQ images)
- **django-taggit** — Tag-based FAQ/question classification
- **django-crispy-forms** + **crispy-bootstrap5** — Bootstrap 5 form rendering
- **bleach** — Sanitize rich HTML in answers/FAQs
- **openai** — Optional AI assistant (Yaksha) via OpenAI API
- **psycopg2-binary** — PostgreSQL adapter (when `DATABASE_URL` uses Postgres)
- **gunicorn** — WSGI server for deployment
- **whitenoise** — Static file serving in production

## requirements-dev.txt

Includes everything in `requirements.txt` plus:

- **django-debug-toolbar** — Request/SQL debugging
- **pytest**, **pytest-django**, **coverage** — Testing
- **ruff** — Linting/formatting
- **ipython** — Enhanced shell

Install: `pip install -r requirements-dev.txt`

## requirements-prod.txt

Includes core plus:

- **dj-database-url** — Parse `DATABASE_URL` on PaaS (Render, Railway)
- **sentry-sdk** — Error monitoring (configure in production settings if needed)

Install: `pip install -r requirements-prod.txt`

## Environment Variables (.env)

See `.env.example` for full list. Key variables:

- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- `DATABASE_URL` — SQLite or PostgreSQL connection string
- `OPENAI_API_KEY` — Enables full NLU responses in Yaksha assistant
- Reputation point overrides (`POINTS_*`)

## Python Version

Python 3.10+ recommended (tested with 3.13).

## Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
