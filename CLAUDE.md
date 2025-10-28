# Claude Code Context - Secret Santa Bot

This file provides context for Claude Code to understand the current state of the Secret Santa Bot project.

## Project Overview

A Flask-based web application for organizing Secret Santa gift exchanges. Participants register, admin creates matches, and everyone receives email notifications with their assignments.

## Current State

### Production Status
- **Security hardened** - CSRF protection, password hashing, input validation, rate limiting
- **Production ready** - Running with Gunicorn WSGI server (not Flask dev server)
- **Modern UI** - Using Pico CSS for clean, responsive design
- **Email configured** - Office 365 SMTP (smtp.office365.com)
- **Single-cycle matching** - All participants in one connected chain (prevents A->B, B->A small loops)

### Key Technologies
- **Backend**: Flask 3.0+ with SQLAlchemy
- **Database**: SQLite (stored in `/data/secretsanta.db`)
- **Security**: Flask-WTF (CSRF), Flask-Limiter (rate limiting), Werkzeug (password hashing)
- **Email**: Office 365 SMTP with authentication
- **Frontend**: Pico CSS v2, semantic HTML, no JavaScript
- **Deployment**: Docker + Gunicorn
- **Code Quality**: Black (formatter), Ruff (linter)
- **Versioning**: `<major>.<yyyymmdd>.<patch>` format

## Project Structure

```
secretsantabot/
├── app/                          # Main application
│   ├── __init__.py              # Flask app factory, CSRF, rate limiter, logging
│   ├── models.py                # SQLAlchemy models (Participant, Match, Settings)
│   ├── routes.py                # All routes with validation & security
│   └── templates/               # Jinja2 templates with Pico CSS
│       ├── base.html            # Base template with navigation
│       ├── index.html           # Landing page
│       ├── register.html        # Participant registration
│       ├── admin_login.html     # Admin authentication
│       ├── admin_dashboard.html # Participant management, matching
│       └── reveal.html          # Gift exchange tracking
│
├── data/                        # Database directory (gitignored)
│   ├── .gitkeep                # Keeps directory in git
│   └── secretsanta.db          # SQLite database (created automatically)
│
├── dev-tools/                   # Development utilities
│   ├── generate_password_hash.py  # Generate admin password hashes
│   ├── seed_database.py         # Seed DB with test participants
│   ├── seed_database.sql        # SQL template for test data
│   └── README.md                # Dev tools documentation
│
├── docs/                        # Project documentation
│   ├── SECURITY.md              # Security features & setup guide
│   ├── CHANGELOG_SECURITY.md    # Security improvements log
│   ├── QUICK_START.md           # Quick setup guide
│   ├── VERSIONING.md            # Version scheme documentation
│   ├── DEVELOPMENT.md           # Dev tools and workflow guide
│   ├── TROUBLESHOOTING.md       # Common issues and solutions
│   └── FIX_UBUNTU_LOGIN.md      # Quick fix guide for login issues
│
├── .env                         # Environment variables (NOT in git)
├── .env.example                 # Template for .env
├── .gitignore                   # Git exclusions
├── docker-compose.yml           # Docker Compose configuration
├── Dockerfile                   # Container definition with Gunicorn
├── pyproject.toml               # Python dependencies & dev tools config
├── VERSION                      # Current version (<major>.<yyyymmdd>.<patch>)
├── README.md                    # Main documentation
└── CLAUDE.md                    # This file
```

## Important Files & Locations

### Configuration Files
- **`.env`** - Environment variables (SECRET_KEY, ADMIN_PASSWORD_HASH, SMTP credentials)
- **`.env.example`** - Template with instructions for generating secure values
- **`docker-compose.yml`** - Runs app with Gunicorn on port 5000
- **`Dockerfile`** - Production setup with Gunicorn WSGI server

### Core Application Files
- **`app/__init__.py`** - Flask factory, CSRF protection, rate limiting, session security
- **`app/routes.py`** - All routes with input validation, logging, error handling
- **`app/models.py`** - Participant, Match, Settings models

### Templates Location
All HTML templates are in `app/templates/`:
- Use Pico CSS v2 from CDN (no local CSS files)
- All forms have CSRF tokens
- Semantic HTML with `<article>`, `<hgroup>`, etc.

### Development Tools Location
All in `dev-tools/` directory:
- Password hash generator
- Database seeding scripts
- Works from both project root and dev-tools directory

### Documentation Location
All documentation (except README.md and CLAUDE.md) is in `docs/`:
- Security documentation
- Setup guides
- Changelog

## Key Implementation Details

### Security Features Implemented
1. **CSRF Protection** - Flask-WTF on all POST forms
2. **Password Hashing** - Werkzeug scrypt for admin password (ADMIN_PASSWORD_HASH in .env)
3. **Input Validation** - Email validator, length checks, sanitization
4. **Rate Limiting** - 5 login attempts per minute, global limits
5. **Session Security** - HttpOnly, SameSite=Lax, 1-hour expiration
6. **Email Sanitization** - Prevents header injection attacks
7. **Proper Logging** - Python logging module (not print statements)
8. **Specific Exception Handling** - SMTP errors caught specifically

### Email Configuration (Office 365)
- **Server**: smtp.office365.com
- **Port**: 587 with STARTTLS
- **Auth**: SMTP_USERNAME and SMTP_PASSWORD from .env
- **From Address**: Uses SMTP_USERNAME (Office 365 requirement)
- **Note**: FROM_EMAIL was removed (caused auth issues)

### Database Models
- **Participant**: name, email, gift_preference
- **Match**: giver_id, receiver_id, email_sent, revealed
- **Settings**: (exists but unused)

### Matching Algorithm
Single-cycle algorithm in `app/routes.py:102-135`:
- Shuffles participants randomly
- Creates chain: A->B->C->D->A
- Prevents small loops (A->B, B->A)
- Guaranteed valid with 2+ participants

### Admin Authentication
- Hashed password in .env (ADMIN_PASSWORD_HASH)
- Rate limited (5 attempts/min)
- Session expires after 1 hour
- Generate hash with: `python dev-tools/generate_password_hash.py`

## Running the Application

### Development (Local)
```bash
# Generate credentials first
python -c "import secrets; print(secrets.token_hex(32))"  # SECRET_KEY
python dev-tools/generate_password_hash.py                # ADMIN_PASSWORD_HASH

# Configure .env file
cp .env.example .env
# Edit .env with generated values

# Run with Docker (recommended)
docker-compose up --build

# Access at http://localhost:5000
```

### Production Deployment
- Uses Gunicorn WSGI server (not Flask dev server)
- 2 workers, 300-second timeout (5 minutes)
- Graceful timeout: 30 seconds
- Keep-alive: 5 seconds (reduces connection overhead)
- Set SESSION_COOKIE_SECURE=True for HTTPS
- Ensure SMTP AUTH is enabled in Microsoft 365 admin center

## Common Development Tasks

### Generate Admin Password Hash
```bash
python dev-tools/generate_password_hash.py
```

### Seed Database with Test Data
```bash
# Edit dev-tools/seed_database.sql with test participants
python dev-tools/seed_database.py
```

### View Logs
```bash
docker-compose logs -f
```

### Access Database
```bash
sqlite3 data/secretsanta.db
```

## Known Limitations & TODOs

### Not Yet Implemented
- Email verification (anyone can register with any email)
- Audit logging of admin actions
- Database backup/export functionality
- Email resend functionality
- Custom 404/500 error pages
- Exclusion list (prevent certain pairs)

### Design Decisions
- SQLite is sufficient for 10-15 people (small groups)
- No JavaScript (all server-rendered)
- Pico CSS from CDN (no build process)
- No email verification (trust-based for small groups)

## Troubleshooting

**See `docs/TROUBLESHOOTING.md` for comprehensive troubleshooting guide.**

Quick reference:

### Admin Login Issues
- **Most common:** Wrong dollar sign escaping in `.env` (use single `$`, not `$$`)
- Run: `docker-compose exec web printenv ADMIN_PASSWORD_HASH` to verify
- See full guide: `docs/TROUBLESHOOTING.md` → "Admin Login Issues"
- Hash should start with `scrypt:32768:8:1$` (single dollar sign)
- Rate limiting: max 5 attempts per minute

### Email Issues
- SMTP_USERNAME must be full Office 365 email address
- SMTP AUTH must be enabled in Microsoft 365 admin center
- Check container logs: `docker-compose logs -f`

### CSRF Token Issues
- Clear browser cookies and hard refresh
- Rebuild: `docker-compose down && docker-compose up --build`

### Database Location
- In Docker: `/app/data/secretsanta.db`
- Local: `data/secretsanta.db`

### Container Issues
- Rebuild from scratch: `docker-compose down -v && docker-compose build --no-cache && docker-compose up -d`
- Check logs: `docker-compose logs -f web`

## Project Status

**Status**: PRODUCTION READY ✓
**Last Reviewed**: 2025-10-27
**All Security Features**: Implemented and tested
**All Documentation**: Complete and accurate

## Recent Changes

### Latest Updates (2025-10-28)

**UX & Stability Improvements:**
- **Auto-focus password field** on admin login page (no more clicking to start typing)
- **Fixed Gunicorn worker timeouts** - Increased timeout to 300s, added graceful-timeout and keep-alive settings
- Settings prevent occasional "[CRITICAL] WORKER TIMEOUT" errors in logs

**CRITICAL BUG FIX - Admin Login Issue:**
- **Fixed incorrect password hash escaping guidance** that prevented admin login
- `.env` files must use **SINGLE `$`** signs (not `$$`)
- Only `docker-compose.yml` inline environment needs `$$`
- Updated `generate_password_hash.py` with correct instructions
- Updated `.env.example` with correct guidance
- Added `docs/TROUBLESHOOTING.md` with comprehensive troubleshooting guide
- **If you can't log in to admin, see `docs/TROUBLESHOOTING.md`**

1. **Three-Phase Workflow**
   - Registration Open → Matching Phase → Locked (after emails sent)
   - Can add participants and re-match until emails are sent
   - Registration auto-locks after emails sent
   - Admin dashboard shows current phase with color coding

2. **Thank You Email Feature**
   - When match marked as "revealed", receiver gets email
   - Email reveals their Secret Santa and encourages thank you
   - Includes giver's email address for easy response
   - `thank_you_email_sent` field prevents duplicate emails

3. **Code Quality & Versioning**
   - Added Black (code formatter) - line length 100
   - Added Ruff (linter) - replaces flake8, isort, pyupgrade
   - New versioning scheme: `<major>.<yyyymmdd>.<patch>`
   - Current version: 1.20251028.1
   - Created `VERSION` file and `docs/VERSIONING.md`
   - Created `docs/DEVELOPMENT.md` with tooling guide

4. **Database Schema**
   - Added `thank_you_email_sent` to Match model
   - Migration script: `dev-tools/migrate_add_thank_you_email.py`
   - Auto-creates from models on fresh install

### Previous Updates (2025-10-27)
1. **Project Reorganization**
   - Moved docs to `docs/` directory
   - Moved dev tools to `dev-tools/` directory
   - Updated all path references
   - Cleaned up root directory

2. **Production Readiness**
   - Switched from Flask dev server to Gunicorn
   - Removed FLASK_ENV=development
   - Added 2 workers with 120s timeout

3. **Frontend Modernization**
   - Added Pico CSS v2
   - Semantic HTML throughout
   - Responsive design
   - Purple gradient background preserved

4. **Security Hardening** (see docs/CHANGELOG_SECURITY.md)
   - CSRF protection on all forms
   - Password hashing (scrypt)
   - Input validation
   - Rate limiting
   - Session security
   - Email header injection prevention
   - Proper logging

5. **Package Configuration Fix**
   - Fixed pyproject.toml to properly exclude non-package directories
   - Added explicit package discovery settings

6. **Password Hash Dollar Sign Issue** (CORRECTED 2025-10-28)
   - Updated generate_password_hash.py with correct guidance
   - .env files use SINGLE $ (env_file: doesn't interpret $$)
   - docker-compose.yml inline environment uses DOUBLE $$
   - Fixed incorrect documentation that caused login failures

7. **UI/UX Improvements**
   - Added padding to main container (fixed cramped layout)
   - Fixed button widths (no longer full-width)
   - Improved spacing throughout

8. **Documentation Cleanup**
   - Fixed outdated Gmail references (now Office 365)
   - Fixed outdated ADMIN_PASSWORD references (now ADMIN_PASSWORD_HASH)
   - Added MIT LICENSE file
   - Added Contributors section

## Important Notes for Future Development

### Critical - Don't Break These:
1. **Single-cycle matching algorithm** (`app/routes.py:102-135`) - Ensures everyone is in one connected chain
2. **CSRF tokens on ALL POST forms** - Security requirement, all 7 forms have them
3. **Password hashing** - Always use ADMIN_PASSWORD_HASH (hashed), never plain text
4. **Email sanitization** - Prevents header injection (removes newlines in names/preferences)
5. **Dollar sign in password hashes**:
   - `.env` files: Use SINGLE `$` (env_file: directive doesn't escape `$$`)
   - `docker-compose.yml` inline: Use DOUBLE `$$` (Docker Compose variable interpolation)
   - Running locally: Use SINGLE `$`

### Project Conventions:
- All documentation in `docs/` directory (not root)
- Dev tools in `dev-tools/` directory
- Templates use Pico CSS v2 from CDN (minimal custom CSS)
- Use Python logging module (not print statements)
- Email validation with email-validator package
- Office 365 SMTP uses SMTP_USERNAME as From address (no FROM_EMAIL variable)
- Package discovery configured in pyproject.toml to avoid "Multiple top-level packages" error
- **Code formatting**: Black with 100-char line length
- **Linting**: Ruff (replaces flake8, isort, pyupgrade)
- **Versioning**: `<major>.<yyyymmdd>.<patch>` format in `pyproject.toml` and `VERSION`

### Known Working Solutions:
- **Button width issue**: Fixed with `width: auto !important;` in base.html
- **Container padding**: Main container has 2rem padding
- **CSRF protection**: Flask-WTF initialized in app/__init__.py
- **Rate limiting**: Flask-Limiter with 5 attempts/min on login
- **Session security**: HttpOnly, SameSite=Lax, 1-hour expiration

## Quick Reference Commands

```bash
# Generate secrets
python -c "import secrets; print(secrets.token_hex(32))"
python dev-tools/generate_password_hash.py

# Development
docker-compose up --build
docker-compose logs -f
docker-compose down

# Install dependencies locally
pip install -e .

# Database operations
python dev-tools/seed_database.py
python dev-tools/seed_database.py --interactive
sqlite3 data/secretsanta.db

# Access running container
docker exec -it secretsantabot-web-1 bash
docker exec -it secretsantabot-web-1 python dev-tools/seed_database.py
```

## Dependencies (pyproject.toml)

### Production Dependencies
```toml
flask>=3.0.0              # Web framework
flask-sqlalchemy>=3.1.1   # ORM
flask-wtf>=1.2.0          # CSRF protection
flask-limiter>=3.5.0      # Rate limiting
python-dotenv>=1.0.0      # Environment variables
email-validator>=2.1.0    # Email validation
gunicorn>=21.2.0          # Production WSGI server
```

### Dev Dependencies
```toml
black>=24.0.0             # Code formatter
ruff>=0.1.0               # Fast Python linter
```

Install with: `pip install -e ".[dev]"`

## Package Configuration

The `pyproject.toml` includes package discovery settings to avoid build errors:

```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["app*"]
exclude = ["data*", "dev-tools*", "docs*"]
```

This ensures only the `app` package is included when installing with `pip install -e .`

## Code Quality Tools

### Black (Code Formatter)
- Line length: 100 characters
- Target: Python 3.11+
- Configuration in `pyproject.toml` under `[tool.black]`

Usage:
```bash
# Format code
black app/ dev-tools/

# Check without formatting
black --check app/ dev-tools/
```

### Ruff (Linter)
- Fast all-in-one linter (replaces flake8, isort, pyupgrade)
- Line length: 100 characters
- Configuration in `pyproject.toml` under `[tool.ruff]`

Usage:
```bash
# Lint and auto-fix
ruff check app/ dev-tools/ --fix

# Lint only
ruff check app/ dev-tools/
```

### Pre-Commit Workflow
Before committing code:
1. Format: `black app/ dev-tools/`
2. Lint: `ruff check app/ dev-tools/ --fix`
3. Verify: `python -m py_compile app/*.py`

## Versioning

Format: `<major>.<yyyymmdd>.<patch>`

Example: `1.20251028.0` = Major version 1, released October 28, 2025, patch 0

### Version Files
- `pyproject.toml` - Primary source (line 3)
- `VERSION` - Plain text for scripts

### When to Increment
- **Patch** (third number): Bug fixes, docs, no breaking changes
- **Date** (middle): New features, enhancements, reset patch to 0
- **Major** (first): Breaking changes, architectural changes, reset date and patch

See `docs/VERSIONING.md` for full details.

---

## Comprehensive Review Completed

A full code and documentation review was completed on 2025-10-27. Results:

**Python Code**: ✓ All files compile without errors
**Templates**: ✓ All 7 POST forms have CSRF tokens
**Documentation**: ✓ All references accurate and up-to-date
**Configuration**: ✓ Dockerfile, docker-compose.yml, .env.example all correct
**Security**: ✓ All 8 critical security features implemented and tested
**Project Structure**: ✓ Clean, organized, properly .gitignored

**Issues Fixed During Review**:
- README.md: Updated ADMIN_PASSWORD → ADMIN_PASSWORD_HASH in troubleshooting
- README.md: Removed Gmail references, updated to Office 365

**Project Status**: PRODUCTION READY - No critical issues found

---

**Last Updated**: 2025-10-28
**Project Status**: Production Ready
**Current Version**: 1.20251028.1
**Last Full Review**: 2025-10-27 - PASSED