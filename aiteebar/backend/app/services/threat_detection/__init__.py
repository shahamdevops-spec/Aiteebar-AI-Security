"""
Threat Detection Service Module.
Rule-based system for identifying risky AI agent behaviors.
"""

from .engine import ThreatDetectionEngine, ThreatDetection
from .rules import (
    SensitiveDataExfiltrationRule,
    UnauthorizedToolAccessRule,
    AbnormalAgentBehaviorRule,
    CredentialExposureRule,
    PromptInjectionRule,
    DangerousToolInvocationRule,
)

__all__ = [
    'ThreatDetectionEngine',
    'ThreatDetection',
    'SensitiveDataExfiltrationRule',
    'UnauthorizedToolAccessRule',
    'AbnormalAgentBehaviorRule',
    'CredentialExposureRule',
    'PromptInjectionRule',
    'DangerousToolInvocationRule',
]
