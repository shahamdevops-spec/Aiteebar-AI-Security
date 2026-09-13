"""
Risk Factor Calculation - Computes individual risk factors from system state.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class FactorCalculation:
    """Result of calculating a single risk factor"""
    name: str
    value: float  # 0-100
    explanation: str
    contributing_factors: Dict[str, Any]
    weight: float


class RiskCalculator:
    """Calculates individual risk factors from system state"""

    @staticmethod
    def calculate_application_risk(app_data: Dict[str, Any]) -> FactorCalculation:
        """
        Calculate application risk (0-100).

        Based on:
        - Application risk_score from database
        - Risk level (LOW=20, MEDIUM=50, HIGH=75, CRITICAL=100)
        - Security assessment scores
        """
        contributing = {}

        # Get risk score from app data
        app_risk_score = float(app_data.get('risk_score', 0))
        contributing['risk_score'] = app_risk_score

        # Map risk level to baseline
        risk_level = app_data.get('risk_level', 'LOW')
        level_scores = {'LOW': 20, 'MEDIUM': 50, 'HIGH': 75, 'CRITICAL': 100}
        level_score = level_scores.get(risk_level, 50)
        contributing['risk_level'] = level_score

        # Consider security assessment dimensions
        privacy_score = float(app_data.get('privacy_score', 50))
        security_score = float(app_data.get('security_score', 50))
        data_handling_score = float(app_data.get('data_handling_score', 50))

        contributing['privacy_score'] = privacy_score
        contributing['security_score'] = security_score
        contributing['data_handling_score'] = data_handling_score

        # Calculate average (weighted more towards actual risk_score)
        overall = (
            app_risk_score * 0.4 +
            level_score * 0.3 +
            (100 - security_score) * 0.15 +  # Invert: high security = low risk
            (100 - privacy_score) * 0.10 +
            (100 - data_handling_score) * 0.05
        )

        explanation = f"Application '{app_data.get('name', 'Unknown')}' has {risk_level} risk level with {security_score:.0f}% security score"

        return FactorCalculation(
            name="Application Risk",
            value=min(100.0, max(0.0, overall)),
            explanation=explanation,
            contributing_factors=contributing,
            weight=0.25
        )

    @staticmethod
    def calculate_agent_privilege_level(agent_data: Dict[str, Any]) -> FactorCalculation:
        """
        Calculate agent privilege risk (0-100).

        Based on:
        - Number of connected tools
        - Tool permission scope
        - Data access level
        - Agent status
        """
        contributing = {}

        privilege_score = 0.0

        # Factor 1: Number of connected tools (more tools = higher risk)
        tools = agent_data.get('connected_tools', [])
        num_tools = len(tools)
        tool_risk = min(40.0, num_tools * 5)  # Max 40 points
        contributing['connected_tools_count'] = num_tools
        contributing['connected_tools_risk'] = tool_risk
        privilege_score += tool_risk

        # Factor 2: Data access scope
        data_access = agent_data.get('data_access', {})
        access_types = len(data_access.get('types', []))
        data_risk = min(30.0, access_types * 10)  # Max 30 points
        contributing['data_access_types'] = access_types
        contributing['data_access_risk'] = data_risk
        privilege_score += data_risk

        # Factor 3: Agent status
        status = agent_data.get('status', 'active')
        status_risk = 20.0 if status == 'active' else 5.0
        contributing['agent_status'] = status
        contributing['agent_status_risk'] = status_risk
        privilege_score += status_risk

        # Factor 4: Agent risk level
        agent_risk_level = agent_data.get('risk_level', 'LOW')
        level_scores = {'LOW': 10, 'MEDIUM': 30, 'HIGH': 60, 'CRITICAL': 100}
        level_risk = level_scores.get(agent_risk_level, 30)
        contributing['agent_risk_level'] = level_risk
        privilege_score += level_risk

        explanation = f"Agent with {num_tools} tools, {access_types} data types, status={status}"

        return FactorCalculation(
            name="Agent Privilege Level",
            value=min(100.0, privilege_score),
            explanation=explanation,
            contributing_factors=contributing,
            weight=0.20
        )

    @staticmethod
    def calculate_data_sensitivity(data_access: Dict[str, Any]) -> FactorCalculation:
        """
        Calculate data sensitivity risk (0-100).

        Based on:
        - Types of data accessed (CNIC, IBAN, PASSWORD, etc)
        - Sensitivity weights per data type
        - Frequency of access
        """
        contributing = {}

        # Data type severity weights
        severity_weights = {
            'CNIC': 95,
            'IBAN': 90,
            'PASSWORD': 98,
            'API_KEY': 92,
            'AWS_SECRET': 98,
            'CREDIT_CARD': 95,
            'EMAIL': 40,
            'PHONE': 35,
            'SOURCE_CODE': 70,
            'CONFIDENTIAL': 75,
        }

        accessed_types = data_access.get('types', [])
        contributing['data_types_accessed'] = accessed_types

        if not accessed_types:
            return FactorCalculation(
                name="Data Sensitivity Level",
                value=10.0,  # Low baseline if no sensitive data
                explanation="No sensitive data types accessed",
                contributing_factors=contributing,
                weight=0.25
            )

        # Calculate weighted average of accessed data types
        total_weight = 0.0
        weighted_sum = 0.0

        for data_type in accessed_types:
            weight = severity_weights.get(data_type, 50)
            weighted_sum += weight
            total_weight += 1
            contributing[f'{data_type}_sensitivity'] = weight

        average_sensitivity = weighted_sum / total_weight if total_weight > 0 else 0

        # Boost based on number of sensitive types (access to multiple = higher risk)
        num_sensitive = len([t for t in accessed_types if severity_weights.get(t, 0) >= 80])
        boost = min(15.0, num_sensitive * 5)

        final_score = min(100.0, average_sensitivity + boost)

        explanation = f"Accessing {len(accessed_types)} data types including: {', '.join(accessed_types[:3])}"

        return FactorCalculation(
            name="Data Sensitivity Level",
            value=final_score,
            explanation=explanation,
            contributing_factors=contributing,
            weight=0.25
        )

    @staticmethod
    def calculate_tool_permissions(tools_data: list) -> FactorCalculation:
        """
        Calculate tool permission risk (0-100).

        Based on:
        - Number of dangerous tools with access
        - Permission scope per tool
        - Tool risk levels
        """
        contributing = {}

        if not tools_data:
            return FactorCalculation(
                name="Tool Permission Scope",
                value=10.0,
                explanation="No tools configured",
                contributing_factors=contributing,
                weight=0.15
            )

        # Tool risk weights
        tool_risk_weights = {
            'CRITICAL': 95,
            'HIGH': 70,
            'MEDIUM': 40,
            'LOW': 15,
        }

        total_risk = 0.0

        for tool in tools_data:
            sensitivity = tool.get('data_sensitivity', 'MEDIUM')
            risk = tool_risk_weights.get(sensitivity, 40)
            total_risk += risk
            contributing[f"tool_{tool.get('name', 'unknown')}"] = risk

        average_risk = total_risk / len(tools_data) if tools_data else 0

        # Boost for dangerous permissions
        dangerous_count = len([t for t in tools_data if t.get('data_sensitivity') in ['CRITICAL', 'HIGH']])
        boost = min(20.0, dangerous_count * 10)

        final_score = min(100.0, average_risk + boost)
        contributing['num_tools'] = len(tools_data)
        contributing['dangerous_tools'] = dangerous_count

        explanation = f"Agent has access to {len(tools_data)} tools, {dangerous_count} with elevated permissions"

        return FactorCalculation(
            name="Tool Permission Scope",
            value=final_score,
            explanation=explanation,
            contributing_factors=contributing,
            weight=0.15
        )

    @staticmethod
    def calculate_destination_risk(connections: list) -> FactorCalculation:
        """
        Calculate destination/network risk (0-100).

        Based on:
        - Internal vs External destinations
        - Destination risk scores
        - Connection frequency
        """
        contributing = {}

        if not connections:
            return FactorCalculation(
                name="Destination Risk",
                value=10.0,
                explanation="No external connections detected",
                contributing_factors=contributing,
                weight=0.10
            )

        external_connections = [c for c in connections if not c.get('is_internal', True)]
        contributing['total_connections'] = len(connections)
        contributing['external_connections'] = len(external_connections)

        if not external_connections:
            return FactorCalculation(
                name="Destination Risk",
                value=15.0,
                explanation="Only internal connections detected",
                contributing_factors=contributing,
                weight=0.10
            )

        # Each external connection adds risk
        external_risk = min(60.0, len(external_connections) * 20)

        # Check destination risk scores
        destination_risk_sum = 0.0
        for conn in external_connections:
            dest_risk = conn.get('destination_risk_score', 50)
            destination_risk_sum += dest_risk

        avg_dest_risk = destination_risk_sum / len(external_connections) if external_connections else 0

        # Combine: external connections + destination risk
        final_score = (external_risk * 0.6) + (avg_dest_risk * 0.4)
        final_score = min(100.0, final_score)

        explanation = f"Agent connects to {len(external_connections)} external destination(s)"

        return FactorCalculation(
            name="Destination Risk",
            value=final_score,
            explanation=explanation,
            contributing_factors=contributing,
            weight=0.10
        )

    @staticmethod
    def calculate_behavior_anomaly_score(threats: list) -> FactorCalculation:
        """
        Calculate behavior anomaly risk (0-100).

        Based on:
        - Number of detected threats
        - Threat severity levels
        - Recent threat frequency
        """
        contributing = {}

        if not threats:
            return FactorCalculation(
                name="Behavior Anomaly Score",
                value=10.0,
                explanation="No behavioral anomalies detected",
                contributing_factors=contributing,
                weight=0.05
            )

        # Weight threats by severity
        severity_weights = {
            'CRITICAL': 100,
            'HIGH': 60,
            'MEDIUM': 30,
            'LOW': 10,
        }

        total_threat_score = 0.0
        severity_counts = {}

        for threat in threats:
            severity = threat.get('severity', 'MEDIUM')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

            weight = severity_weights.get(severity, 30)
            risk_score = threat.get('risk_score', weight)
            total_threat_score += risk_score

        contributing['threat_counts'] = severity_counts
        contributing['total_threats'] = len(threats)

        # Average threat score
        avg_threat_score = total_threat_score / len(threats) if threats else 0

        # Boost for recent threats (within last hour)
        now = datetime.utcnow()
        recent_threats = [
            t for t in threats
            if (now - t.get('timestamp', datetime.utcnow())).total_seconds() < 3600
        ]
        recency_boost = min(20.0, len(recent_threats) * 5)

        final_score = min(100.0, (avg_threat_score * 0.8) + recency_boost)
        contributing['recent_threats'] = len(recent_threats)

        explanation = f"Detected {len(threats)} behavioral anomalies in recent activity"

        return FactorCalculation(
            name="Behavior Anomaly Score",
            value=final_score,
            explanation=explanation,
            contributing_factors=contributing,
            weight=0.05
        )

    @staticmethod
    def calculate_dlp_detection_score(dlp_events: list) -> FactorCalculation:
        """
        Calculate DLP detection risk (implicit factor).

        Based on:
        - Number of active DLP detections
        - Severity of detections
        - Data types detected
        """
        contributing = {}

        if not dlp_events:
            return FactorCalculation(
                name="DLP Detection Score",
                value=5.0,
                explanation="No sensitive data detections",
                contributing_factors=contributing,
                weight=0.05
            )

        # Weight DLP events by severity
        severity_weights = {
            'CRITICAL': 95,
            'HIGH': 70,
            'MEDIUM': 40,
            'LOW': 15,
        }

        total_dlp_risk = 0.0
        severity_counts = {}
        data_types = set()

        for event in dlp_events:
            severity = event.get('severity', 'MEDIUM')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            data_types.add(event.get('data_type', 'UNKNOWN'))

            weight = severity_weights.get(severity, 40)
            confidence = event.get('confidence', 80)
            # Score based on both weight and confidence
            event_risk = (weight * confidence) / 100
            total_dlp_risk += event_risk

        contributing['dlp_event_counts'] = severity_counts
        contributing['total_events'] = len(dlp_events)
        contributing['data_types_detected'] = list(data_types)

        # Average DLP risk
        avg_dlp_risk = total_dlp_risk / len(dlp_events) if dlp_events else 0

        explanation = f"Detected {len(dlp_events)} sensitive data instances across {len(data_types)} data types"

        return FactorCalculation(
            name="DLP Detection Score",
            value=min(100.0, avg_dlp_risk),
            explanation=explanation,
            contributing_factors=contributing,
            weight=0.05
        )
