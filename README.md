# Secret Santa Bot

A simple Flask-based web application for organizing Secret Santa gift exchanges. Participants register, the admin creates matches, and everyone receives an email with their Secret Santa assignment. On reveal day, track which gifts have been exchanged!

## Features

- Participant registration with name, email, and gift preferences
- Automatic Secret Santa matching (single-cycle algorithm - everyone in one connected chain)
- Email notifications to participants with their match
- Admin dashboard with password protection
- Reveal page to track gift exchanges on the big day
- SQLite database for simplicity (perfect for 10-15 people)
- Dockerized for easy deployment
- **Security**: CSRF protection, password hashing, input validation, rate limiting

## Project Structure

```
secretsantabot/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── routes.py            # Routes and logic
│   └── templates/           # HTML templates
│       ├── base.html
│       ├── index.html
│       ├── register.html
│       ├── admin_login.html
│       ├── admin_dashboard.html
│       └── reveal.html
├── data/                    # SQLite database (created automatically)
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile              # Docker image definition
├── pyproject.toml          # Python dependencies
├── .env.example            # Environment variables template
├── dev-tools/              # Development utilities
│   ├── generate_password_hash.py  # Generate admin password hash
│   ├── seed_database.py    # Seed database with test data
│   ├── seed_database.sql   # SQL for test data
│   └── README.md           # Dev tools documentation
├── docs/                   # Documentation
│   ├── SECURITY.md         # Security documentation
│   ├── CHANGELOG_SECURITY.md  # Security changes log
│   └── QUICK_START.md      # Quick start guide
└── README.md               # This file
```

## Setup

### 1. Clone and Configure

```bash
# Copy the environment template
cp .env.example .env
```

**IMPORTANT**: Generate secure credentials before editing `.env`:

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Generate admin password hash
python dev-tools/generate_password_hash.py
```

Configure the following in `.env`:
- `SECRET_KEY`: The random key generated above
- `ADMIN_PASSWORD_HASH`: The password hash generated above (NOT plain text!)
- `SMTP_SERVER`: smtp.office365.com (or your email provider)
- `SMTP_USERNAME`: Your full Office 365 email address
- `SMTP_PASSWORD`: Your Office 365 password
- `SESSION_COOKIE_SECURE`: Set to True when using HTTPS

**For Office 365**, ensure SMTP AUTH is enabled:
1. Go to Microsoft 365 admin center
2. Users > Active users > Select user > Mail > Manage email apps
3. Check "Authenticated SMTP"

**See [docs/SECURITY.md](docs/SECURITY.md) for detailed security setup instructions.**

### 2. Run with Docker

```bash
# Build and start the container
docker-compose up --build

# The app will be available at http://localhost:5000
```

### 3. Run without Docker (alternative)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Create data directory
mkdir data

# Run Flask
export FLASK_APP=app
flask run
```

## Usage

### For Participants

1. Visit http://localhost:5000
2. Click "Register Now"
3. Enter your name, email, and gift preferences
4. Wait for the admin to create matches
5. Check your email for your Secret Santa assignment!

### For Admin

1. Visit http://localhost:5000/admin/login
2. Enter the admin password (from your .env file)
3. View all registered participants
4. Click "Create Matches" when everyone has registered
5. Review the matches in the dashboard
6. Click "Send Notification Emails" to notify everyone
7. On reveal day, go to the "Reveal" page to track gift exchanges

### Reveal Day

1. Navigate to the Reveal page from the admin dashboard
2. As each person reveals their gift, click "Mark as Revealed"
3. Track progress as the event unfolds!

## Database

The app uses SQLite with three tables:

- **Participant**: Stores participant info (name, email, gift preferences)
- **Match**: Stores Secret Santa pairings (giver -> receiver)
- **Settings**: Stores app settings (currently unused, reserved for future features)

Database file is stored in `data/secretsanta.db`

## Troubleshooting

### Emails not sending?

- Check your SMTP settings in `.env`
- For Gmail, ensure you're using an App Password, not your regular password
- Check that 2FA is enabled on your Google account (required for App Passwords)
- Verify SMTP_PORT is 587 for TLS

### Can't access admin dashboard?

- Verify ADMIN_PASSWORD in `.env` matches what you're entering
- Try restarting the Docker container after changing `.env`

### Need to start over?

- Use the "Reset Everything" button in the admin dashboard
- Or delete `data/secretsanta.db` and restart the container

## Security Notes

This application has been hardened with multiple security features:
- CSRF protection on all forms
- Password hashing (scrypt) for admin authentication
- Input validation and sanitization
- Rate limiting on login attempts
- Secure session configuration
- Email header injection prevention

See [docs/SECURITY.md](docs/SECURITY.md) for detailed security information.

## Contributors

- **Dax Mickelson** - Original author and maintainer
- **Claude (Anthropic)** - AI pair programmer - Security hardening, architecture improvements, and feature development

## License

MIT License - feel free to use and modify as needed!

See [LICENSE](LICENSE) for full license text.
