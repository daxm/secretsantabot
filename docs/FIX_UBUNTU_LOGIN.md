# Fix for Ubuntu VM Admin Login Issue

## Problem
The admin login fails with "Invalid password" error because the `.env` file has `$$` (double dollar signs) in the password hash, but it should have single `$`.

## Root Cause
The previous documentation incorrectly stated that `.env` files need `$$` escaping. This is **only** true for inline environment variables in `docker-compose.yml`, NOT for `.env` files loaded via `env_file:`.

## Fix for Your Ubuntu VM

### Step 1: Check Current State
```bash
cd ~/containers/secretsantabot
docker-compose exec web printenv ADMIN_PASSWORD_HASH
```

**Expected problem:** You'll see `$$` (double dollar signs) in the output, like:
```
scrypt:32768:8:1$$S0wP6M8HlSIbQoNE$$94d11ebc...
```

### Step 2: Fix the .env File

**Option A: Generate New Hash (Recommended)**
```bash
# Generate a new hash with correct instructions
python dev-tools/generate_password_hash.py

# Copy the hash shown (with single $ signs)
# Edit .env and replace ADMIN_PASSWORD_HASH line
nano .env
```

**Option B: Fix Existing Hash Manually**
```bash
# Edit .env file
nano .env

# Find the line starting with ADMIN_PASSWORD_HASH=
# Change all $$ to single $
# Before: ADMIN_PASSWORD_HASH=scrypt:32768:8:1$$S0wP6M8HlSIbQoNE$$94d11ebc...
# After:  ADMIN_PASSWORD_HASH=scrypt:32768:8:1$S0wP6M8HlSIbQoNE$94d11ebc...
```

### Step 3: Rebuild Container
```bash
docker-compose down
docker-compose up --build -d
```

### Step 4: Verify Fix
```bash
# Check the environment variable in container
docker-compose exec web printenv ADMIN_PASSWORD_HASH

# Should now show SINGLE $ signs:
# scrypt:32768:8:1$S0wP6M8HlSIbQoNE$94d11ebc...
```

### Step 5: Test Login
1. Open browser to: http://your-server:5000/admin/login
2. Enter your password
3. Should work now!

## Why This Happened

Docker Compose handles `$$` differently depending on where it's used:

| Location | Dollar Sign | Why |
|----------|-------------|-----|
| `.env` file | Single `$` | `env_file:` directive passes values as-is |
| `docker-compose.yml` inline | Double `$$` | Variable interpolation needs escaping |

The old documentation confused these two, causing the login issue.

## Files Fixed in This Repo

✅ `dev-tools/generate_password_hash.py` - Now shows correct instructions
✅ `.env.example` - Updated with correct guidance
✅ `CLAUDE.md` - Fixed documentation
✅ `docs/TROUBLESHOOTING.md` - New comprehensive troubleshooting guide

## Need Help?

See `docs/TROUBLESHOOTING.md` for more detailed troubleshooting steps.

---

**After fixing, you can delete this file:** `rm docs/FIX_UBUNTU_LOGIN.md`
