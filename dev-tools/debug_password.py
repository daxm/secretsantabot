#!/usr/bin/env python3
"""
Debug script to test admin password hash validation.
Usage: python dev-tools/debug_password.py
"""

import getpass
import os
import sys

from dotenv import load_dotenv
from werkzeug.security import check_password_hash

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load .env file
load_dotenv()


def main():
    print("Secret Santa Bot - Password Debug Tool")
    print("=" * 60)
    print()

    # Get the password hash from .env
    password_hash = os.getenv("ADMIN_PASSWORD_HASH", "")

    if not password_hash:
        print("❌ ERROR: ADMIN_PASSWORD_HASH is not set in .env file!")
        print("\nPlease run: python dev-tools/generate_password_hash.py")
        return

    print(f"✓ Found ADMIN_PASSWORD_HASH in .env file")
    print(f"\nHash preview: {password_hash[:30]}...")
    print(f"Hash length: {len(password_hash)} characters")

    # Check if hash has proper format
    if password_hash.startswith("scrypt:"):
        print("✓ Hash format looks correct (starts with 'scrypt:')")
    else:
        print("⚠️  Warning: Hash doesn't start with 'scrypt:' - may be incorrect format")

    # Count dollar signs
    dollar_count = password_hash.count("$")
    print(f"✓ Dollar sign count: {dollar_count}")
    if dollar_count == 4:
        print("  (Correct for Docker Compose - 4 dollar signs expected)")
    elif dollar_count == 2:
        print("  ⚠️  Only 2 dollar signs - you may need to escape them as $$")
        print("     This is required for Docker Compose .env files")
    else:
        print(f"  ⚠️  Unexpected dollar sign count: {dollar_count}")

    print("\n" + "=" * 60)
    print("Now let's test if your password matches this hash:")
    print()

    # Test password
    test_password = getpass.getpass("Enter the admin password to test: ")

    print("\nTesting password against hash...")
    if check_password_hash(password_hash, test_password):
        print("✓✓✓ SUCCESS! Password matches the hash!")
        print("\nThe hash is correct. If you still can't log in:")
        print("1. Make sure you're using the exact same password in the web form")
        print("2. Restart the Docker container: docker-compose down && docker-compose up --build")
        print("3. Clear your browser cache/cookies")
        print("4. Check the container logs: docker-compose logs -f")
    else:
        print("❌ FAILED! Password does NOT match the hash!")
        print("\nPossible causes:")
        print("1. You're entering a different password than the one used to generate the hash")
        print("2. There was a typo when generating or copying the hash")
        print("3. The hash in .env got corrupted (extra spaces, newlines, etc.)")
        print("\nRecommendation:")
        print("1. Run: python dev-tools/generate_password_hash.py")
        print("2. Use a simple, memorable password for testing")
        print("3. Carefully copy the ENTIRE hash line to .env")
        print("4. Rebuild container: docker-compose down && docker-compose up --build")


if __name__ == "__main__":
    main()
