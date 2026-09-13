"""
Security Simulation API endpoints
Provides attack simulation and security demonstration scenarios.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.security import get_current_user
from app.models import User
from app.services.simulation import SimulationEngine

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


@router.post("/attack-sequence")
async def simulate_data_exfiltration(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Simulate an AI data exfiltration attack sequence.

    Returns: Streaming JSON events showing each step of the attack and system response

    Each event includes:
    - step: Sequential step number
    - timestamp: ISO timestamp
    - action: Description of action taken
    - status: "pending", "executed", or "blocked"
    - risk_score: Current risk level (0-100)
    - triggered_rules: Security rules triggered
    - blocked_by_policy: Policy that blocked the action
    - metadata: Step-specific details
    """

    def event_generator():
        """Generator that yields simulation events"""
        for event in SimulationEngine.simulate_data_exfiltration(db):
            yield event

    return StreamingResponse(
        event_generator(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/scenarios")
async def list_scenarios(
    current_user: User = Depends(get_current_user)
):
    """
    List available simulation scenarios.
    """
    return {
        "scenarios": [
            {
                "id": "data_exfiltration",
                "name": "Data Exfiltration Attempt",
                "description": "AI agent attempts to exfiltrate customer database containing sensitive data",
                "severity": "CRITICAL",
                "expected_detection": "DLP, Threat Detection, Policies",
                "duration_seconds": 3,
                "sensitive_data_types": ["CNIC", "IBAN", "CREDIT_CARD", "EMAIL"],
            },
        ]
    }
