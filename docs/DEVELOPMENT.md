# Development Guide

## Setup

```bash
# Install with dev dependencies
pip install -e ".[dev]"
```

## Code Quality Tools

### Black (Formatter)
- Line length: 100
- Target: Python 3.11+
- Auto-formats code to consistent style

```bash
# Format all code
black app/ dev-tools/

# Check without formatting
black --check app/ dev-tools/
```

### Ruff (Linter)
- Fast Python linter
- Replaces flake8, isort, pyupgrade
- Line length: 100

```bash
# Lint and auto-fix
ruff check app/ dev-tools/ --fix

# Lint only (no fixes)
ruff check app/ dev-tools/
```

## Pre-Commit Workflow

Before committing:
```bash
# 1. Format code
black app/ dev-tools/

# 2. Lint and fix
ruff check app/ dev-tools/ --fix

# 3. Verify compilation
python -m py_compile app/*.py

# 4. Run tests (if any)
pytest  # when tests exist
```

## Configuration

All tool configuration in `pyproject.toml`:
- `[tool.black]` - Black formatter settings
- `[tool.ruff]` - Ruff linter settings
- `[tool.ruff.lint]` - Linting rules

## Database Migrations

When adding new columns:

1. Update models in `app/models.py`
2. Create migration script in `dev-tools/`
3. Test migration on fresh DB
4. Document in migration script

Example: `dev-tools/migrate_add_thank_you_email.py`

## Fresh Database

```bash
docker compose down
rm -f data/secretsanta.db*
docker compose up --build
```

SQLAlchemy auto-creates schema from models.

## Seeding Test Data

```bash
# From SQL file
python dev-tools/seed_database.py

# Interactive mode
python dev-tools/seed_database.py --interactive
```

## Version Updates

See `docs/VERSIONING.md` for version scheme.

Update both files together:
1. `pyproject.toml` - version field
2. `VERSION` - plain text file
