# Security Improvements Changelog

## Summary

This update addresses critical security vulnerabilities identified in the Secret Santa Bot application. All critical and high-priority security issues have been resolved.

## Files Modified

### Core Application Files

1. **`app/__init__.py`**
   - Added Flask-WTF CSRF protection
   - Added Flask-Limiter for rate limiting
   - Configured session security (HttpOnly, SameSite, expiration)
   - Added logging configuration
   - Changed ADMIN_PASSWORD to ADMIN_PASSWORD_HASH
   - Added warning for weak SECRET_KEY

2. **`app/routes.py`**
   - Added email validation using email-validator
   - Added input validation for all form fields
   - Implemented password hashing with werkzeug.security
   - Added rate limiting (5 attempts/minute) on admin login
   - Sanitized email body content to prevent header injection
   - Replaced `print()` with proper logging
   - Added specific SMTP exception handling
   - Improved error messages

3. **`pyproject.toml`**
   - Added `flask-wtf>=1.2.0` for CSRF protection
   - Added `flask-limiter>=3.5.0` for rate limiting
   - email-validator was already present but now being used

### Template Files (All Forms)

4. **`app/templates/register.html`**
   - Added CSRF token
   - Added form field value preservation on validation errors

5. **`app/templates/admin_login.html`**
   - Added CSRF token

6. **`app/templates/admin_dashboard.html`**
   - Added CSRF token to all 4 forms:
     - Delete participant
     - Create matches
     - Send emails
     - Reset all

7. **`app/templates/reveal.html`**
   - Added CSRF token to toggle reveal form

### Configuration Files

8. **`.env.example`**
   - Updated to use ADMIN_PASSWORD_HASH instead of plain password
   - Added instructions for generating password hash
   - Added instructions for generating SECRET_KEY
   - Added SESSION_COOKIE_SECURE option
   - Added comprehensive security notes
   - Updated Office 365 SMTP documentation

### New Files Created

9. **`dev-tools/generate_password_hash.py`**
   - Helper script to generate secure password hashes
   - Interactive CLI tool with password confirmation
   - Provides formatted output for .env file

10. **`SECURITY.md`**
    - Comprehensive security documentation
    - Lists all vulnerabilities fixed
    - Setup instructions for security features
    - Best practices guide
    - Security checklist for deployment
    - Credential exposure remediation guide

11. **`CHANGELOG_SECURITY.md`** (this file)
    - Documents all security changes

### Documentation Updates

12. **`README.md`**
    - Updated features list to mention security improvements
    - Updated setup instructions for password hash generation
    - Added reference to SECURITY.md
    - Updated project structure section
    - Removed Gmail-specific instructions (now Office 365)

## Breaking Changes

⚠️ **IMPORTANT**: Existing deployments need to update their `.env` file:

### Required Actions

1. **Generate new SECRET_KEY**:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Generate ADMIN_PASSWORD_HASH**:
   ```bash
   python dev-tools/generate_password_hash.py
   ```

3. **Update .env file**:
   - Replace `ADMIN_PASSWORD=your-password` with `ADMIN_PASSWORD_HASH=<hash-from-step-2>`
   - Update `SECRET_KEY` with value from step 1
   - Remove `FROM_EMAIL` (no longer needed)

4. **Reinstall dependencies**:
   ```bash
   pip install -e .
   # or with Docker:
   docker-compose build
   ```

## Security Issues Fixed

### Critical (All Fixed ✅)

- ✅ Missing CSRF protection on all POST forms
- ✅ Plain text password storage
- ✅ No input validation
- ✅ Hardcoded default SECRET_KEY with warning
- ✅ FROM_EMAIL removed (was causing Office 365 auth issues)

### High (All Fixed ✅)

- ✅ Email validation not implemented (despite dependency)
- ✅ Email header injection vulnerability
- ✅ No rate limiting on admin login
- ✅ Poor exception handling (broad catch-all)

### Medium (All Fixed ✅)

- ✅ Session security not configured (HttpOnly, SameSite, expiration)
- ✅ Logging using print() instead of logging module
- ✅ No SMTP-specific exception handling

## Security Features Added

1. **CSRF Protection**: All forms now protected against Cross-Site Request Forgery
2. **Password Hashing**: Admin password now uses scrypt hashing algorithm
3. **Input Validation**: Email, name, and gift preference validation
4. **Rate Limiting**: 5 login attempts per minute per IP address
5. **Session Security**: HttpOnly, SameSite=Lax, 1-hour expiration
6. **Email Sanitization**: Prevents header injection attacks
7. **Proper Logging**: Security events logged with appropriate levels
8. **Error Handling**: Specific SMTP exception handling

## Migration Guide

### For Fresh Installations

Follow the updated README.md setup instructions.

### For Existing Deployments

1. **Backup your database**:
   ```bash
   cp data/secretsanta.db data/secretsanta.db.backup
   ```

2. **Pull the latest code**:
   ```bash
   git pull
   ```

3. **Update dependencies**:
   ```bash
   # If using Docker:
   docker-compose down
   docker-compose build

   # If using Python directly:
   pip install -e .
   ```

4. **Generate new credentials** (see "Required Actions" above)

5. **Update your .env file** with the new format

6. **Restart the application**:
   ```bash
   # Docker:
   docker-compose up

   # Python:
   flask run
   ```

7. **Test admin login** with your new password

## Testing Checklist

After updating, verify:

- [ ] Admin login works with new password hash
- [ ] Registration validates email addresses
- [ ] Registration rejects invalid inputs
- [ ] Forms are protected (try submitting without CSRF token - should fail)
- [ ] Rate limiting works (try 6 login attempts quickly)
- [ ] Email sending works (if configured)
- [ ] Session expires after 1 hour
- [ ] All forms on admin dashboard work
- [ ] Reveal page toggle works

## Future Security Enhancements (Not Yet Implemented)

### Medium Priority
- Email verification before registration confirmation
- Audit logging of all admin actions
- Database cascade delete rules
- Custom 404/500 error pages

### Low Priority
- Automated security testing
- Content Security Policy headers
- HTTPS enforcement/redirect
- Email resend functionality
- Backup/export functionality

## Support

For questions about these security changes, see:
- [SECURITY.md](SECURITY.md) - Detailed security documentation
- [README.md](README.md) - Setup instructions

## Credits

Security improvements based on OWASP Top 10 and Flask security best practices.
