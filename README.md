# Order Portal

A secure Flask web application that allows customers to log in and view their sales orders from a Microsoft SQL Server database. An admin user manages customer accounts through a dedicated admin panel.

---

## Overview

The Order Portal serves as a self-service interface for customers to view their orders stored in an MS SQL Server table (`IASSALITEM`). Each customer logs in with a username that maps to a `CUSTOMER` value in the SQL Server database. The admin account can create and delete customer users, and reset their passwords.

### Key Workflows

1. **Admin** runs the seed script to create the initial admin account.
2. **Admin** logs in and creates customer user accounts via the Admin Panel. Each username corresponds to a `CUSTOMER` value in the `IASSALITEM` table.
3. **Customers** log in with their credentials and click "Get Orders" to fetch their order data from SQL Server.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Client (Browser)                       │
│                                                                 │
│   Login Page ──► Orders Page ──► Get Orders (AJAX fetch)        │
│                  Admin Panel ──► Create/Delete Users            │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Reverse Proxy (Nginx)                         │
│              SSL termination, static file serving                │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTP (localhost)
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                   WSGI Server (Gunicorn / Waitress)              │
│                        wsgi.py entry point                       │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                       Flask Application                          │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌───────────┐                   │
│  │   Auth   │    │  Admin   │    │  Orders   │   ◄── Blueprints  │
│  │ Blueprint│    │ Blueprint│    │ Blueprint │                   │
│  └────┬─────┘    └────┬─────┘    └─────┬─────┘                   │
│       │               │                │                         │
│       ▼               ▼                ▼                         │
│  ┌─────────────────────────┐   ┌─────────────────┐               │
│  │   SQLite (app.db)       │   │  MS SQL Server  │               │
│  │   User accounts,        │   │  IASSALITEM     │               │
│  │   passwords, roles      │   │  (order data)   │               │
│  └─────────────────────────┘   └─────────────────┘               │
└──────────────────────────────────────────────────────────────────┘
```

### Dual-Database Design

| Database | Purpose | Technology |
|----------|---------|------------|
| **SQLite** (`app.db`) | Stores application users — usernames, hashed passwords, admin flag, timestamps | Flask-SQLAlchemy |
| **MS SQL Server** | Stores business data — the `IASSALITEM` table containing customer orders | pymssql (connection-pooled) |

This separation means the app only needs `SELECT` access to SQL Server, while user management is self-contained in the local SQLite database.

---

## Project Structure

```
order-portal/
├── run.py                      # Dev server entry point (debug=False)
├── wsgi.py                     # Production WSGI entry point
├── seed.py                     # Creates the initial admin user (interactive)
├── requirements.txt            # Python dependencies (pinned versions)
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
│
└── app/
    ├── __init__.py             # Application (create_app)
    ├── config.py               # All configuration (secrets, DB, sessions)
    ├── models.py               # SQLAlchemy User model
    ├── app.db                  # SQLite database (auto-created, gitignored)
    │
    ├── auth/                   # Authentication blueprint
    │   ├── __init__.py         #   Blueprint registration
    │   ├── routes.py           #   Login, logout, change password
    │   └── forms.py            #   WTForms with password validation
    │
    ├── admin/                  # Admin blueprint
    │   ├── __init__.py         #   Blueprint registration
    │   ├── routes.py           #   Create/delete users, reset passwords
    │   └── forms.py            #   WTForms with password complexity rules
    │
    ├── orders/                 # Orders blueprint
    │   ├── __init__.py         #   Blueprint registration
    │   ├── routes.py           #   Orders page and AJAX fetch endpoint
    │   └── queries.py          #   SQL Server queries with connection pool
    │
    ├── templates/              # Jinja2 HTML templates
    │   ├── base.html           #   Base layout (nav, flash messages)
    │   ├── auth/
    │   │   ├── login.html      #   Login page
    │   │   └── change_password.html
    │   ├── admin/
    │   │   └── dashboard.html  #   User management panel
    │   └── orders/
    │       └── orders.html     #   Order viewer with AJAX table
    │
    └── static/
        ├── css/
        │   └── style.css       # Full stylesheet (dark theme, glassmorphism)
        └── js/
            └── app.js          # Client-side JS (fetch orders, flash dismiss)
```

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Web Framework** | Flask | 3.1.1 |
| **Authentication** | Flask-Login | 0.6.3 |
| **ORM (User DB)** | Flask-SQLAlchemy | 3.1.1 |
| **Form Validation** | Flask-WTF (WTForms) | 1.2.2 |
| **Security Headers** | Flask-Talisman | 1.1.0 |
| **Rate Limiting** | Flask-Limiter | 3.10.1 |
| **DB Migrations** | Flask-Migrate (Alembic) | 4.1.0 |
| **SQL Server Client** | pymssql | 2.3.13 |
| **Password Hashing** | Werkzeug (scrypt/pbkdf2) | 3.1.3 |
| **User DB** | SQLite | Built-in |
| **Order Data DB** | Microsoft SQL Server | Any supported version |
| **Frontend** | Vanilla HTML/CSS/JS | — |
| **Font** | Inter (Google Fonts) | — |

---

## Security Features

| Feature | Implementation |
|---------|---------------|
| **Password Hashing** | Werkzeug `generate_password_hash` / `check_password_hash` (scrypt) |
| **CSRF Protection** | Flask-WTF CSRF tokens on all forms including logout and delete |
| **SQL Injection Prevention** | Parameterized queries (`%s` placeholders) in pymssql |
| **XSS Prevention** | Jinja2 auto-escaping + `escapeHtml()` in JavaScript |
| **Security Headers** | Flask-Talisman sets CSP, HSTS, X-Content-Type-Options, X-Frame-Options |
| **Session Security** | `HttpOnly`, `SameSite=Lax`, `Secure` cookie flags |
| **Session Timeout** | 2-hour `PERMANENT_SESSION_LIFETIME` |
| **Rate Limiting** | Login endpoint limited to 5 attempts per minute per IP |
| **Password Complexity** | Minimum 8 characters, requires uppercase, lowercase, digit, and special character |
| **Secret Key** | Loaded from `SECRET_KEY` env var; auto-generates random fallback |
| **Error Handling** | Generic error messages to clients; detailed exceptions logged server-side |
| **Audit Logging** | All login attempts, user management actions, and errors are logged |
| **Connection Pooling** | Module-level queue-based pool for SQL Server connections |

---

## Prerequisites

- **Python 3.10+**
- **Microsoft SQL Server** with the `IASSALITEM` table accessible
- **pip** (Python package manager)
- **Git** (optional, for version control)

---

## Local Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd order-portal
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the application

Edit `app/config.py` and set your MS SQL Server connection details:

```python
MSSQL_SERVER = 'your-server-address'
MSSQL_DATABASE = 'your-database-name'
MSSQL_USERNAME = 'your-sql-login'
MSSQL_PASSWORD = 'your-sql-password'
MSSQL_PORT = 1433
```

For local development over HTTP, set:

```python
SESSION_COOKIE_SECURE = False
```

### 5. Initialize the database

```bash
# Initialize migrations (first time only)
flask db init
flask db migrate -m "initial"
flask db upgrade
```

### 6. Create the admin user

```bash
python seed.py
```

You will be prompted to enter and confirm a password interactively.

### 7. Run the development server

```bash
python run.py
```

The app will be available at `http://localhost:5000`.

---

## Database Migrations

This project uses **Flask-Migrate** (Alembic) to manage the SQLite user database schema.

```bash
# Initialize migrations directory (first time only)
flask db init

# Generate a migration after model changes
flask db migrate -m "describe your change"

# Apply migrations to the database
flask db upgrade

# Rollback the last migration
flask db downgrade
```

> **Note**: The `migrations/` directory should be committed to version control so all environments apply the same schema changes.

---

## User Management

### Admin Account

The admin account is created once using the seed script:

```bash
python seed.py
```

- You will be prompted to enter and confirm a password.
- Password must be at least 8 characters.
- Running the script again is safe — it skips if the admin already exists.

### Customer Accounts

Customer accounts are managed through the **Admin Panel** (`/admin/`):

1. Log in as admin.
2. Navigate to "Admin Panel" in the navbar.
3. **Create User**: Enter the customer's `CUSTOMER` value (from `IASSALITEM`) as the username and set a password.
4. **Reset Password**: Click "Reset Password" next to any user.
5. **Delete User**: Click "Delete" next to any user (with confirmation).

> The username for each customer account **must match** the `CUSTOMER` column value in the `IASSALITEM` table in SQL Server. This is how the app maps a logged-in user to their orders.

---

## Configuration Reference

All configuration is in `app/config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `SECRET_KEY` | Auto-generated | Session signing key. Set via `SECRET_KEY` env var in production |
| `SQLALCHEMY_DATABASE_URI` | `sqlite:///app.db` | SQLite path for user accounts |
| `MSSQL_SERVER` | `localhost` | MS SQL Server hostname or IP |
| `MSSQL_DATABASE` | `TestDB` | SQL Server database name |
| `MSSQL_USERNAME` | `sa` | SQL Server login |
| `MSSQL_PASSWORD` | `Password@123` | SQL Server password |
| `MSSQL_PORT` | `1433` | SQL Server port |
| `SESSION_COOKIE_HTTPONLY` | `True` | Prevents JavaScript access to session cookie |
| `SESSION_COOKIE_SAMESITE` | `Lax` | CSRF protection for cookies |
| `SESSION_COOKIE_SECURE` | `True` | Cookies only sent over HTTPS. Set `False` for local HTTP dev |
| `PERMANENT_SESSION_LIFETIME` | `2 hours` | Session expiry after inactivity |
| `LOG_LEVEL` | `INFO` | Logging verbosity (via `LOG_LEVEL` env var) |

---

## Troubleshooting

### "Table not found" or "no such table: users"
The database hasn't been initialized. Run:
```bash
flask db upgrade
```
Or if migrations haven't been generated yet:
```bash
flask db init
flask db migrate -m "initial"
flask db upgrade
```

### Sessions reset on every restart
The `SECRET_KEY` environment variable is not set, so a random key is generated each time. Set a persistent key:
```bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

### "Connection refused" when fetching orders
Check that your MS SQL Server connection details in `app/config.py` are correct and that the server is reachable from the app host. Verify firewall rules allow connections on the configured port (default `1433`).

### Rate limit hit on login
The login endpoint is limited to 5 attempts per minute per IP. Wait 60 seconds and try again. If you're behind a reverse proxy, ensure `X-Forwarded-For` headers are passed correctly so rate limiting applies per real client IP rather than the proxy IP.

### Cookie / session issues in local development
If running locally over HTTP (not HTTPS), set `SESSION_COOKIE_SECURE = False` in `app/config.py`. The `Secure` flag prevents cookies from being sent over unencrypted connections.

---