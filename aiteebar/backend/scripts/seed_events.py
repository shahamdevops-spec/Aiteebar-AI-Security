"""
Seed script to populate the database with security events and activities.
Run: python scripts/seed_events.py
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import (
    SecurityEvent,
    AgentActivity,
    AIApplication,
    AIAgent,
    EventSeverity,
    ActionType,
    ActivityStatus,
)
import uuid

EVENT_TYPES = [
    "Unauthorized API Access",
    "High Memory Usage",
    "Unusual Data Access Pattern",
    "Rate Limit Exceeded",
    "Failed Authentication",
    "Privilege Escalation Attempt",
    "Data Exfiltration Detected",
    "Configuration Change",
]

SEVERITY_LEVELS = [EventSeverity.LOW, EventSeverity.MEDIUM, EventSeverity.HIGH, EventSeverity.CRITICAL]

ACTIVITY_TYPES = [
    ActionType.EXECUTE,
    ActionType.READ,
    ActionType.WRITE,
    ActionType.CONNECT,
    ActionType.EXTERNAL_CALL,
]

ACTIVITY_STATUS_LIST = [ActivityStatus.PENDING, ActivityStatus.EXECUTED, ActivityStatus.BLOCKED]


def seed_events(db: Session):
    """Seed security events"""

    # Check if events already exist
    existing_count = db.query(SecurityEvent).count()
    if existing_count > 0:
        print(f"Database already contains {existing_count} events. Skipping seed.")
        return

    # Get applications
    apps = db.query(AIApplication).all()
    if not apps:
        print("No applications found. Please seed applications first.")
        return

    events = []
    for i in range(15):
        app = random.choice(apps)
        event = SecurityEvent(
            id=str(uuid.uuid4()),
            application_id=str(app.id),
            event_type=random.choice(EVENT_TYPES),
            severity=random.choice(SEVERITY_LEVELS),
            source=f"{app.name}",
            risk_score=random.uniform(10, 90),
        )
        events.append(event)

    db.add_all(events)
    db.commit()
    print(f"✓ Successfully seeded {len(events)} security events!")


def seed_activities(db: Session):
    """Seed agent activities"""

    # Check if activities already exist
    existing_count = db.query(AgentActivity).count()
    if existing_count > 0:
        print(f"Database already contains {existing_count} activities. Skipping seed.")
        return

    # Get agents
    agents = db.query(AIAgent).all()
    if not agents:
        print("No agents found. Please seed agents first.")
        return

    activities = []
    for i in range(20):
        agent = random.choice(agents)
        activity = AgentActivity(
            id=str(uuid.uuid4()),
            agent_id=str(agent.id),
            action_type=random.choice(ACTIVITY_TYPES),
            status=random.choice(ACTIVITY_STATUS_LIST),
            resource_name=f"Resource_{i}",
            risk_score=random.uniform(0, 100),
            agent_metadata={"operation": "automated", "version": "1.0"},
        )
        activities.append(activity)

    db.add_all(activities)
    db.commit()
    print(f"✓ Successfully seeded {len(activities)} agent activities!")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_events(db)
        seed_activities(db)
        print("\n✓ Event and activity seeding complete!")
    except Exception as e:
        print(f"✗ Error seeding events/activities: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
