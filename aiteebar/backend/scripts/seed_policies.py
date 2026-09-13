"""
Seed example security policies.
Run: python scripts/seed_policies.py
"""

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Policy, PolicyAction, User

EXAMPLE_POLICIES = [
    {
        "name": "Block Confidential Data Exfiltration",
        "description": "An agent reading national ID data must not send it to an external destination.",
        "condition": {
            "entity_type": "agent",
            "triggers": [
                {"field": "data_type", "operator": "equals", "value": "CNIC"},
                {"field": "destination", "operator": "contains", "value": "external"},
            ],
            "logic": "AND",
        },
        "action": PolicyAction.BLOCK,
        "priority": 10,
    },
    {
        "name": "Warn on High-Risk Tool",
        "description": "Execute-level access to a database tool is unusual and worth flagging.",
        "condition": {
            "entity_type": "agent",
            "triggers": [
                {"field": "tool_name", "operator": "contains", "value": "Database"},
                {"field": "action_type", "operator": "equals", "value": "EXECUTE"},
            ],
            "logic": "AND",
        },
        "action": PolicyAction.WARN,
        "priority": 50,
    },
    {
        "name": "Require Approval for API Access",
        "description": "Outbound calls through an API tool need a human in the loop.",
        "condition": {
            "entity_type": "agent",
            "triggers": [
                {"field": "tool_name", "operator": "contains", "value": "API"},
                {"field": "action_type", "operator": "equals", "value": "EXTERNAL_CALL"},
            ],
            "logic": "AND",
        },
        "action": PolicyAction.REQUIRE_APPROVAL,
        "priority": 60,
    },
]


def seed_policies(db: Session):
    """Insert the example policies, skipping any that already exist by name."""
    owner = db.query(User).filter(User.role == "admin").first() or db.query(User).first()

    if not owner:
        print("No users found. Run scripts/seed_users.py first.")
        return

    created = 0
    for policy_data in EXAMPLE_POLICIES:
        exists = db.query(Policy).filter(Policy.name == policy_data["name"]).first()
        if exists:
            print(f"  skip   {policy_data['name']} (already exists)")
            continue

        db.add(Policy(
            id=str(uuid.uuid4()),
            name=policy_data["name"],
            description=policy_data["description"],
            condition=policy_data["condition"],
            action=policy_data["action"],
            priority=policy_data["priority"],
            enabled=True,
            created_by=owner.id,
        ))
        created += 1
        print(f"  create {policy_data['name']} -> {policy_data['action'].value}")

    db.commit()
    print(f"\nSeeded {created} policy(ies).")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_policies(db)
    except Exception as exc:
        print(f"Error seeding policies: {exc}")
        db.rollback()
    finally:
        db.close()
