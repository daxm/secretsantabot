#!/usr/bin/env python3
"""
Helper script to generate password hashes for the Secret Santa Bot admin password.
Usage: python generate_password_hash.py
"""

from werkzeug.security import generate_password_hash
import getpass

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
        print("\n⚠️  Warning: Password is less than 8 characters. Consider using a stronger password.")

    # Generate hash
    password_hash = generate_password_hash(password)

    # Check for dollar signs (Docker Compose issue)
    if '$' in password_hash:
        # Escape dollar signs for Docker Compose
        escaped_hash = password_hash.replace('$', '$$')

        print("\nPassword hash generated successfully!")
        print("\nIMPORTANT: The hash contains $ signs which need to be escaped for Docker Compose.")
        print("\nAdd this line to your .env file (with $$ escaped):")
        print("-" * 80)
        print(f"ADMIN_PASSWORD_HASH={escaped_hash}")
        print("-" * 80)

        print("\nNOTE: If you're NOT using Docker, use this version instead (single $):")
        print("-" * 80)
        print(f"ADMIN_PASSWORD_HASH={password_hash}")
        print("-" * 80)
    else:
        print("\nPassword hash generated successfully!")
        print("\nAdd this line to your .env file:")
        print("-" * 80)
        print(f"ADMIN_PASSWORD_HASH={password_hash}")
        print("-" * 80)

    print("\nIMPORTANT: Keep this hash secure and never commit it to version control!")

if __name__ == "__main__":
    main()
