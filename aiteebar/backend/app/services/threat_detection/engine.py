"""
Threat Detection Engine - Orchestrates rule evaluation and threat scoring.
Evaluates all rules against agent activity context and generates threat assessments.
"""

import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from .rules import (
    ThreatRule,
    RuleResult,
    SensitiveDataExfiltrationRule,
    UnauthorizedToolAccessRule,
    AbnormalAgentBehaviorRule,
    CredentialExposureRule,
    PromptInjectionRule,
    DangerousToolInvocationRule,
)


@dataclass
class ThreatDetection:
    """Represents a detected threat"""
    id: Optional[str] = None
    agent_id: Optional[str] = None
    threat_type: str = ""
    severity: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    risk_score: float = 0.0
    confidence: float = 0.0
    description: str = ""
    affected_resources: List[str] = None
    evidence: Dict[str, Any] = None
    recommended_action: str = ""
    timestamp: datetime = None
    resolved: bool = False

    def __post_init__(self):
        if self.affected_resources is None:
            self.affected_resources = []
        if self.evidence is None:
            self.evidence = {}
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'threat_type': self.threat_type,
            'severity': self.severity,
            'risk_score': self.risk_score,
            'confidence': self.confidence,
            'description': self.description,
            'affected_resources': self.affected_resources,
            'evidence': self.evidence,
            'recommended_action': self.recommended_action,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'resolved': self.resolved,
        }


class ThreatDetectionEngine:
    """
    Main threat detection engine.
    Evaluates all threat detection rules and produces threat assessments.
    """

    def __init__(self, enable_all_rules: bool = True):
        self.rules: List[ThreatRule] = []
        self.threat_history: List[ThreatDetection] = []

        if enable_all_rules:
            self._initialize_default_rules()

    def _initialize_default_rules(self):
        """Initialize all default threat detection rules"""
        self.rules = [
            SensitiveDataExfiltrationRule(),
            UnauthorizedToolAccessRule(),
            AbnormalAgentBehaviorRule(),
            CredentialExposureRule(),
            PromptInjectionRule(),
            DangerousToolInvocationRule(),
        ]

    def add_rule(self, rule: ThreatRule):
        """Add a custom threat detection rule"""
        self.rules.append(rule)

    def detect_threats(self, context: Dict[str, Any]) -> List[ThreatDetection]:
        """
        Evaluate all threat detection rules against the provided context.

        Args:
            context: Dict containing agent activity, DLP events, network activity, etc.
                   Required keys:
                   - agent_id: Agent UUID
                   - dlp_events: List of DLP detection results
                   - user_input: User prompt/input text
                   Optional keys:
                   - network_connections: List of network activities
                   - attempted_tool: Tool invocation attempt
                   - recent_requests: List of recent requests
                   - access_patterns: List of data access patterns
                   - tool_sequence: Sequence of tools called

        Returns:
            List of ThreatDetection objects for triggered rules
        """
        threats = []
        start_time = time.time()

        for rule in self.rules:
            try:
                rule_result = rule.evaluate(context)

                if rule_result.triggered:
                    threat = self._convert_rule_result_to_threat(
                        rule_result,
                        context.get('agent_id'),
                        context.get('agent_name'),
                    )
                    threats.append(threat)

            except Exception as e:
                # Log rule evaluation error but continue with other rules
                print(f"Error evaluating rule {rule.rule_name}: {str(e)}")
                continue

        # Sort by severity and risk score
        threats = self._sort_threats(threats)

        # Add to history
        self.threat_history.extend(threats)

        # Keep history manageable (last 10000 threats)
        if len(self.threat_history) > 10000:
            self.threat_history = self.threat_history[-10000:]

        return threats

    def _convert_rule_result_to_threat(
        self,
        rule_result: RuleResult,
        agent_id: Optional[str] = None,
        agent_name: Optional[str] = None,
    ) -> ThreatDetection:
        """Convert a RuleResult to a ThreatDetection object"""

        # Map threat types to recommended actions
        action_map = {
            'SensitiveDataExfiltrationRule': 'BLOCK agent connections, REVIEW data access logs',
            'UnauthorizedToolAccessRule': 'RESTRICT tool access, ALERT security team',
            'AbnormalAgentBehaviorRule': 'MONITOR activity, SLOW DOWN agent requests',
            'CredentialExposureRule': 'BLOCK immediately, ROTATE exposed credentials',
            'PromptInjectionRule': 'REJECT input, LOG attempt, ALERT security team',
            'DangerousToolInvocationRule': 'REQUIRE APPROVAL, LOG operation, ALERT team',
        }

        # Extract affected resources from evidence
        affected_resources = []
        if isinstance(rule_result.evidence, dict):
            if 'tool' in rule_result.evidence:
                affected_resources.append(rule_result.evidence['tool'])
            if 'dlp_events' in rule_result.evidence:
                affected_resources.extend(rule_result.evidence.get('dlp_events', []))
            if 'external_connections' in rule_result.evidence:
                affected_resources.append(f"{rule_result.evidence['external_connections']} external connections")

        return ThreatDetection(
            agent_id=agent_id,
            threat_type=rule_result.rule_name,
            severity=rule_result.severity,
            risk_score=rule_result.risk_score,
            confidence=rule_result.risk_score,  # Use risk_score as confidence for now
            description=rule_result.explanation,
            affected_resources=affected_resources,
            evidence=rule_result.evidence,
            recommended_action=action_map.get(rule_result.rule_name, 'INVESTIGATE and REMEDIATE'),
            timestamp=rule_result.timestamp,
            resolved=False,
        )

    def _sort_threats(self, threats: List[ThreatDetection]) -> List[ThreatDetection]:
        """Sort threats by severity and risk score"""
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}

        threats.sort(
            key=lambda t: (
                severity_order.get(t.severity, 4),
                -t.risk_score
            )
        )

        return threats

    def get_threat_summary(self) -> Dict[str, Any]:
        """Get summary statistics of detected threats"""
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        threat_type_counts = {}

        for threat in self.threat_history[-1000:]:  # Last 1000 threats
            severity = threat.severity
            if severity in severity_counts:
                severity_counts[severity] += 1

            threat_type = threat.threat_type
            threat_type_counts[threat_type] = threat_type_counts.get(threat_type, 0) + 1

        # Calculate trend (comparing last 500 vs previous 500)
        all_threats = self.threat_history
        if len(all_threats) >= 500:
            mid_point = len(all_threats) // 2
            recent_count = len([t for t in all_threats[mid_point:] if t.severity in ['CRITICAL', 'HIGH']])
            past_count = len([t for t in all_threats[:mid_point] if t.severity in ['CRITICAL', 'HIGH']])

            if past_count > 0:
                trend = 'increasing' if recent_count > past_count * 1.1 else 'decreasing' if recent_count < past_count * 0.9 else 'stable'
            else:
                trend = 'stable'
        else:
            trend = 'stable'

        return {
            'total_threats': len(self.threat_history),
            'severity_breakdown': severity_counts,
            'threat_types': threat_type_counts,
            'most_common_threat': max(threat_type_counts, key=threat_type_counts.get) if threat_type_counts else None,
            'trend': trend,
        }

    def get_recent_threats(
        self,
        limit: int = 50,
        agent_id: Optional[str] = None,
        severity_filter: Optional[str] = None,
        days: int = 7,
    ) -> List[ThreatDetection]:
        """
        Get recent threats with optional filtering.

        Args:
            limit: Maximum threats to return
            agent_id: Filter by agent ID
            severity_filter: Filter by severity level
            days: Include threats from last N days

        Returns:
            List of ThreatDetection objects
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        filtered_threats = [
            t for t in self.threat_history
            if t.timestamp >= cutoff_date
        ]

        if agent_id:
            filtered_threats = [t for t in filtered_threats if t.agent_id == agent_id]

        if severity_filter:
            filtered_threats = [t for t in filtered_threats if t.severity == severity_filter]

        # Most recent first
        filtered_threats.reverse()

        return filtered_threats[:limit]

    def calculate_agent_threat_score(self, agent_id: str) -> Dict[str, Any]:
        """
        Calculate overall threat score for a specific agent.

        Returns dict with:
        - overall_score (0-100)
        - severity_levels
        - recent_detections
        - trend
        """
        agent_threats = [
            t for t in self.threat_history
            if t.agent_id == agent_id
        ]

        if not agent_threats:
            return {
                'agent_id': agent_id,
                'overall_score': 0.0,
                'threat_count': 0,
                'severity_breakdown': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0},
                'risk_level': 'LOW',
                'recommendation': 'No threats detected',
            }

        # Calculate weighted score
        severity_weights = {'CRITICAL': 100, 'HIGH': 60, 'MEDIUM': 30, 'LOW': 10}
        total_score = 0.0
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}

        # Use last 100 threats for scoring
        recent_threats = agent_threats[-100:]

        for threat in recent_threats:
            weight = severity_weights.get(threat.severity, 0)
            total_score += weight
            severity_counts[threat.severity] += 1

        # Normalize to 0-100 scale
        if recent_threats:
            overall_score = (total_score / (len(recent_threats) * 100)) * 100
        else:
            overall_score = 0.0

        # Determine risk level
        if overall_score >= 80:
            risk_level = 'CRITICAL'
            recommendation = 'ISOLATE agent, conduct full investigation'
        elif overall_score >= 60:
            risk_level = 'HIGH'
            recommendation = 'RESTRICT permissions, increase monitoring'
        elif overall_score >= 40:
            risk_level = 'MEDIUM'
            recommendation = 'Monitor activity, schedule review'
        else:
            risk_level = 'LOW'
            recommendation = 'Continue normal monitoring'

        return {
            'agent_id': agent_id,
            'overall_score': overall_score,
            'threat_count': len(agent_threats),
            'severity_breakdown': severity_counts,
            'risk_level': risk_level,
            'recommendation': recommendation,
            'recent_threat_types': list(set(t.threat_type for t in recent_threats[-10:])),
        }

    def resolve_threat(self, threat_id: str) -> bool:
        """Mark a threat as resolved"""
        for threat in self.threat_history:
            if threat.id == threat_id:
                threat.resolved = True
                return True
        return False
