# PlanSpark

A **Persian-first**, bilingual (فارسی / English) task management web application built with Flask and SQLite. Designed from the ground up around the **Jalali (Shamsi) calendar system** with full RTL layout support, glassmorphism UI, and offline-capable PWA architecture.

---

## Architecture Overview

PlanSpark follows a **monolithic Flask application factory** pattern with server-rendered Jinja2 templates and a vanilla JavaScript frontend. All state is persisted in a single SQLite database file, with no external service dependencies.

```
┌─────────────────────────────────────────────────────────┐
│                      Client (Browser)                   │
│  Vanilla JS (main.js) ─── Jinja2-rendered HTML ─── CSS  │
│  Service Worker (sw.js)                                 │
└──────────────────────────┬──────────────────────────────┘
                           │  HTTP (HTML forms + fetch)
┌──────────────────────────▼──────────────────────────────┐
│                    Flask Application                    │
│  app.py (factory) ── forms.py ── translations.py        │
│  models.py (SQLAlchemy ORM) ── utils.py (date helpers)  │
└──────────────────────────┬──────────────────────────────┘
                           │  SQLAlchemy
┌──────────────────────────▼──────────────────────────────┐
│               SQLite (instance/todo.db)                 │
│         users │ tasks │ custom_priorities               │
└─────────────────────────────────────────────────────────┘
```

**Key architectural decisions:**
- **Naive UTC everywhere**: All `DateTime` columns store timezone-unaware UTC. Conversion to Jalali/Gregorian display strings happens exclusively at render time via `utils.py`.
- **Computed status, never stored**: Task status (`pending` / `done` / `expired`) is derived at query time from `is_done` and `expires_at` — no status column exists in the database.
- **Dictionary-driven i18n**: All user-facing strings live in a single `translations.py` dictionary keyed by `"fa"` / `"en"`, consumed by a `_t()` helper and Jinja2 context processor. No `.po` / `.mo` files or gettext dependency.
- **Zero build tooling**: No bundler, transpiler, or CSS preprocessor. All frontend code is shipped as-is.

---

## Core Features

### Backend (Python / Flask)
- **Application factory** (`create_app()`) with environment-based configuration
- **Bcrypt password hashing** via Flask-Bcrypt
- **CSRF protection** on every POST route via Flask-WTF
- **Session-based authentication** with Flask-Login and `@login_required` guards
- **Password recovery** system using two user-defined security words (bcrypt-hashed), with rate limiting (attempt counter + cooldown window)
- **User preferences**: per-user language (`fa`/`en`), date format (`jalali`/`gregorian`), and display style (`text`/`numeric`)
- **SQLAlchemy ORM** with `@validates` decorators enforcing data integrity at the model level
- **Cascading deletes**: removing a user automatically removes all their tasks and custom priorities
- **Composite index** on `(is_done, expires_at)` for efficient filtered queries
- **Static asset cache-busting** via file mtime appended as `?v=<timestamp>` query parameters
- **CLI command**: `flask init-db` to create all database tables

### Frontend (Vanilla JS / CSS / Jinja2)
- **Glassmorphism design system** with dark/light theme toggle (CSS custom properties)
- **Full RTL/LTR support** — layout direction switches dynamically with language
- **Jalali date pickers** powered by `jalaali.js` (vendored UMD bundle)
- **Live search** across task cards with real-time filtering
- **Modal dialog system** for task creation, editing, and deletion confirmation
- **Toast notifications** for flash messages with auto-dismiss animations
- **Custom select dropdowns** with glassmorphism styling replacing native `<select>` elements
- **Responsive breakpoints** at 900px, 480px, and 300px
- **Dual-font typography**: Vazirmatn (Persian) + Inter (Latin), served as local WOFF2 files

### Analytics Dashboard
- **Chart.js donut charts** for task status and priority distribution
- **Time-range filters**: daily, weekly, monthly, yearly, and custom Jalali date ranges
- **Visual statistics** computed client-side from server-rendered data

### PWA & Offline
- **Service Worker** (`sw.js`): cache-first for static assets, network-first for dynamic requests
- **Offline fallback page** (`offline.html`) with bilingual messaging and retry functionality
- **Web App Manifest** (`manifest.json`) with icons for installability
- **Pre-cached assets**: CSS, JS, app icons, and the offline page

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Runtime** | Python 3.x | Server-side logic |
| **Framework** | Flask ≥ 2.3 | HTTP routing, templating, session management |
| **ORM** | Flask-SQLAlchemy ≥ 3.0 | Database abstraction and model layer |
| **Database** | SQLite | Persistent storage (zero-config, file-based) |
| **Auth** | Flask-Login ≥ 0.6 | Session-based user authentication |
| **Passwords** | Flask-Bcrypt ≥ 1.0 | Bcrypt hashing for passwords and recovery words |
| **CSRF** | Flask-WTF ≥ 1.1 | Form-level CSRF token protection |
| **Forms** | WTForms (via Flask-WTF) | Server-side form validation |
| **Jalali dates** | jdatetime ≥ 4.1 | Python Jalali/Shamsi calendar conversion |
| **Timezone** | pytz ≥ 2023.3 | Timezone definitions for UTC conversion |
| **Environment** | python-dotenv ≥ 1.0 | `.env` file loading |
| **Templates** | Jinja2 (bundled with Flask) | Server-side HTML rendering |
| **Frontend JS** | Vanilla ES6+ | No framework — direct DOM manipulation |
| **Charts** | Chart.js (CDN) | Donut chart rendering on analytics page |
| **Calendar** | jalaali.js (vendored) | Client-side Jalali date picker |
| **Fonts** | Vazirmatn + Inter (WOFF2) | Offline-capable bilingual typography |
| **Icons** | Custom SVG set | 30+ inline SVG icons |

---

## Database Schema

### Entity-Relationship Diagram

```
┌──────────────────────┐       ┌──────────────────────────┐
│        users         │       │          tasks           │
├──────────────────────┤       ├──────────────────────────┤
│ id            PK     │──┐    │ id              PK       │
│ username      UQ,IDX │  │    │ user_id         FK → IDX │
│ name                 │  ├───<│ title                    │
│ family               │  │    │ description     NULL     │
│ password_hash        │  │    │ priority        NULL,IDX │
│ language       "fa"  │  │    │ expires_at      IDX      │
│ date_format  "jalali"│  │    │ estimated_time  NULL     │
│ date_display  "text" │  │    │ is_done         false    │
│ recovery_w1_hash     │  │    │ created_at      UTC      │
│ recovery_w2_hash     │  │    └──────────────────────────┘
│ recovery_attempts  0 │  │
│ last_recovery_attempt│  │    ┌──────────────────────────┐
│ created_at      UTC  │  │    │   custom_priorities      │
└──────────────────────┘  │    ├──────────────────────────┤
                          │    │ id              PK       │
                          └───<│ user_id         FK → IDX │
                               │ name                     │
                               └──────────────────────────┘
```

### Table: `users`

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| `id` | `Integer` | Primary Key | Auto |
| `username` | `String(20)` | Unique, Not Null, Indexed | — |
| `name` | `String(30)` | Not Null | — |
| `family` | `String(30)` | Not Null | — |
| `password_hash` | `String(128)` | Not Null | — |
| `language` | `String(2)` | Not Null | `"fa"` |
| `date_format` | `String(10)` | Not Null | `"jalali"` |
| `date_display_style` | `String(10)` | Not Null | `"text"` |
| `recovery_w1_hash` | `String(128)` | Not Null | — |
| `recovery_w2_hash` | `String(128)` | Not Null | — |
| `recovery_attempts` | `Integer` | Not Null | `0` |
| `last_recovery_attempt` | `DateTime` | Nullable | `NULL` |
| `created_at` | `DateTime` | Not Null | UTC now |

### Table: `tasks`

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| `id` | `Integer` | Primary Key | Auto |
| `user_id` | `Integer` | FK → `users.id` (CASCADE), Not Null, Indexed | — |
| `title` | `String(100)` | Not Null | — |
| `description` | `String(500)` | Nullable | `NULL` |
| `priority` | `String(50)` | Nullable, Indexed | `NULL` |
| `expires_at` | `DateTime` | Not Null, Indexed | — |
| `estimated_time` | `Integer` | Nullable | `NULL` |
| `is_done` | `Boolean` | Not Null | `False` |
| `created_at` | `DateTime` | Not Null | UTC now |

**Composite Index:** `ix_tasks_is_done_expires` on `(is_done, expires_at)`

**Computed Status Logic** (never stored):
| Status | Condition |
|--------|-----------|
| `pending` | `is_done = False` AND `expires_at ≥ NOW()` |
| `done` | `is_done = True` |
| `expired` | `is_done = False` AND `expires_at < NOW()` |

### Table: `custom_priorities`

| Column | Type | Constraints | Default |
|--------|------|-------------|---------|
| `id` | `Integer` | Primary Key | Auto |
| `user_id` | `Integer` | FK → `users.id` (CASCADE), Not Null, Indexed | — |
| `name` | `String(15)` | Not Null | — |

**Application-level constraint:** 5 custom priorities per user.

### Relationships

| Parent | Child | Cardinality | On Delete |
|--------|-------|-------------|-----------|
| `users` | `tasks` | One-to-Many | CASCADE (orphan removal) |
| `users` | `custom_priorities` | One-to-Many | CASCADE (orphan removal) |

---

## Environment Configuration

All configuration is loaded from a `.env` file at the project root (not committed to version control). Copy `.env.example` as a starting point:

```bash
cp .env.example .env
```

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | **Yes** | — | Flask session signing key. Must be a long, random string. The app **will not start** without this. |
| `DATABASE_URL` | No | `sqlite:///todo.db` | SQLAlchemy connection URI. Defaults to a file-based SQLite database in the Flask instance folder. |
| `FLASK_ENV` | No | `production` | Set to `development` to enable debug features. |
| `FLASK_DEBUG` | No | `0` | Set to `1` to enable Flask's interactive debugger and auto-reloader. |

---

## Development & Deployment Guide

### Prerequisites

- Python 3.9+ installed and available on `PATH`
- `pip` package manager
- (Optional) `virtualenv` or Python's built-in `venv`

### Local Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd plan-spark

# 2. Create and activate a virtual environment
python -m venv venv

# Linux / macOS:
source venv/bin/activate

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and set a strong SECRET_KEY value

# 5. Initialize the database
flask init-db
# Or: python app.py (auto-creates tables on first run)

# 6. Start the development server
python app.py
```

The application will be available at **`http://localhost:5000`**.

### Production Deployment

The repository includes a `Procfile` for Heroku/Railway-style PaaS deployment:

```
web: gunicorn app:app
```

For production, ensure:
- `gunicorn` is installed (`pip install gunicorn`)
- `SECRET_KEY` is set to a cryptographically strong random value
- `FLASK_DEBUG` is `0` (or unset)
- The SQLite database file has appropriate filesystem permissions

---

## Project Structure

```

plan-spark/
│
├── static/
│   ├── css/
│   │   ├── landing.css                # Landing page styles
│   │   └── style.css                  # Master design system
│   │
│   ├── fonts/
│   │   ├── Inter-Variable.woff2       # Latin typeface
│   │   └── Vazirmatn-Variable.woff2   # Persian typeface
│   │
│   ├── icons/                         # SVG icons + PWA PNG icons
│   │
│   ├── js/
│   │   ├── analytics.js               # Chart.js analytics renderer
│   │   ├── jalaali.js                 # Vendored Jalali calendar library
│   │   ├── landing.js                 # Landing page interactions
│   │   └── main.js                    # Core dashboard engine
│   │
│   ├── manifest.json                  # PWA web app manifest
│   ├── offline.html                   # Offline fallback page (bilingual)
│   └── sw.js                          # Service Worker (cache-first)
│
├── templates/
│   ├── analytics.html                 # Analytics dashboard with Chart.js
│   ├── base.html                      # Master layout (header, nav, modals, scripts)
│   ├── index.html                     # Dashboard + task list + create/edit modals
│   ├── landing.html                   # Public marketing landing page
│   ├── login.html                     # Login form + password recovery modal
│   ├── register.html                  # Registration form with security words
│   └── settings.html                  # User preferences + custom priority manager
│
├── .env.example                       # Environment variable template
├── .gitignore                         # Git exclusion rules
├── app.py                             # Flask application factory (20 routes, 1 CLI command)
├── forms.py                           # WTForms form classes (7 forms)
├── models.py                          # SQLAlchemy ORM models
├── Procfile                           # PaaS deployment command (gunicorn)
├── requirements.txt                   # Python dependencies
├── translations.py                    # Bilingual FA/EN dictionary (~270 keys total)
└── utils.py                           # Date/time helpers, status logic, digit localization

```

### Route Map (21 routes)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/` | No | Landing page (unauthenticated) or redirect to dashboard |
| `GET` | `/dashboard` | Yes | Main task list with filters and search |
| `GET, POST` | `/register` | No | User registration with security words |
| `GET, POST` | `/login` | No | User login |
| `POST` | `/logout` | Yes | Session logout |
| `GET` | `/set-lang/<lang>` | No | Switch UI language (fa/en) |
| `POST` | `/tasks/create` | Yes | Create a new task |
| `POST` | `/tasks/<id>/edit` | Yes | Edit an existing task |
| `POST` | `/tasks/<id>/done` | Yes | Mark a task as done |
| `POST` | `/tasks/<id>/delete` | Yes | Delete a task |
| `GET` | `/priorities` | Yes | List custom priorities (JSON) |
| `POST` | `/priorities/create` | Yes | Create a custom priority |
| `POST` | `/priorities/<id>/delete` | Yes | Delete a custom priority |
| `GET, POST` | `/settings` | Yes | User preferences page |
| `GET` | `/analytics` | Yes | Analytics dashboard with charts |
| `POST` | `/api/recovery/check` | No | Check username for password recovery |
| `POST` | `/api/recovery/verify` | No | Verify security words |
| `POST` | `/api/recovery/reset` | No | Reset password after verification |
| `GET` | `/sw.js` | No | Serve Service Worker with no-cache headers |
| `GET` | `/manifest.json` | No | Serve PWA manifest |
| CLI | `flask init-db` | — | Create all database tables |

---

## License

© 2026 PlanSpark. All rights reserved.
