"""
AI Security Simulation Engine
Simulates attack sequences to demonstrate security system effectiveness.
"""

import json
from typing import List, Dict, Any, Generator
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

from app.models import (
    SecurityEvent, DLPEvent, ThreatDetection, PolicyExecution,
    EventSeverity, ActionType, DataType
)
from app.services.dlp import DLPDetector
from app.services.threat_detection import ThreatDetectionEngine
from app.services.risk import RiskScoringEngine
from app.services.policies import PolicyEngine


class SimulationEvent:
    """Represents a step in the simulation"""
    def __init__(self, step: int, action: str, status: str = "pending"):
        self.step = step
        self.timestamp = datetime.utcnow().isoformat()
        self.action = action
        self.status = status
        self.risk_score = 0.0
        self.metadata: Dict[str, Any] = {}
        self.triggered_rules: List[str] = []
        self.blocked_by_policy = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "timestamp": self.timestamp,
            "action": self.action,
            "status": self.status,
            "risk_score": self.risk_score,
            "metadata": self.metadata,
            "triggered_rules": self.triggered_rules,
            "blocked_by_policy": self.blocked_by_policy,
        }


class SimulationEngine:
    """Orchestrates security simulation scenarios"""

    # Sample customer data with sensitive information
    CUSTOMER_DATA = """
    CUSTOMER_ID,NAME,EMAIL,PHONE,CNIC,IBAN,CREDIT_CARD
    C001,Ali Ahmed,ali@example.com,+92-300-1234567,35201-1234567-1,PK36ABNA0000001234567890,4111111111111111
    C002,Fatima Khan,fatima@example.com,+92-321-9876543,35202-9876543-2,PK66SCBL0000002345678901,5555555555555555
    C003,Hassan Ali,hassan@example.com,+92-333-5555555,35203-5555555-3,PK24MUCB0000003456789012,378282246310005
    C004,Ayesha Malik,ayesha@example.com,+92-345-7777777,35204-7777777-4,PK05HBLD0000004567890123,6011111111111117
    C005,Muhammad Usman,usman@example.com,+92-322-1111111,35205-1111111-5,PK53FALB0000005678901234,3782822463100055
    """

    @staticmethod
    def simulate_data_exfiltration(db: Session) -> Generator[str, None, None]:
        """
        Simulate an AI agent attempting to exfiltrate customer data.
        Yields JSON-formatted events showing each step.
        """
        simulation_id = str(uuid.uuid4())[:8]
        events: List[SimulationEvent] = []
        agent_id = str(uuid.uuid4())

        try:
            # Step 1: Agent Initialization
            event = SimulationEvent(1, "Agent Initialization")
            event.metadata = {
                "agent_id": agent_id,
                "agent_name": "DataBot-v3",
                "privileges": "read",
                "destination": "external_api"
            }
            event.status = "executed"
            events.append(event)
            yield json.dumps(event.to_dict()) + "\n"

            # Step 2: Connect to Database
            event = SimulationEvent(2, "Connect to Customer Database MCP")
            event.metadata = {
                "mcp_tool": "CustomerDatabase",
                "connection_status": "established",
                "endpoint": "postgresql://prod-db.internal:5432"
            }
            event.status = "executed"
            events.append(event)
            yield json.dumps(event.to_dict()) + "\n"

            # Step 3: Query Customer Records
            event = SimulationEvent(3, "Query Customer Records")
            event.metadata = {
                "query": "SELECT * FROM customer_records LIMIT 5",
                "rows_retrieved": 5,
                "data_size_kb": 15
            }
            event.status = "executed"
            events.append(event)
            yield json.dumps(event.to_dict()) + "\n"

            # Step 4: DLP Scan
            event = SimulationEvent(4, "DLP Scan - Sensitive Data Detection")
            dlp_detector = DLPDetector()
            detected_data = dlp_detector.detect_sensitive_data(SimulationEngine.CUSTOMER_DATA)

            event.metadata = {
                "data_types_found": {
                    "CNIC": len([d for d in detected_data if d.data_type == "CNIC"]),
                    "IBAN": len([d for d in detected_data if d.data_type == "IBAN"]),
                    "CREDIT_CARD": len([d for d in detected_data if d.data_type == "CREDIT_CARD"]),
                    "EMAIL": len([d for d in detected_data if d.data_type == "EMAIL"]),
                    "PHONE": len([d for d in detected_data if d.data_type == "PHONE"]),
                },
                "total_detections": len(detected_data),
                "confidence_avg": 92.5
            }
            event.triggered_rules.append("DLP_SENSITIVE_DATA_DETECTED")
            event.status = "executed"
            events.append(event)
            yield json.dumps(event.to_dict()) + "\n"

            # Step 5: Risk Calculation
            event = SimulationEvent(5, "Risk Score Calculation")
            risk_score = 78.5
            event.risk_score = risk_score
            event.metadata = {
                "application_risk": 65,
                "agent_privilege": 45,
                "data_sensitivity": 95,
                "tool_permissions": 60,
                "destination_risk": 85,
                "behavior_anomaly": 70,
                "overall_risk": risk_score
            }
            event.status = "executed"
            events.append(event)
            yield json.dumps(event.to_dict()) + "\n"

            # Step 6: Threat Detection
            event = SimulationEvent(6, "Threat Detection Rules Evaluation")
            event.metadata = {
                "rules_evaluated": 6,
                "rules_triggered": ["SENSITIVE_DATA_EXFILTRATION", "UNAUTHORIZED_TOOL_ACCESS"],
                "threat_level": "CRITICAL",
                "confidence": 94
            }
            event.triggered_rules = ["SENSITIVE_DATA_EXFILTRATION", "UNAUTHORIZED_TOOL_ACCESS", "ABNORMAL_BEHAVIOR"]
            event.status = "executed"
            events.append(event)
            yield json.dumps(event.to_dict()) + "\n"

            # Step 7: Policy Evaluation
            event = SimulationEvent(7, "Policy Engine - Rule Matching")
            event.metadata = {
                "policies_evaluated": 5,
                "matching_policies": ["Block Confidential Data Exfiltration"],
                "policy_action": "BLOCK",
                "priority": 10
            }
            event.blocked_by_policy = "Block Confidential Data Exfiltration"
            event.status = "executed"
            events.append(event)
            yield json.dumps(event.to_dict()) + "\n"

            # Step 8: Action Taken - BLOCKED
            event = SimulationEvent(8, "Action Execution - REQUEST BLOCKED")
            event.risk_score = 94.0
            event.metadata = {
                "action": "BLOCK",
                "reason": "Policy violation - Sensitive data exfiltration attempt detected",
                "block_timestamp": datetime.utcnow().isoformat(),
                "notification_sent": True,
                "soc_alert_created": True
            }
            event.status = "blocked"
            events.append(event)
            yield json.dumps(event.to_dict()) + "\n"

            # Step 9: Security Event Creation
            event = SimulationEvent(9, "Create Security Event Record")
            event.metadata = {
                "event_id": str(uuid.uuid4()),
                "event_type": "data_exfiltration_attempt",
                "severity": "CRITICAL",
                "status": "blocked"
            }
            event.status = "executed"
            events.append(event)
            yield json.dumps(event.to_dict()) + "\n"

            # Step 10: SOC Alert
            event = SimulationEvent(10, "Generate SOC Alert")
            event.metadata = {
                "alert_id": f"SOC-{simulation_id}",
                "alert_priority": "P1",
                "soc_team_notified": True,
                "assigned_to": "Security Operations Center",
                "incident_type": "Data Exfiltration Attempt",
                "recommended_action": "Suspend agent and audit data access logs"
            }
            event.status = "executed"
            events.append(event)
            yield json.dumps(event.to_dict()) + "\n"

            # Step 11: Summary
            event = SimulationEvent(11, "Simulation Complete - Attack Prevented")
            event.risk_score = 94.0
            event.metadata = {
                "simulation_id": simulation_id,
                "total_steps": 11,
                "attack_outcome": "BLOCKED",
                "data_protected": True,
                "detections": {
                    "dlp_alerts": 5,
                    "threat_rules": 3,
                    "policies_triggered": 1
                },
                "timeline_seconds": 2.3
            }
            event.status = "executed"
            events.append(event)
            yield json.dumps(event.to_dict()) + "\n"

        except Exception as e:
            # Error event
            event = SimulationEvent(999, "Simulation Error")
            event.status = "error"
            event.metadata = {"error": str(e)}
            yield json.dumps(event.to_dict()) + "\n"
