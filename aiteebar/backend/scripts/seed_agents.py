"""
Seed script to populate the database with AI agents.
Run: python scripts/seed_agents.py
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import AIAgent, AIApplication, AgentStatus, RiskLevel
import uuid

AGENTS_DATA = [
    {
        "name": "Customer Support Agent",
        "application_name": "Claude",
        "owner": "Support Team",
        "environment": "production",
        "risk_score": 62,
        "risk_level": RiskLevel.HIGH,
        "connected_tools": ["Customer DB MCP", "Email MCP", "Ticket System"],
        "data_access": {
            "customer_data": "read",
            "email": "write",
            "tickets": "read-write"
        },
        "status": AgentStatus.ACTIVE,
    },
    {
        "name": "Developer Agent",
        "application_name": "Claude",
        "owner": "Engineering Team",
        "environment": "development",
        "risk_score": 55,
        "risk_level": RiskLevel.MEDIUM,
        "connected_tools": ["GitHub MCP", "AWS MCP", "GitLab"],
        "data_access": {
            "repositories": "read-write",
            "aws_resources": "read",
            "deployment": "execute"
        },
        "status": AgentStatus.ACTIVE,
    },
    {
        "name": "Finance Assistant",
        "application_name": "ChatGPT",
        "owner": "Finance Team",
        "environment": "production",
        "risk_score": 78,
        "risk_level": RiskLevel.CRITICAL,
        "connected_tools": ["Finance API", "Database MCP", "Report Generator"],
        "data_access": {
            "financial_data": "read",
            "transactions": "read",
            "reports": "write"
        },
        "status": AgentStatus.ACTIVE,
    },
    {
        "name": "HR Assistant",
        "application_name": "Claude",
        "owner": "HR Department",
        "environment": "production",
        "risk_score": 65,
        "risk_level": RiskLevel.HIGH,
        "connected_tools": ["HR Systems", "Email MCP", "Employee Database"],
        "data_access": {
            "employee_records": "read",
            "hr_documents": "read-write",
            "communication": "write"
        },
        "status": AgentStatus.ACTIVE,
    },
    {
        "name": "Database Assistant",
        "application_name": "Claude",
        "owner": "Database Team",
        "environment": "staging",
        "risk_score": 72,
        "risk_level": RiskLevel.HIGH,
        "connected_tools": ["Database MCP", "Query Analyzer", "Backup System"],
        "data_access": {
            "databases": "read",
            "queries": "execute",
            "backups": "read-write"
        },
        "status": AgentStatus.ACTIVE,
    },
    {
        "name": "Data Analysis Agent",
        "application_name": "Claude",
        "owner": "Analytics Team",
        "environment": "production",
        "risk_score": 48,
        "risk_level": RiskLevel.MEDIUM,
        "connected_tools": ["Analytics MCP", "Cloud Storage", "Data Warehouse"],
        "data_access": {
            "raw_data": "read",
            "dashboards": "write",
            "cloud_storage": "read-write"
        },
        "status": AgentStatus.ACTIVE,
    },
    {
        "name": "Security Agent",
        "application_name": "Claude",
        "owner": "Security Team",
        "environment": "production",
        "risk_score": 58,
        "risk_level": RiskLevel.MEDIUM,
        "connected_tools": ["Log Analysis", "Threat Detection", "SIEM"],
        "data_access": {
            "security_logs": "read",
            "threat_data": "read",
            "alerts": "read-write"
        },
        "status": AgentStatus.ACTIVE,
    },
]


def seed_agents(db: Session):
    """Seed the database with AI agents."""

    # Check if agents already exist
    existing_count = db.query(AIAgent).count()
    if existing_count > 0:
        print(f"Database already contains {existing_count} agents. Skipping seed.")
        return

    agents = []
    for agent_data in AGENTS_DATA:
        # Find the application
        app = db.query(AIApplication).filter(
            AIApplication.name == agent_data["application_name"]
        ).first()

        if not app:
            print(f"⚠️  Application '{agent_data['application_name']}' not found, skipping agent")
            continue

        # Create last_activity as sometime in the last 7 days
        last_activity = datetime.utcnow() - timedelta(days=__import__('random').randint(0, 7))

        agent = AIAgent(
            id=str(uuid.uuid4()),
            application_id=str(app.id),
            name=agent_data["name"],
            owner=agent_data["owner"],
            environment=agent_data["environment"],
            risk_score=Decimal(str(agent_data["risk_score"])),
            risk_level=agent_data["risk_level"],
            connected_tools=agent_data["connected_tools"],
            data_access=agent_data["data_access"],
            status=agent_data["status"],
            last_activity=last_activity,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        agents.append(agent)

    db.add_all(agents)
    db.commit()

    print(f"✓ Successfully seeded {len(agents)} AI agents!")

    # Print summary
    print("\nAgents by environment:")
    environments = db.query(
        AIAgent.environment,
        __import__('sqlalchemy').func.count(AIAgent.id)
    ).group_by(AIAgent.environment).all()

    for env, count in environments:
        print(f"  - {env}: {count}")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_agents(db)
        print("\n✓ Agent seeding complete!")
    except Exception as e:
        print(f"✗ Error seeding agents: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
