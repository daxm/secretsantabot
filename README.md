# Secret Santa Bot

A simple Flask-based web application for organizing Secret Santa gift exchanges. Participants register, the admin creates matches, and everyone receives an email with their Secret Santa assignment. On reveal day, track which gifts have been exchanged!

## Features

- Participant registration with name, email, and gift preferences
- Automatic Secret Santa matching (ensures no one gets themselves)
- Email notifications to participants with their match
- Admin dashboard with password protection
- Reveal page to track gift exchanges on the big day
- SQLite database for simplicity (perfect for 10-15 people)
- Dockerized for easy deployment

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
└── README.md               # This file
```

## Setup

### 1. Clone and Configure

```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

Configure the following in `.env`:
- `SECRET_KEY`: A random secret key for Flask sessions
- `ADMIN_PASSWORD`: Password to access the admin dashboard
- Email settings (SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD, FROM_EMAIL)

For Gmail, you'll need to use an App Password:
1. Go to https://myaccount.google.com/apppasswords
2. Generate an app password
3. Use that password in `SMTP_PASSWORD`

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

- The admin password is stored in plain text in `.env` - suitable for small private events
- Email credentials are stored in `.env` - keep this file secure
- Sessions use Flask's session system with a secret key
- This is designed for small, trusted groups - not production security

## License

MIT License - feel free to use and modify as needed!
