#!/usr/bin/env python3
"""
Helper script to generate password hashes for the Secret Santa Bot admin password.
Usage: python generate_password_hash.py
"""

import getpass

from werkzeug.security import generate_password_hash


def main():
    print("Secret Santa Bot - Password Hash Generator")
    print("=" * 50)
    print("\nThis script will generate a secure password hash for your admin password.")
    print("The hash will be used in your .env file as ADMIN_PASSWORD_HASH")
    print()

    password = getpass.getpass("Enter admin password: ")
    password_confirm = getpass.getpass("Confirm admin password: ")

    if password != password_confirm:
        print("\n❌ Error: Passwords do not match!")
        return

    if len(password) < 8:
        print(
            "\n⚠️  Warning: Password is less than 8 characters. Consider using a stronger password."
        )

    # Generate hash
    password_hash = generate_password_hash(password)

    print("\nPassword hash generated successfully!")
    print("\nAdd this line to your .env file:")
    print("-" * 80)
    print(f"ADMIN_PASSWORD_HASH={password_hash}")
    print("-" * 80)

    # Check for dollar signs and provide Docker Compose guidance
    if "$" in password_hash:
        escaped_hash = password_hash.replace("$", "$$")
        print("\n" + "=" * 80)
        print("IMPORTANT: Dollar Sign Handling")
        print("=" * 80)
        print("\n1. For .env files (loaded via env_file: in docker-compose.yml):")
        print("   → Use SINGLE $ signs (shown above)")
        print("\n2. For inline environment in docker-compose.yml:")
        print("   → Use DOUBLE $$ signs:")
        print(f"   ADMIN_PASSWORD_HASH={escaped_hash}")
        print("\n3. For running Python scripts directly (not in Docker):")
        print("   → Use SINGLE $ signs (shown above)")
        print("=" * 80)

    print("\nIMPORTANT: Keep this hash secure and never commit it to version control!")


if __name__ == "__main__":
    main()
