# FAQ Crowdsourcing Platform — Complete Project Documentation

## 1. Project Overview

The FAQ Crowdsourcing Platform is a web-based knowledge-sharing system built with Django (Python). It enables users to collaboratively create, manage, and access frequently asked questions (FAQs). Unlike traditional FAQ systems where only administrators maintain content, this platform uses crowdsourcing: users contribute questions, submit answers, suggest edits, and vote on usefulness.

An AI-powered assistant named **Yaksha** understands natural-language questions and retrieves relevant answers from the FAQ database, with optional OpenAI integration for richer responses.

**Target use cases:** educational institutions, organizations, communities, customer support portals, and internal knowledge management.

## 2. Project Objectives (Implemented)

- [x] Centralized FAQ repository with categories and tags
- [x] Collaborative FAQ contribution and community edit suggestions
- [x] Self-service Q&A to reduce repetitive support requests
- [x] Keyword + advanced search, autocomplete, duplicate detection
- [x] AI assistant (Yaksha) with FAQ retrieval and source citations
- [x] Moderation workflow: submit → review → approve/reject → publish
- [x] Community engagement: voting, reputation, badges, leaderboards
- [x] Analytics dashboard for moderators
- [x] Notifications, bookmarks, trending FAQs, related recommendations

## 3. Technology Stack

| Layer | Technologies |
|-------|----------------|
| Frontend | HTML5, CSS3, Bootstrap 5, Bootstrap Icons, JavaScript |
| Backend | Django 5.x (Python 3.10+) |
| Database | SQLite (default) or PostgreSQL (`DATABASE_URL`) |
| AI Layer | OpenAI API (optional) + keyword/similarity FAQ retrieval |
| Static | WhiteNoise (production), CDN for Bootstrap |
| Deploy | Gunicorn-ready; Render, Railway, AWS, DigitalOcean |

## 4. Directory Structure

```
Test Project/
├── .venv/                    Python virtual environment (local, not in git)
├── .env                      Environment variables (copy from .env.example)
├── .env.example              Template for configuration
├── .gitignore
├── manage.py                 Django management entry point
├── requirements.txt          Core Python dependencies
├── requirements-dev.txt        Development + testing dependencies
├── requirements-prod.txt       Production extras
├── REQUIREMENTS.md           Explains all requirement files
├── README.md                 This file
├── db.sqlite3                SQLite database (created after migrate)
│
├── config/                   Django project settings
├── accounts/                 User management & RBAC
├── faqs/                     FAQ categories, CRUD, search, bookmarks
├── qa/                       Community questions & answers
├── community/                Reputation, badges, notifications, leaderboard
├── moderation/               Reports, admin dashboard
├── analytics/                Analytics for moderators
├── assistant/                Yaksha AI chatbot API & widget
├── templates/                HTML templates (Bootstrap UI)
├── static/                   CSS and JavaScript (chatbot, search)
└── media/                    User uploads (avatars, FAQ attachments)
```

## 5. Django Applications (Modules)

### 5.1 `accounts` — User Management

- Registration, login, logout
- Password reset (email to console in development)
- User profiles (bio, avatar, reputation, role)
- Roles: User, Moderator, Administrator (stored on `UserProfile`)
- Decorators: `@moderator_required`, `@admin_required`

### 5.2 `faqs` — FAQ Management

- Categories: Academics, Technical Support, Placements, Hostel, Administration, General Queries (seeded by default)
- FAQ creation with title, question, answer, tags, image, attachment
- Status workflow: `pending` → `published` / `rejected`
- Community edit suggestions with version increment on approval
- FAQ upvote/downvote, view counting, bookmarks
- Search: keyword, category, tag, sort (popular/recent/views)
- Autocomplete API: `/search/autocomplete/`
- Duplicate check API: `/search/duplicate-check/`

### 5.3 `qa` — Question & Answer System

- Post questions with rich text (sanitized HTML)
- Multiple answers per question, ranked by accepted + votes
- Upvote/downvote answers
- Accept answer (question author only)
- Related FAQ recommendations on question pages

### 5.4 `community` — Engagement

Reputation points (configurable in `.env`):

| Action | Default Points |
|--------|----------------|
| Answer posted | 5 |
| Upvote received | 10 |
| Accepted answer | 20 |
| FAQ published | 15 |
| Edit accepted | 10 |

Also includes badges, leaderboards (overall/weekly/monthly), and in-app notifications.

### 5.5 `moderation` — Content Safety

- Report spam, offensive, incorrect, duplicate content
- Moderator report queue and resolution
- Admin dashboard with user/FAQ/question/report counts
- FAQ approval queue at `/moderation/pending/` (moderator role)

### 5.6 `analytics` — Insights (Moderators)

- Most viewed FAQs, top searched keywords, unanswered questions
- Trending tags, active contributors, FAQ growth totals

### 5.7 `assistant` — Yaksha AI Chatbot

- Floating widget on every page (bottom-right)
- `POST /assistant/api/chat/` with JSON `{ "message": "..." }`
- Retrieves relevant FAQs via similarity + keyword match
- With `OPENAI_API_KEY`: GPT-powered contextual answers with citations
- Without API key: keyword fallback quoting best matching FAQ

## 6. System Architecture

```
[ Users — Browser ]
        |
        v
[ Django Web Application ]
        |
   accounts | faqs | qa | community | ...
        |
        v
[ SQLite / PostgreSQL ]
        |
        v
[ Search Layer — faqs/search.py ]
        |
        v
[ AI Assistant — assistant/services.py ]
        |
        v
[ Relevant FAQ Response + Sources ]
```

## 7. Content Approval Workflow

```
User submits FAQ
      |
      v
Status = PENDING (not visible in public browse)
      |
      v
Moderator opens: /moderation/pending/
      |
      +-- Approve --> PUBLISHED (author gets points + notification)
      |
      +-- Reject  --> REJECTED
```

Edit suggestions follow the same pattern; approved edits bump FAQ version.

## 8. Role-Based Access Control

| Role | Capabilities |
|------|----------------|
| **User** | Browse, search, Q&A, vote, bookmark, submit FAQ/edits, report content, use Yaksha |
| **Moderator** | All user abilities + approve FAQs/edits, analytics, report queue, moderation pending |
| **Administrator** | All moderator abilities + `/moderation/admin-dashboard/` |
| **Superuser** | Full Django admin at `/admin/` |

**Demo accounts** (after `seed_data`):

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | Administrator |
| `moderator` | `mod123` | Moderator |
| `demo` | `demo123` | User |

## 9. Setup Instructions

### 9.1 Prerequisites

- Python 3.10 or newer
- pip (included with Python)
- Optional: PostgreSQL for production
- Optional: OpenAI API key for enhanced Yaksha responses

### 9.2 Create and activate virtual environment

```bash
cd "/Users/radhikasharma/Documents/Test Project"
python3 -m venv .venv

# macOS / Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

### 9.3 Install dependencies

```bash
pip install -r requirements.txt

# For development (tests, linting):
pip install -r requirements-dev.txt
```

### 9.4 Configure environment

```bash
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY for production
```

### 9.5 Initialize database

```bash
python manage.py migrate
python manage.py seed_data

# Optional: create your own superuser
python manage.py createsuperuser
```

### 9.6 Run development server

```bash
python manage.py runserver
```

Open: **http://127.0.0.1:8000/**

### 9.7 Collect static files (production only)

```bash
python manage.py collectstatic --noinput
```

## 10. Environment Variables (`.env`)

| Variable | Description |
|----------|-------------|
| `DEBUG` | `True`/`False` — never `True` in public production |
| `SECRET_KEY` | Random string for Django crypto |
| `ALLOWED_HOSTS` | Comma-separated hostnames |
| `DATABASE_URL` | `sqlite:///db.sqlite3` or `postgres://user:pass@host:5432/db` |
| `OPENAI_API_KEY` | Optional — enables GPT answers in Yaksha |
| `OPENAI_MODEL` | Default: `gpt-4o-mini` |
| `POINTS_*` | Override reputation point values |
| `EMAIL_BACKEND` | Use SMTP in production for password reset |

## 11. Key URL Routes

| URL | Description |
|-----|-------------|
| `/` | Home (trending, categories, recent FAQs) |
| `/browse/` | FAQ search and listing |
| `/faq/<slug>/` | FAQ detail |
| `/submit/` | Submit new FAQ (login required) |
| `/bookmarks/` | Saved FAQs |
| `/category/<slug>/` | FAQs by category |
| `/accounts/register/` | Registration |
| `/accounts/login/` | Login |
| `/accounts/logout/` | Logout |
| `/accounts/password-reset/` | Password reset |
| `/accounts/profile/` | Your profile |
| `/qa/` | Question list |
| `/qa/ask/` | Ask question |
| `/community/leaderboard/` | Overall rankings |
| `/community/notifications/` | Notifications |
| `/moderation/pending/` | FAQ approval (moderator) |
| `/moderation/reports/` | Report queue (moderator) |
| `/moderation/admin-dashboard/` | Admin dashboard |
| `/analytics/` | Analytics (moderator) |
| `/assistant/api/chat/` | Yaksha chat API (POST JSON) |
| `/admin/` | Django admin panel |

## 12. Search System

**Keyword search** — FAQ title, question, answer, tags, category name (logged in `SearchLog`).

**Advanced filters** on `/browse/`:

- `q` — keyword
- `category` — category slug
- `tag` — tag name
- `sort` — `popular` \| `recent` \| `views`

**Smart search** — autocomplete API, similar FAQ recommendations, duplicate detection on new questions.

## 13. AI Assistant (Yaksha)

**Example:**

> **User:** Can I take leave during internship?  
> **Yaksha:** According to FAQ "Can I take leave during internship?" (Placements): Leave requests during internship are approved only under exceptional circumstances with prior written approval.

**Enable OpenAI:**

1. Obtain an API key from [OpenAI](https://platform.openai.com/)
2. Set `OPENAI_API_KEY=sk-...` in `.env`
3. Restart the server

## 14. Reputation & Badges

Points are awarded automatically via `community/services.py` when users post answers, receive upvotes, get answers accepted, have FAQs approved, or have edits accepted.

Badges are granted when thresholds are met (see `seed_data` for defaults). Leaderboards rank by total reputation or period-specific `ReputationLog` sums.

## 15. Database Models (Summary)

| Model | Purpose |
|-------|---------|
| `UserProfile` | Extended user with role, reputation, bio, avatar |
| `Category` | FAQ categories |
| `FAQ` | Core FAQ entries with status, votes, views, version |
| `FAQEditSuggestion` | Community-proposed edits |
| `FAQVote` | Per-user FAQ votes |
| `Bookmark` | User saved FAQs |
| `SearchLog` | Search analytics |
| `Question` / `Answer` / `AnswerVote` | Q&A system |
| `Badge` / `UserBadge` / `ReputationLog` / `Notification` | Community |
| `ContentReport` | Moderation reports |

## 16. Deployment

**Production checklist:**

- Set `DEBUG=False`
- Use a strong `SECRET_KEY`
- Configure `ALLOWED_HOSTS`
- Use PostgreSQL `DATABASE_URL`
- Set up real `EMAIL_BACKEND` for password reset
- `pip install -r requirements-prod.txt`
- `python manage.py collectstatic`
- Serve with Gunicorn:

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## 17. Testing & Development

```bash
pytest                    # if you add tests under tests/
ruff check .              # lint Python code
coverage run manage.py test
python manage.py check
```

## 18. Security Considerations

- User HTML sanitized with **bleach** (XSS prevention)
- CSRF protection on all POST forms
- Login required for contributions, voting, bookmarks
- Role decorators protect moderation and analytics views
- Never commit `.env` or `SECRET_KEY` to version control
- Change default demo passwords before public deployment

## 19. Extending the Platform

Possible future enhancements:

- Vector embeddings (sentence-transformers + pgvector) for semantic search
- Real-time notifications via WebSockets
- Email digests for trending FAQs
- OAuth social login
- WYSIWYG editor (TinyMCE/CKEditor)
- REST API (Django REST Framework) for mobile apps

## 20. Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` for django, decouple, etc. | Activate `.venv` and run `pip install -r requirements.txt` |
| No FAQs visible after submit | FAQs start as `PENDING`; moderator approves at `/moderation/pending/` |
| Yaksha gives generic answers only | Add `OPENAI_API_KEY` or run `python manage.py seed_data` |
| Static files missing in production | Run `collectstatic`; WhiteNoise is configured in settings |
| Profile does not exist for user | Profiles auto-create on user save; re-login or run `seed_data` |

## 21. License & Academic Use

This project is provided as a complete academic/organizational FAQ crowdsourcing implementation. Customize categories, branding, and policies for your institution.
