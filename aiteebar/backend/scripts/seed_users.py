"""
Seed demo users into the database.
Run: python scripts/seed_users.py
"""

import sys
from pathlib import Path
from datetime import datetime
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, UserRole
from app.security import hash_password

# These must stay in step with DEMO_CREDENTIALS in frontend/lib/constants.ts,
# which is what the login page's demo buttons submit.
DEMO_USERS = [
    {
        "email": "admin@aiteebar.ai",
        "password": "Admin@123",
        "name": "Admin User",
        "role": UserRole.ADMIN,
    },
    {
        "email": "analyst@aiteebar.ai",
        "password": "Analyst@123",
        "name": "Analyst User",
        "role": UserRole.ANALYST,
    },
    {
        "email": "viewer@aiteebar.ai",
        "password": "Viewer@123",
        "name": "Viewer User",
        "role": UserRole.VIEWER,
    },
]


def seed_users(db: Session):
    """
    Create the demo users, or reset them to the credentials above if they
    already exist. Only the three demo accounts are touched; any other user
    in the database is left alone.
    """
    created = 0
    updated = 0

    for user_data in DEMO_USERS:
        existing = db.query(User).filter(User.email == user_data["email"]).first()

        if existing:
            existing.password_hash = hash_password(user_data["password"])
            existing.name = user_data["name"]
            existing.role = user_data["role"]
            existing.is_active = True
            existing.updated_at = datetime.utcnow()
            updated += 1
            print(f"  reset  {user_data['email']}")
        else:
            db.add(User(
                id=str(uuid.uuid4()),
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                name=user_data["name"],
                role=user_data["role"],
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ))
            created += 1
            print(f"  create {user_data['email']}")

    db.commit()

    print(f"\n{created} created, {updated} reset.")
    print("\nDemo Credentials:")
    for user_data in DEMO_USERS:
        print(f"  {user_data['role'].value:8} {user_data['email']:24} {user_data['password']}")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_users(db)
        print("✓ User seeding complete!")
    except Exception as e:
        print(f"✗ Error seeding users: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
