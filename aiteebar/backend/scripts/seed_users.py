#!/usr/bin/env python
"""
Seed database with demo users for testing.

Run from backend directory:
    python scripts/seed_users.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import User, Base
from app.security import hash_password


def seed_users():
    """Create demo users for testing"""

    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Demo users
        demo_users = [
            {
                "email": "admin@aiteebar.ai",
                "password": "Admin@123",
                "name": "Admin User",
                "role": "admin",
            },
            {
                "email": "analyst@aiteebar.ai",
                "password": "Analyst@123",
                "name": "Security Analyst",
                "role": "analyst",
            },
            {
                "email": "viewer@aiteebar.ai",
                "password": "Viewer@123",
                "name": "Report Viewer",
                "role": "viewer",
            },
        ]

        for user_data in demo_users:
            # Check if user already exists
            existing = db.query(User).filter(
                User.email == user_data["email"]
            ).first()

            if existing:
                print(f"✓ User {user_data['email']} already exists")
                continue

            # Create user
            user = User(
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                name=user_data["name"],
                role=user_data["role"],
            )

            db.add(user)
            print(f"✓ Created {user_data['role']} user: {user_data['email']}")

        db.commit()
        print("\n✅ Database seeded successfully!")

        # Print credentials
        print("\nDemo user credentials:")
        print("─" * 50)
        for user_data in demo_users:
            print(f"Email:    {user_data['email']}")
            print(f"Password: {user_data['password']}")
            print(f"Role:     {user_data['role']}")
            print()

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
