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
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEMO_USERS = [
    {
        "email": "admin@aiteebar.ai",
        "password": "admin123",
        "name": "Admin User",
        "role": UserRole.ADMIN,
    },
    {
        "email": "analyst@aiteebar.ai",
        "password": "analyst123",
        "name": "Analyst User",
        "role": UserRole.ANALYST,
    },
    {
        "email": "viewer@aiteebar.ai",
        "password": "viewer123",
        "name": "Viewer User",
        "role": UserRole.VIEWER,
    },
]


def seed_users(db: Session):
    """Seed demo users into the database."""
    
    # Check if users already exist
    existing_count = db.query(User).count()
    if existing_count > 0:
        print(f"Database already contains {existing_count} users. Skipping seed.")
        return

    users = []
    for user_data in DEMO_USERS:
        password_hash = pwd_context.hash(user_data["password"])
        user = User(
            id=str(uuid.uuid4()),
            email=user_data["email"],
            password_hash=password_hash,
            name=user_data["name"],
            role=user_data["role"],
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        users.append(user)

    db.add_all(users)
    db.commit()

    print(f"✓ Successfully seeded {len(users)} demo users!")
    print("\nDemo Credentials:")
    for user_data in DEMO_USERS:
        print(f"  Email: {user_data['email']}")
        print(f"  Password: {user_data['password']}")
        print(f"  Role: {user_data['role'].value}")
        print()


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
