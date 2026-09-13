"""
Initialize database by creating all tables.
Run this BEFORE seeding: python scripts/init_db.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import init_db

if __name__ == "__main__":
    try:
        print("🔨 Initializing database...")
        init_db()
        print("✓ Database initialized successfully!")
        print("   Now run: python scripts/seed_applications.py")
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
