# Troubleshooting Guide

## Admin Login Issues

### Problem: "Invalid password" error when logging in to admin panel

**Symptoms:**
- You generated a password hash with `generate_password_hash.py`
- Docker container starts successfully
- When trying to log in to `/admin/login`, you get "Invalid password" error
- Container logs show: `WARNING - Failed admin login attempt`

**Root Cause:**
Incorrect dollar sign escaping in the `.env` file. The password hash contains `$` characters that need different handling depending on where they're used.

**Solution:**

1. **Check what the container sees:**
   ```bash
   docker-compose exec web printenv ADMIN_PASSWORD_HASH
   ```

2. **If the hash is truncated** (e.g., only shows `scrypt:32768:8:1`):
   - Problem: Dollar signs in `docker-compose.yml` inline environment
   - Fix: Use `$$` instead of `$` OR move to `.env` file

3. **If the hash has double `$$`** (e.g., `scrypt:32768:8:1$$xyz$$abc...`):
   - Problem: Using `$$` in `.env` file (incorrect)
   - Fix: Change to single `$` in `.env` file

**Correct Usage:**

| Location | Dollar Sign Syntax | Example |
|----------|-------------------|---------|
| `.env` file (via `env_file:`) | Single `$` | `ADMIN_PASSWORD_HASH=scrypt:32768:8:1$abc$def` |
| `docker-compose.yml` inline | Double `$$` | `ADMIN_PASSWORD_HASH=scrypt:32768:8:1$$abc$$def` |
| Running Python locally | Single `$` | `ADMIN_PASSWORD_HASH=scrypt:32768:8:1$abc$def` |

**Step-by-Step Fix:**

```bash
# 1. Generate a fresh password hash
python dev-tools/generate_password_hash.py

# 2. Copy the hash shown (with single $ signs)

# 3. Edit .env file and paste the hash with single $ signs
nano .env  # or vim, etc.

# 4. Rebuild and restart container
docker-compose down
docker-compose up --build -d

# 5. Verify the container sees the correct hash
docker-compose exec web printenv ADMIN_PASSWORD_HASH
# Should show: scrypt:32768:8:1$xyz$abc... (single $ signs)

# 6. Try logging in again
```

**Why This Happens:**

Docker Compose has two ways to pass environment variables to containers:

1. **`env_file:` directive** (reads `.env` file):
   - Does NOT interpret `$$` as an escape sequence
   - Passes values as-is to the container
   - Use **single `$`** in `.env` file

2. **`environment:` directive** (inline in docker-compose.yml):
   - DOES interpret `$$` as escape for Docker's variable interpolation
   - Converts `$$` → `$` when passing to container
   - Use **double `$$`** in docker-compose.yml

## Email Issues

### Problem: Emails not sending

**Check these:**
1. `SMTP_USERNAME` must be full Office 365 email address
2. SMTP AUTH enabled in Microsoft 365 admin center
3. Check container logs: `docker-compose logs -f`

## CSRF Token Issues

**Solution:**
1. Clear browser cookies
2. Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
3. Rebuild container: `docker-compose down && docker-compose up --build`

## Database Issues

### Problem: Database locked or corrupted

**Solution:**
```bash
# Stop container
docker-compose down

# Backup current database
cp data/secretsanta.db data/secretsanta.db.backup

# Remove and let it recreate
rm data/secretsanta.db

# Start fresh
docker-compose up -d
```

## Rate Limiting

### Problem: "Too many requests" error on admin login

**Cause:** More than 5 failed login attempts in 1 minute

**Solution:**
- Wait 1 minute before trying again
- OR restart container: `docker-compose restart web`

## Worker Timeout Errors

### Problem: "[CRITICAL] WORKER TIMEOUT" in logs

**Symptoms:**
```
[CRITICAL] WORKER TIMEOUT (pid:7)
[ERROR] Error handling request (no URI read)
Worker exiting (pid: 7)
Booting worker with pid: 20
```

**Causes:**
- Browser connection checks or health checks taking too long
- Slow network requests
- Workers getting stuck on long-running operations

**Impact:**
- Usually harmless - worker automatically restarts
- May cause occasional slow page loads

**Solutions:**

**Already Fixed (as of 2025-10-28):**
- Timeout increased from 120s to 300s (5 minutes)
- Added graceful-timeout: 30s
- Added keep-alive: 5s

If still seeing issues:
1. **Check what's causing slow requests:**
   ```bash
   docker-compose logs -f web | grep "GET\|POST"
   ```

2. **Increase workers** (if you have available CPU/memory):
   ```dockerfile
   # Edit Dockerfile, change --workers 2 to --workers 4
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", ...]
   ```

3. **Add access logging** to see request patterns:
   ```dockerfile
   # Add to Dockerfile CMD:
   --access-logfile - --access-logformat '%(t)s %(r)s %(s)s %(b)s %(D)s'
   ```

**When to worry:**
- If happening frequently (more than once per hour)
- If causing actual request failures
- If workers never recover

## Container Won't Start

**Check these:**
1. Port 5000 not already in use: `lsof -i :5000` or `netstat -an | grep 5000`
2. `.env` file exists and has required variables
3. Check logs: `docker-compose logs web`

**Common fixes:**
```bash
# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# Check container status
docker-compose ps

# View logs
docker-compose logs -f web
```

## Permission Issues with data/ Directory

**Problem:** Container can't write to `data/secretsanta.db`

**Solution:**
```bash
# Make sure data directory exists and is writable
mkdir -p data
chmod 755 data

# If using SELinux, you may need:
chcon -Rt svirt_sandbox_file_t data/
```

## Still Having Issues?

1. **Enable debug logging:**
   - Add to docker-compose.yml environment: `- FLASK_DEBUG=1`
   - Restart: `docker-compose restart web`
   - Check logs: `docker-compose logs -f web`

2. **Test password hash manually:**
   ```bash
   docker-compose exec web python dev-tools/debug_password.py
   ```

3. **Check all environment variables:**
   ```bash
   docker-compose exec web printenv | grep -E 'SECRET_KEY|ADMIN|SMTP'
   ```

4. **Report issue:**
   - Include output from above commands
   - Include relevant logs
   - Create issue at: https://github.com/anthropics/claude-code/issues
