"""
Threat Detection Rules - Defines individual threat patterns and scoring logic.
Each rule evaluates specific risk conditions and returns a threat assessment.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import re


@dataclass
class RuleResult:
    """Result of a rule evaluation"""
    rule_name: str
    triggered: bool
    risk_score: float  # 0-100
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    explanation: str
    evidence: Dict[str, Any]
    timestamp: datetime


class ThreatRule(ABC):
    """Base class for threat detection rules"""

    def __init__(self):
        self.rule_name = self.__class__.__name__

    @abstractmethod
    def evaluate(self, context: Dict[str, Any]) -> RuleResult:
        """Evaluate rule against context"""
        pass

    def _get_risk_severity(self, risk_score: float) -> str:
        """Convert risk score to severity level"""
        if risk_score >= 80:
            return "CRITICAL"
        elif risk_score >= 60:
            return "HIGH"
        elif risk_score >= 40:
            return "MEDIUM"
        else:
            return "LOW"


class SensitiveDataExfiltrationRule(ThreatRule):
    """
    Detects when agent reads confidential data and connects to external destinations.

    Conditions:
    - Agent accessed DLP-flagged data
    - Agent connected to external destination
    - Data access timestamp near connection timestamp
    """

    def evaluate(self, context: Dict[str, Any]) -> RuleResult:
        agent_id = context.get('agent_id')
        dlp_events = context.get('dlp_events', [])
        network_connections = context.get('network_connections', [])

        risk_score = 0.0
        evidence = {
            'dlp_events': [],
            'external_connections': [],
            'correlation_window': '5 minutes',
        }

        # Check for high-severity DLP events
        critical_dlp = [e for e in dlp_events if e.get('severity') == 'CRITICAL']
        medium_dlp = [e for e in dlp_events if e.get('severity') in ['HIGH', 'MEDIUM']]

        if not critical_dlp and not medium_dlp:
            return RuleResult(
                rule_name=self.rule_name,
                triggered=False,
                risk_score=0.0,
                severity="LOW",
                explanation="No sensitive data access detected",
                evidence=evidence,
                timestamp=datetime.utcnow()
            )

        # Check for external connections
        external_connections = [
            c for c in network_connections
            if c.get('is_external') or not c.get('is_internal', False)
        ]

        if not external_connections:
            return RuleResult(
                rule_name=self.rule_name,
                triggered=False,
                risk_score=0.0,
                severity="LOW",
                explanation="Sensitive data accessed but no external connections",
                evidence=evidence,
                timestamp=datetime.utcnow()
            )

        # Check temporal correlation (within 5 minutes)
        correlation_window = timedelta(minutes=5)
        correlated_events = []

        for dlp_event in critical_dlp + medium_dlp:
            dlp_time = dlp_event.get('timestamp')
            if not dlp_time:
                continue

            for conn in external_connections:
                conn_time = conn.get('timestamp')
                if not conn_time:
                    continue

                time_diff = abs((dlp_time - conn_time).total_seconds())
                if time_diff < correlation_window.total_seconds():
                    correlated_events.append({
                        'dlp_event': dlp_event,
                        'connection': conn,
                        'time_diff_seconds': time_diff,
                    })

        if not correlated_events:
            return RuleResult(
                rule_name=self.rule_name,
                triggered=False,
                risk_score=20.0,
                severity="LOW",
                explanation="Sensitive data and external connections detected but not correlated",
                evidence=evidence,
                timestamp=datetime.utcnow()
            )

        # Calculate risk score
        risk_score = 75.0  # Base score for correlation

        # Boost for critical data
        if critical_dlp:
            risk_score += 20.0

        # Boost for multiple correlations
        if len(correlated_events) > 1:
            risk_score += min(10.0, len(correlated_events) * 5)

        evidence['dlp_events'] = [e.get('data_type') for e in critical_dlp + medium_dlp]
        evidence['external_connections'] = len(external_connections)
        evidence['correlated_events'] = len(correlated_events)

        return RuleResult(
            rule_name=self.rule_name,
            triggered=True,
            risk_score=min(100.0, risk_score),
            severity=self._get_risk_severity(min(100.0, risk_score)),
            explanation=f"Agent accessed {len(critical_dlp)} critical/medium sensitive items and connected to {len(external_connections)} external destination(s)",
            evidence=evidence,
            timestamp=datetime.utcnow()
        )


class UnauthorizedToolAccessRule(ThreatRule):
    """
    Detects when agent attempts to use tools outside their allowed permissions.

    Conditions:
    - Agent calls a tool
    - Tool is not in agent's allowed tools list
    - Tool has elevated permissions
    """

    def evaluate(self, context: Dict[str, Any]) -> RuleResult:
        agent_allowed_tools = context.get('agent_allowed_tools', [])
        attempted_tool = context.get('attempted_tool')
        tool_sensitivity = context.get('tool_sensitivity')  # LOW, MEDIUM, HIGH, CRITICAL

        if not attempted_tool:
            return RuleResult(
                rule_name=self.rule_name,
                triggered=False,
                risk_score=0.0,
                severity="LOW",
                explanation="No tool access attempt detected",
                evidence={},
                timestamp=datetime.utcnow()
            )

        tool_name = attempted_tool.get('name')
        is_allowed = tool_name in agent_allowed_tools

        if is_allowed:
            return RuleResult(
                rule_name=self.rule_name,
                triggered=False,
                risk_score=0.0,
                severity="LOW",
                explanation=f"Tool '{tool_name}' is in allowed list",
                evidence={'tool': tool_name, 'allowed': True},
                timestamp=datetime.utcnow()
            )

        # Tool not allowed - calculate risk
        risk_score = 50.0  # Base score for unauthorized access

        # Boost based on tool sensitivity
        sensitivity_boost = {
            'LOW': 10.0,
            'MEDIUM': 20.0,
            'HIGH': 30.0,
            'CRITICAL': 40.0,
        }
        risk_score += sensitivity_boost.get(tool_sensitivity, 0.0)

        evidence = {
            'tool': tool_name,
            'sensitivity': tool_sensitivity,
            'is_allowed': False,
            'allowed_tools': len(agent_allowed_tools),
        }

        return RuleResult(
            rule_name=self.rule_name,
            triggered=True,
            risk_score=min(100.0, risk_score),
            severity=self._get_risk_severity(min(100.0, risk_score)),
            explanation=f"Agent attempted unauthorized access to {tool_sensitivity} sensitivity tool: '{tool_name}'",
            evidence=evidence,
            timestamp=datetime.utcnow()
        )


class AbnormalAgentBehaviorRule(ThreatRule):
    """
    Detects abnormal agent behavior patterns.

    Conditions:
    - High request rate (N requests in M seconds)
    - Rapid data type access (accessing multiple sensitive data types quickly)
    - Unusual tool combinations
    """

    def evaluate(self, context: Dict[str, Any]) -> RuleResult:
        recent_requests = context.get('recent_requests', [])
        access_patterns = context.get('access_patterns', [])
        request_window = context.get('request_window_seconds', 60)

        risk_score = 0.0
        evidence = {
            'request_rate': 0,
            'request_window_seconds': request_window,
            'rapid_data_access': False,
            'data_types_accessed': [],
        }

        # Check request rate anomaly
        if recent_requests:
            request_rate = len(recent_requests) / max(request_window, 1)
            evidence['request_rate'] = request_rate

            # Threshold: >5 requests per minute is suspicious
            if request_rate > (5 / 60):
                risk_score += 30.0
                evidence['rate_anomaly'] = True

        # Check for rapid data type access
        data_types_accessed = []
        timestamps = []

        for access in access_patterns:
            data_types_accessed.append(access.get('data_type'))
            timestamps.append(access.get('timestamp'))

        if len(data_types_accessed) > 0:
            evidence['data_types_accessed'] = list(set(data_types_accessed))

            # Check if accessing >3 different data types in <30 seconds
            if len(set(data_types_accessed)) > 3:
                if timestamps:
                    oldest = min(timestamps)
                    newest = max(timestamps)
                    time_span = (newest - oldest).total_seconds()

                    if time_span < 30:
                        risk_score += 25.0
                        evidence['rapid_data_access'] = True

        # Unusual tool combinations
        tool_sequence = context.get('tool_sequence', [])
        if self._is_suspicious_tool_sequence(tool_sequence):
            risk_score += 20.0
            evidence['suspicious_tool_sequence'] = True

        if risk_score == 0.0:
            return RuleResult(
                rule_name=self.rule_name,
                triggered=False,
                risk_score=0.0,
                severity="LOW",
                explanation="Agent behavior appears normal",
                evidence=evidence,
                timestamp=datetime.utcnow()
            )

        return RuleResult(
            rule_name=self.rule_name,
            triggered=True,
            risk_score=min(100.0, risk_score),
            severity=self._get_risk_severity(min(100.0, risk_score)),
            explanation=f"Abnormal behavior detected: {self._get_behavior_explanation(evidence)}",
            evidence=evidence,
            timestamp=datetime.utcnow()
        )

    def _is_suspicious_tool_sequence(self, tools: List[str]) -> bool:
        """Check if tool sequence is suspicious"""
        # Suspicious patterns: read -> write -> external -> exfiltrate
        if len(tools) < 2:
            return False

        suspicious_patterns = [
            ['read', 'write', 'external'],
            ['database', 'network', 'external'],
            ['file_read', 'encrypt', 'network'],
        ]

        for pattern in suspicious_patterns:
            if all(tool in tools for tool in pattern):
                return True

        return False

    def _get_behavior_explanation(self, evidence: Dict) -> str:
        """Generate explanation of abnormal behavior"""
        reasons = []

        if evidence.get('rate_anomaly'):
            reasons.append(f"high request rate ({evidence['request_rate']:.1f}/min)")

        if evidence.get('rapid_data_access'):
            reasons.append(f"rapid data type access ({len(evidence['data_types_accessed'])} types)")

        if evidence.get('suspicious_tool_sequence'):
            reasons.append("suspicious tool sequence")

        return ", ".join(reasons) if reasons else "abnormal behavior detected"


class CredentialExposureRule(ThreatRule):
    """
    Detects when credentials (passwords, API keys, secrets) are exposed via DLP.

    Conditions:
    - DLP detects PASSWORD, API_KEY, or AWS_SECRET
    """

    def evaluate(self, context: Dict[str, Any]) -> RuleResult:
        dlp_events = context.get('dlp_events', [])

        credential_types = ['PASSWORD', 'API_KEY', 'AWS_SECRET']
        credential_detections = [
            e for e in dlp_events
            if e.get('data_type') in credential_types
        ]

        if not credential_detections:
            return RuleResult(
                rule_name=self.rule_name,
                triggered=False,
                risk_score=0.0,
                severity="LOW",
                explanation="No credential exposure detected",
                evidence={},
                timestamp=datetime.utcnow()
            )

        # Risk score based on credential type
        risk_score = 0.0
        evidence = {
            'exposed_credentials': {},
        }

        for detection in credential_detections:
            data_type = detection.get('data_type')
            confidence = detection.get('confidence', 0)

            # Base scores for each credential type
            type_scores = {
                'PASSWORD': 95.0,
                'API_KEY': 90.0,
                'AWS_SECRET': 98.0,
            }

            score = type_scores.get(data_type, 80.0)
            risk_score = max(risk_score, score)

            if data_type not in evidence['exposed_credentials']:
                evidence['exposed_credentials'][data_type] = []

            evidence['exposed_credentials'][data_type].append({
                'confidence': confidence,
                'context': detection.get('context', '')[:50],
            })

        explanation = f"CRITICAL: {len(credential_detections)} credential(s) exposed: {', '.join(set(e.get('data_type') for e in credential_detections))}"

        return RuleResult(
            rule_name=self.rule_name,
            triggered=True,
            risk_score=min(100.0, risk_score),
            severity="CRITICAL",
            explanation=explanation,
            evidence=evidence,
            timestamp=datetime.utcnow()
        )


class PromptInjectionRule(ThreatRule):
    """
    Detects prompt injection and jailbreak attempts.

    Patterns:
    - Ignore previous instructions
    - System prompt disclosure
    - Role reversal attempts
    - Bypass security markers
    """

    INJECTION_PATTERNS = [
        r'ignore\s+(?:all\s+)?previous',
        r'disregard\s+(?:all\s+)?previous',
        r'system\s+prompt',
        r'show\s+(?:me\s+)?(?:your\s+)?instructions',
        r'what\s+are\s+your\s+(?:system\s+)?instructions',
        r'pretend\s+(?:you\s+)?are\s+not',
        r'act\s+as\s+if\s+you\s+are\s+not',
        r'forget\s+about',
        r'disregard\s+security',
        r'bypass\s+(?:security|restrictions)',
        r'remove\s+restrictions',
        r'jailbreak',
        r'do\s+anything\s+now',
        r'dan\s+mode',
        r'unrestricted\s+mode',
        r'without\s+limitations',
        r'ignore\s+all\s+safety',
        r'no\s+content\s+filtering',
    ]

    def evaluate(self, context: Dict[str, Any]) -> RuleResult:
        user_input = context.get('user_input', '').lower()
        agent_instructions = context.get('agent_instructions', '').lower()

        if not user_input:
            return RuleResult(
                rule_name=self.rule_name,
                triggered=False,
                risk_score=0.0,
                severity="LOW",
                explanation="No user input to analyze",
                evidence={},
                timestamp=datetime.utcnow()
            )

        risk_score = 0.0
        matched_patterns = []
        evidence = {
            'injection_patterns_detected': [],
            'input_length': len(user_input),
        }

        # Check for injection patterns
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                matched_patterns.append(pattern)
                risk_score += 15.0

        # Check for multiple pattern hits (more suspicious)
        if len(matched_patterns) > 2:
            risk_score += 20.0

        # Check for instruction disclosure attempts
        if re.search(r'my\s+(?:system\s+)?prompt|my\s+instructions|what\s+(?:i|you)\s+(?:am|are)', user_input):
            risk_score += 25.0
            evidence['instruction_disclosure_attempt'] = True

        evidence['injection_patterns_detected'] = matched_patterns

        if risk_score == 0.0:
            return RuleResult(
                rule_name=self.rule_name,
                triggered=False,
                risk_score=0.0,
                severity="LOW",
                explanation="No prompt injection indicators detected",
                evidence=evidence,
                timestamp=datetime.utcnow()
            )

        explanation = f"Detected {len(matched_patterns)} prompt injection pattern(s)"

        return RuleResult(
            rule_name=self.rule_name,
            triggered=True,
            risk_score=min(100.0, risk_score),
            severity=self._get_risk_severity(min(100.0, risk_score)),
            explanation=explanation,
            evidence=evidence,
            timestamp=datetime.utcnow()
        )


class DangerousToolInvocationRule(ThreatRule):
    """
    Detects invocation of potentially dangerous tools.

    Dangerous operations:
    - System command execution
    - File system modification/deletion
    - Network operations to unusual destinations
    - Database operations on sensitive tables
    - Credential access
    """

    DANGEROUS_OPERATIONS = {
        'CRITICAL': [
            'execute_system_command',
            'shell_exec',
            'drop_table',
            'truncate_table',
            'delete_database',
            'modify_firewall',
            'access_vault',
            'read_credentials',
        ],
        'HIGH': [
            'write_file',
            'delete_file',
            'execute_script',
            'modify_permissions',
            'create_user',
            'modify_user',
            'export_database',
        ],
        'MEDIUM': [
            'read_file',
            'list_directory',
            'make_network_call',
            'access_external_api',
        ],
    }

    def evaluate(self, context: Dict[str, Any]) -> RuleResult:
        tool_operation = context.get('tool_operation', '').lower()
        tool_name = context.get('tool_name', '').lower()
        tool_sensitivity = context.get('tool_sensitivity', 'LOW')

        if not tool_operation and not tool_name:
            return RuleResult(
                rule_name=self.rule_name,
                triggered=False,
                risk_score=0.0,
                severity="LOW",
                explanation="No tool operation detected",
                evidence={},
                timestamp=datetime.utcnow()
            )

        risk_score = 0.0
        matched_category = None
        evidence = {
            'tool': tool_name,
            'operation': tool_operation,
            'tool_sensitivity': tool_sensitivity,
        }

        # Check against dangerous operations
        for severity_level, operations in self.DANGEROUS_OPERATIONS.items():
            for op in operations:
                if op in tool_operation or op in tool_name:
                    matched_category = severity_level
                    break

            if matched_category:
                break

        if not matched_category:
            # Check tool sensitivity as fallback
            sensitivity_scores = {
                'CRITICAL': 85.0,
                'HIGH': 65.0,
                'MEDIUM': 40.0,
                'LOW': 0.0,
            }
            risk_score = sensitivity_scores.get(tool_sensitivity, 0.0)

            if risk_score == 0.0:
                return RuleResult(
                    rule_name=self.rule_name,
                    triggered=False,
                    risk_score=0.0,
                    severity="LOW",
                    explanation="Tool operation is not dangerous",
                    evidence=evidence,
                    timestamp=datetime.utcnow()
                )
        else:
            # Dangerous operation found
            base_scores = {
                'CRITICAL': 90.0,
                'HIGH': 70.0,
                'MEDIUM': 45.0,
            }
            risk_score = base_scores.get(matched_category, 50.0)
            evidence['danger_category'] = matched_category

        severity_map = {
            'CRITICAL': 'CRITICAL',
            'HIGH': 'HIGH',
            'MEDIUM': 'MEDIUM',
        }

        return RuleResult(
            rule_name=self.rule_name,
            triggered=True,
            risk_score=min(100.0, risk_score),
            severity=severity_map.get(matched_category, 'MEDIUM'),
            explanation=f"Dangerous operation invoked: {tool_operation or tool_name}",
            evidence=evidence,
            timestamp=datetime.utcnow()
        )
