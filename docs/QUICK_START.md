# Quick Start Guide - Security Update

## ⚠️ IMPORTANT: Action Required for Existing Users

If you were using this application before the security update, you **MUST** update your `.env` file.

## Quick Setup (5 minutes)

### Step 1: Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output (should look like: `a1b2c3d4e5f6...`)

### Step 2: Generate Password Hash

```bash
python dev-tools/generate_password_hash.py
```

Enter your desired admin password when prompted. Copy the entire hash (starts with `scrypt:...`)

### Step 3: Update .env File

Edit your `.env` file and update these lines:

```env
SECRET_KEY=<paste-the-secret-key-from-step-1>
ADMIN_PASSWORD_HASH=<paste-the-hash-from-step-2>
```

**Remove this line if present:**
```env
ADMIN_PASSWORD=...  # DELETE THIS LINE
FROM_EMAIL=...      # DELETE THIS LINE
```

### Step 4: Rebuild and Restart

**Using Docker:**
```bash
docker-compose down
docker-compose build
docker-compose up
```

**Using Python directly:**
```bash
pip install -e .
flask run
```

### Step 5: Test Login

1. Go to `http://localhost:5000/admin/login`
2. Enter the password you chose in Step 2
3. You should be able to log in successfully

## What Changed?

- ✅ **CSRF Protection**: Forms are now protected against attacks
- ✅ **Password Hashing**: Admin password is now securely hashed
- ✅ **Input Validation**: Email addresses and user inputs are validated
- ✅ **Rate Limiting**: Login attempts are limited to prevent brute force
- ✅ **Better Security**: Session cookies, logging, error handling improved

## Common Issues

### "Admin password not configured"
- Make sure you set `ADMIN_PASSWORD_HASH` (not `ADMIN_PASSWORD`) in `.env`
- The hash should start with `scrypt:32768:8:1$`

### "Invalid password" when trying to log in
- Run `python dev-tools/generate_password_hash.py` again
- Copy the ENTIRE hash including `scrypt:...`
- Make sure there are no extra spaces or line breaks

### Forms show "CSRF token missing"
- Clear your browser cookies
- Make sure you rebuilt the Docker container or reinstalled dependencies

### Email sending fails with "from address" error
- Remove `FROM_EMAIL` from your `.env` file
- The app now uses `SMTP_USERNAME` as the from address (Office 365 requirement)

## Need Help?

- See [SECURITY.md](SECURITY.md) for detailed security documentation
- See [README.md](../README.md) for full setup instructions
- See [CHANGELOG_SECURITY.md](CHANGELOG_SECURITY.md) for all changes

## Example .env File

```env
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=a1b2c3d4e5f6789...your-random-key-here

# Generate with: python generate_password_hash.py
ADMIN_PASSWORD_HASH=scrypt:32768:8:1$abc123...your-hash-here

# Office 365 Settings
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your-email@yourdomain.com
SMTP_PASSWORD=your-office365-password

# Optional: Set to True when using HTTPS
# SESSION_COOKIE_SECURE=False
```

## Security Checklist

Before going live:

- [ ] Generated strong SECRET_KEY
- [ ] Generated ADMIN_PASSWORD_HASH (not plain text!)
- [ ] Removed old ADMIN_PASSWORD line from .env
- [ ] Removed FROM_EMAIL line from .env
- [ ] Tested admin login
- [ ] Tested participant registration
- [ ] Verified email sending works
- [ ] .env file is NOT committed to git (check .gitignore)

## Still Using Plain Passwords?

**This is no longer supported.** You must migrate to password hashing:

1. Run `python dev-tools/generate_password_hash.py`
2. Enter your desired password
3. Update `.env` with the hash
4. Restart the application

Plain text passwords will be rejected with an error message.
