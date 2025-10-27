# Security Improvements

This document outlines the security enhancements made to the Secret Santa Bot application.

## Critical Security Fixes Implemented

### 1. CSRF Protection ✅
- **Issue**: All POST forms were vulnerable to Cross-Site Request Forgery attacks
- **Fix**: Implemented Flask-WTF CSRF protection on all forms
- **Impact**: Prevents attackers from tricking authenticated users into performing unwanted actions

### 2. Password Hashing ✅
- **Issue**: Admin password was stored and compared in plain text
- **Fix**: Implemented Werkzeug password hashing (scrypt algorithm)
- **Usage**: Run `python generate_password_hash.py` to create a secure password hash
- **Impact**: Protects admin credentials even if `.env` file is compromised

### 3. Input Validation ✅
- **Issue**: No validation on user inputs (name, email, gift preferences)
- **Fix**:
  - Email validation using `email-validator` library
  - Name length validation (max 100 characters)
  - Gift preference length validation (max 500 characters)
  - Empty field validation
- **Impact**: Prevents malicious or malformed data from entering the database

### 4. Email Header Injection Prevention ✅
- **Issue**: User names and preferences could contain newlines to inject email headers
- **Fix**: Sanitize all user inputs by removing newlines and control characters before email composition
- **Impact**: Prevents attackers from manipulating email headers (e.g., adding BCC recipients)

### 5. Session Security ✅
- **Issue**: Sessions had no expiration and insecure cookie flags
- **Fix**:
  - Session timeout set to 1 hour
  - HttpOnly flag enabled (prevents JavaScript access)
  - SameSite=Lax to prevent CSRF
  - Secure flag available for HTTPS deployments
- **Impact**: Reduces risk of session hijacking and XSS attacks

### 6. Rate Limiting ✅
- **Issue**: No protection against brute force password attempts
- **Fix**: Implemented Flask-Limiter with 5 login attempts per minute
- **Impact**: Prevents automated password guessing attacks

### 7. Proper Logging ✅
- **Issue**: Used `print()` statements that could expose sensitive data
- **Fix**: Replaced with Python logging module with appropriate log levels
- **Impact**: Better security auditing and no credential exposure in logs

### 8. Better Error Handling ✅
- **Issue**: Broad exception catching masked specific errors
- **Fix**: Catch specific SMTP exceptions separately
- **Impact**: Better error diagnosis without exposing sensitive information

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -e .
```

New dependencies added:
- `flask-wtf>=1.2.0` - CSRF protection
- `flask-limiter>=3.5.0` - Rate limiting

### 2. Generate Admin Password Hash

```bash
python dev-tools/generate_password_hash.py
```

Copy the generated hash to your `.env` file as `ADMIN_PASSWORD_HASH`.

### 3. Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output to your `.env` file as `SECRET_KEY`.

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and fill in all required values:

```bash
cp .env.example .env
# Edit .env with your values
```

### 5. Enable HTTPS (Production Only)

When deploying with HTTPS, add to `.env`:
```
SESSION_COOKIE_SECURE=True
```

## Remaining Security Considerations

### Medium Priority (Not Yet Implemented)

1. **Email Verification**: Users can register with any email without confirmation
2. **Audit Logging**: No trail of admin actions for security review
3. **Database Cascading Deletes**: Foreign keys don't have cascade rules
4. **HTTPS Enforcement**: No automatic redirect from HTTP to HTTPS
5. **Content Security Policy**: No CSP headers to prevent XSS

### Low Priority

1. **Unused Settings Model**: Clean up unused database table
2. **No Test Suite**: Security fixes should have automated tests
3. **No 404/500 Error Handlers**: Custom error pages needed

## Security Best Practices

1. **Never commit `.env` file** - It's in `.gitignore`, keep it there
2. **Use strong passwords** - Minimum 12 characters with mixed case, numbers, symbols
3. **Enable HTTPS** - Use a reverse proxy (nginx) with SSL/TLS certificates
4. **Regular updates** - Keep all dependencies updated for security patches
5. **Backup database** - Regular backups of `/app/data/secretsanta.db`
6. **Rotate credentials** - Change admin password and SMTP credentials periodically
7. **Monitor logs** - Review application logs for suspicious activity

## Credential Exposure Remediation

**IMPORTANT**: If you had a `.env` file committed to git with real credentials:

1. **Immediately rotate all exposed credentials**:
   - Generate new SECRET_KEY
   - Change admin password and generate new hash
   - Change SMTP password in Office 365

2. **Remove from git history**:
   ```bash
   # Use git-filter-repo or BFG Repo-Cleaner
   # This rewrites history - coordinate with all team members
   ```

3. **Verify `.gitignore`**:
   ```bash
   # Ensure .env is ignored
   echo ".env" >> .gitignore
   git add .gitignore
   git commit -m "Ensure .env is ignored"
   ```

## Security Checklist for Deployment

- [ ] Strong SECRET_KEY generated
- [ ] Admin password hashed (not plain text)
- [ ] `.env` file not in version control
- [ ] HTTPS enabled with valid certificate
- [ ] SESSION_COOKIE_SECURE=True set
- [ ] SMTP credentials secured
- [ ] All dependencies up to date
- [ ] Database backups configured
- [ ] Logs monitored regularly
- [ ] Rate limiting tested

## Reporting Security Issues

If you discover a security vulnerability, please email the maintainer directly rather than opening a public issue.

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Guide](https://flask.palletsprojects.com/en/latest/security/)
- [CSRF Protection](https://flask-wtf.readthedocs.io/en/stable/csrf.html)
- [Werkzeug Security Utilities](https://werkzeug.palletsprojects.com/en/latest/utils/#module-werkzeug.security)
