# Development Tools

Helper scripts for Secret Santa Bot development and testing.

## Files in this Directory

- **`generate_password_hash.py`** - Generate secure admin password hashes
- **`seed_database.py`** - Seed database with test participants
- **`seed_database.sql`** - SQL template for test participants

## Quick Reference

### Generate Admin Password
```bash
# From project root:
python dev-tools/generate_password_hash.py

# From dev-tools directory:
python generate_password_hash.py
```

### Seed Database
```bash
# From project root:
python dev-tools/seed_database.py

# From dev-tools directory:
python seed_database.py
```

---

# Database Seed Scripts

These scripts help you quickly populate the database with test participants, so you don't have to manually register everyone through the web interface each time you test.

## Quick Start

### Option 1: Edit the SQL file (Recommended)

1. **Edit `seed_database.sql`** with your test participants:

```sql
INSERT INTO participant (name, email, gift_preference) VALUES
('Your Name', 'your.email@example.com', 'Your preferences'),
('Friend Name', 'friend@example.com', 'Their preferences');
```

2. **Run the seed script**:

```bash
# From project root (recommended):
python dev-tools/seed_database.py

# From dev-tools directory:
cd dev-tools
python seed_database.py

# Or manually with sqlite3:
sqlite3 data/secretsanta.db < dev-tools/seed_database.sql
```

### Option 2: Interactive Entry

Add participants interactively without editing files:

```bash
python seed_database.py --interactive
```

You'll be prompted to enter each participant's details.

### Option 3: Use Docker

If your database is inside a Docker container:

```bash
# Copy the SQL file into the container
docker cp seed_database.sql secretsantabot-web-1:/app/seed_database.sql

# Execute it
docker exec secretsantabot-web-1 sqlite3 /app/data/secretsanta.db < /app/seed_database.sql

# Or use the Python script
docker exec -it secretsantabot-web-1 python seed_database.py
```

## Command Options

```bash
# Basic usage (run seed_database.sql)
python seed_database.py

# Clear database first, then seed
python seed_database.py --clear

# Interactive mode
python seed_database.py --interactive

# Help
python seed_database.py --help
```

## Usage Scenarios

### Scenario 1: Testing Registration Flow

Just use the web interface - register a few test participants normally.

### Scenario 2: Testing with Many Participants

1. Edit `seed_database.sql` with 10-15 participants
2. Run `python seed_database.py`
3. Go to admin dashboard and create matches

### Scenario 3: Iterative Testing

```bash
# Clear and reseed between tests
python seed_database.py --clear
python seed_database.py
```

### Scenario 4: Quick One-Off Test

```bash
# Add a few participants interactively
python seed_database.py --interactive
```

## Example seed_database.sql

Here's a template with 5 participants:

```sql
-- Clear existing data (optional)
DELETE FROM match;
DELETE FROM participant;

-- Insert test participants
INSERT INTO participant (name, email, gift_preference) VALUES
('Alice Johnson', 'alice@example.com', 'Books, coffee, cozy things'),
('Bob Smith', 'bob@example.com', 'Tech gadgets, gaming'),
('Carol Davis', 'carol@example.com', 'Art supplies, crafts'),
('David Wilson', 'david@example.com', 'Sports gear, fitness'),
('Eve Martinez', 'eve@example.com', 'Plants, home decor');

-- Verify
SELECT COUNT(*) as total FROM participant;
SELECT name, email FROM participant;
```

## Tips

1. **Real Emails**: You can use real emails in the seed file since it's not committed to git
2. **Clear First**: Use `--clear` flag to reset the database between tests
3. **Verify**: After seeding, check the admin dashboard to see all participants
4. **Matches**: The seed script only adds participants, not matches. Use the admin dashboard to create matches.

## Database Schema

For reference, the participant table structure:

```sql
CREATE TABLE participant (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    gift_preference TEXT
);
```

## Troubleshooting

### "Database not found"
- Make sure you've run the app at least once to create the database
- Check that `data/secretsanta.db` exists
- If using Docker, the database is at `/app/data/secretsanta.db` inside the container

### "Email already exists"
- You're trying to insert a participant with a duplicate email
- Either clear the database first with `--clear` or use different emails

### "seed_database.sql not found"
- The template file was created, but you may have moved it
- Use `--interactive` mode instead, or create a new SQL file

## Safety Notes

- ✅ These files are in `.gitignore` - safe to add real data
- ✅ The seed script doesn't delete data unless you use `--clear`
- ✅ You can always reset by deleting `data/secretsanta.db` and restarting the app
- ⚠️ Don't run seed scripts on production databases with real event data!

## Alternative: Manual SQL

If you prefer to run SQL commands directly:

```bash
# Open SQLite CLI
sqlite3 data/secretsanta.db

# Run commands
sqlite> INSERT INTO participant (name, email, gift_preference)
        VALUES ('Test User', 'test@example.com', 'Anything');
sqlite> SELECT * FROM participant;
sqlite> .quit
```
