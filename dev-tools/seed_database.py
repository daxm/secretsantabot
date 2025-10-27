#!/usr/bin/env python3
"""
Helper script to seed the Secret Santa database with test participants.

Usage (from dev-tools directory):
    python seed_database.py                    # Use seed_database.sql
    python seed_database.py --clear            # Clear DB first, then seed
    python seed_database.py --interactive      # Add participants interactively

Usage (from project root):
    python dev-tools/seed_database.py
"""

import sqlite3
import os
import sys
from pathlib import Path

# Get script directory and project root
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent

# Database path - try relative to script location first, then absolute
DATABASE_PATH = os.getenv('DATABASE_URL', str(PROJECT_ROOT / 'data' / 'secretsanta.db'))
if DATABASE_PATH.startswith('sqlite:///'):
    DATABASE_PATH = DATABASE_PATH.replace('sqlite:///', '')

def clear_database(conn):
    """Clear all data from the database."""
    cursor = conn.cursor()
    print("⚠️  Clearing database...")
    cursor.execute("DELETE FROM match")
    cursor.execute("DELETE FROM participant")
    cursor.execute("DELETE FROM settings")
    conn.commit()
    print("✅ Database cleared")

def seed_from_sql_file(conn, sql_file='seed_database.sql'):
    """Execute SQL commands from a file."""
    # Check if file exists in current directory, then in script directory
    sql_path = Path(sql_file)
    if not sql_path.exists():
        sql_path = SCRIPT_DIR / sql_file

    if not sql_path.exists():
        print(f"❌ Error: {sql_file} not found!")
        print(f"   Looked in: {Path.cwd()} and {SCRIPT_DIR}")
        print(f"   Create it or use --interactive mode")
        return False

    with open(sql_path, 'r') as f:
        sql_script = f.read()

    cursor = conn.cursor()
    try:
        cursor.executescript(sql_script)
        conn.commit()
        print(f"✅ Successfully seeded database from {sql_file}")
        return True
    except Exception as e:
        print(f"❌ Error executing SQL: {e}")
        return False

def interactive_seed(conn):
    """Interactively add participants."""
    print("\n📝 Interactive Participant Entry")
    print("=" * 50)
    print("Enter participant details (or press Ctrl+C to finish)\n")

    cursor = conn.cursor()
    count = 0

    try:
        while True:
            print(f"\n--- Participant #{count + 1} ---")
            name = input("Name: ").strip()
            if not name:
                break

            email = input("Email: ").strip()
            if not email:
                break

            gift_pref = input("Gift Preferences (optional): ").strip()

            try:
                cursor.execute(
                    "INSERT INTO participant (name, email, gift_preference) VALUES (?, ?, ?)",
                    (name, email, gift_pref if gift_pref else None)
                )
                conn.commit()
                count += 1
                print(f"✅ Added {name}")
            except sqlite3.IntegrityError:
                print(f"⚠️  Email {email} already exists, skipping...")

    except KeyboardInterrupt:
        print("\n\n✅ Finished adding participants")

    if count > 0:
        print(f"\n🎉 Added {count} participant(s) to database")
    else:
        print("\n❌ No participants added")

def show_participants(conn):
    """Display all participants in the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, gift_preference FROM participant ORDER BY id")
    participants = cursor.fetchall()

    if not participants:
        print("\n📭 No participants in database")
        return

    print(f"\n📋 Current Participants ({len(participants)}):")
    print("=" * 80)
    for p_id, name, email, gift_pref in participants:
        gift_text = gift_pref if gift_pref else "No preference"
        print(f"{p_id:3d}. {name:25s} {email:30s}")
        print(f"      Gift Preferences: {gift_text}")
    print("=" * 80)

def main():
    """Main function."""
    args = sys.argv[1:]

    # Check if database file exists
    if not os.path.exists(DATABASE_PATH):
        print(f"❌ Database not found at: {DATABASE_PATH}")
        print("   Run the application first to create the database:")
        print("   docker-compose up  OR  flask run")
        sys.exit(1)

    # Connect to database
    conn = sqlite3.connect(DATABASE_PATH)

    try:
        # Parse arguments
        clear_first = '--clear' in args or '-c' in args
        interactive = '--interactive' in args or '-i' in args
        show_help = '--help' in args or '-h' in args

        if show_help:
            print(__doc__)
            sys.exit(0)

        # Clear database if requested
        if clear_first:
            response = input("⚠️  Are you sure you want to clear the database? (yes/no): ")
            if response.lower() in ['yes', 'y']:
                clear_database(conn)
            else:
                print("❌ Cancelled")
                sys.exit(0)

        # Seed database
        if interactive:
            interactive_seed(conn)
        else:
            success = seed_from_sql_file(conn)
            if not success:
                print("\n💡 Tip: Use --interactive mode to add participants manually")
                print("   python seed_database.py --interactive")

        # Show results
        show_participants(conn)

    finally:
        conn.close()

if __name__ == "__main__":
    main()
