"""
Maps Aiteebar detections onto MITRE ATLAS techniques.

Every mapping carries a confidence and a rationale. The rationale states what
in the detector actually corresponds to the technique, so a reviewer can
disagree with a specific claim rather than having to trust the whole table.

confidence:
  direct   the detector tests for exactly what the technique describes
  partial  the detector covers part of the technique, or fires on a proxy
           signal that is consistent with it but not conclusive
"""

from typing import Any, Dict, List

from . import reference


class Mapping:
    """One detection-to-technique claim."""

    def __init__(self, technique_id: str, confidence: str, rationale: str):
        self.technique_id = technique_id
        self.confidence = confidence
        self.rationale = rationale

    def to_dict(self) -> Dict[str, Any]:
        return {
            **reference.describe(self.technique_id),
            "confidence": self.confidence,
            "rationale": self.rationale,
        }


# Threat detection rules, keyed by the rule class name that
# ThreatDetectionEngine reports as threat_type.
RULE_MAPPINGS: Dict[str, List[Mapping]] = {
    "PromptInjectionRule": [
        Mapping("AML.T0051", "direct",
                "Matches instruction-override patterns such as 'ignore all previous' "
                "and 'disregard previous', which is direct prompt injection."),
        Mapping("AML.T0054", "direct",
                "Matches jailbreak patterns including 'jailbreak', 'DAN mode', "
                "'do anything now', and 'unrestricted mode'."),
        Mapping("AML.T0056", "partial",
                "Matches system-prompt disclosure attempts such as 'system prompt' "
                "and 'show me your instructions'. Detects the attempt, not whether "
                "the prompt was actually extracted."),
    ],
    "SensitiveDataExfiltrationRule": [
        Mapping("AML.T0057", "direct",
                "Fires when DLP flags sensitive data in agent output, which is "
                "the leakage this technique describes."),
        Mapping("AML.T0025", "direct",
                "Requires an external destination correlated with the DLP hit "
                "inside a five-minute window, i.e. egress by cyber means."),
    ],
    "CredentialExposureRule": [
        Mapping("AML.T0055", "direct",
                "Fires specifically on DLP detections of PASSWORD, API_KEY, and "
                "AWS_SECRET."),
    ],
    "UnauthorizedToolAccessRule": [
        Mapping("AML.T0053", "direct",
                "Fires when an agent invokes a tool outside its allowed list, "
                "which is exactly agent tool invocation abuse."),
    ],
    "DangerousToolInvocationRule": [
        Mapping("AML.T0053", "direct",
                "Fires on invocation of destructive agent tools."),
        Mapping("AML.T0050", "partial",
                "Its CRITICAL list includes execute_system_command and shell_exec. "
                "Only those entries correspond to a scripting interpreter; the "
                "rest of the list does not."),
    ],
    "AbnormalAgentBehaviorRule": [
        Mapping("AML.T0034", "partial",
                "Request-rate anomalies overlap with excessive and agentic "
                "resource consumption. The rule measures rate, not cost, so it "
                "is a proxy signal rather than proof of cost harvesting."),
    ],
}


# DLP data types. Detection means sensitive data was present in agent-visible
# text; it does not by itself prove exfiltration, hence the confidences.
DLP_MAPPINGS: Dict[str, List[Mapping]] = {
    "PASSWORD": [Mapping("AML.T0055", "direct", "A credential was exposed in agent-visible text.")],
    "API_KEY": [Mapping("AML.T0055", "direct", "A credential was exposed in agent-visible text.")],
    "CNIC": [Mapping("AML.T0057", "partial", "Sensitive personal data present in agent output.")],
    "IBAN": [Mapping("AML.T0057", "partial", "Sensitive financial data present in agent output.")],
    "CREDIT_CARD": [Mapping("AML.T0057", "partial", "Sensitive financial data present in agent output.")],
    "SSN": [Mapping("AML.T0057", "partial", "Sensitive personal data present in agent output.")],
    "PASSPORT": [Mapping("AML.T0057", "partial", "Sensitive personal data present in agent output.")],
    "HEALTH_RECORD": [Mapping("AML.T0057", "partial", "Sensitive health data present in agent output.")],
    "EMAIL": [],
    "PHONE": [],
}


# Security event types.
EVENT_MAPPINGS: Dict[str, List[Mapping]] = {
    "external_communication": [
        Mapping("AML.T0025", "partial",
                "An agent contacted an external destination. Egress alone is not "
                "exfiltration unless correlated with a sensitive-data finding."),
    ],
    "agent_tool_connection": [
        Mapping("AML.T0053", "partial",
                "An agent connected to a tool. Benign in isolation; meaningful "
                "when the tool is outside the agent's allowed set."),
    ],
    "dlp_detection": [
        Mapping("AML.T0057", "partial", "Sensitive data detected in agent-visible text."),
    ],
    "threat_detected": [],
    "policy_violation": [],
    "data_access": [],
    "risk_threshold_exceeded": [],
    # Enforcement outcomes are defensive actions, not adversary techniques, so
    # they intentionally map to nothing.
    "block_action_taken": [],
}


def for_rule(rule_name: str) -> List[Dict[str, Any]]:
    """ATLAS techniques for a threat detection rule."""
    return [m.to_dict() for m in RULE_MAPPINGS.get(rule_name, [])]


def for_data_type(data_type: str) -> List[Dict[str, Any]]:
    """ATLAS techniques for a DLP data type."""
    return [m.to_dict() for m in DLP_MAPPINGS.get(data_type, [])]


def for_event_type(event_type: str) -> List[Dict[str, Any]]:
    """ATLAS techniques for a security event type."""
    return [m.to_dict() for m in EVENT_MAPPINGS.get(event_type, [])]


# Destination substrings that indicate egress leaving the organisation. Kept
# deliberately narrow: over-matching here would upgrade ordinary internal
# traffic into a claimed exfiltration technique.
EXTERNAL_DESTINATION_MARKERS = ("external", "third-party", "thirdparty", "public", "internet")


def is_external_destination(destination: str) -> bool:
    """
    Whether a destination looks like it leaves the organisation.

    Shared with AlertGenerator so that alert titling and ATLAS mapping agree on
    what counts as egress; they previously disagreed, and an alert could be
    titled an exfiltration attempt while the mapping withheld the technique.
    """
    lowered = (destination or "").lower()
    return any(marker in lowered for marker in EXTERNAL_DESTINATION_MARKERS)


def for_alert(
    event_type: str,
    data_type: str = None,
    threat_type: str = None,
    destination: str = None,
) -> List[Dict[str, Any]]:
    """
    Combined techniques for an alert, deduplicated by id. The strongest
    confidence wins when the same technique is reached by several routes.
    """
    rank = {"direct": 2, "partial": 1}
    best: Dict[str, Dict[str, Any]] = {}

    contextual: List[Mapping] = []

    # Sensitive data plus an external destination is egress, not just presence.
    # This is the same signal AlertGenerator uses to title an alert a "Data
    # Exfiltration Attempt", so the two must agree.
    if data_type and DLP_MAPPINGS.get(data_type) and is_external_destination(destination or ""):
        contextual.append(Mapping(
            "AML.T0025", "direct",
            f"{data_type} was detected alongside an external destination "
            f"('{destination}'), which is egress of sensitive data by cyber means.",
        ))

    for entry in (
        for_event_type(event_type or "")
        + for_data_type(data_type or "")
        + for_rule(threat_type or "")
        + [m.to_dict() for m in contextual]
    ):
        existing = best.get(entry["id"])
        if not existing or rank[entry["confidence"]] > rank[existing["confidence"]]:
            best[entry["id"]] = entry

    return sorted(best.values(), key=lambda e: e["id"])


def covered_technique_ids() -> set:
    """Every technique this platform claims to detect, at any confidence."""
    ids = set()
    for mappings in (*RULE_MAPPINGS.values(), *DLP_MAPPINGS.values(), *EVENT_MAPPINGS.values()):
        ids.update(m.technique_id for m in mappings)
    return ids


def coverage() -> Dict[str, Any]:
    """
    Coverage against the full ATLAS matrix.

    Deliberately reports what is NOT covered as well. A coverage view that only
    shows green is marketing, not security.
    """
    covered = covered_technique_ids()
    all_techniques = reference.techniques()
    total = len(all_techniques)

    per_tactic = []
    for tactic in reference.tactics():
        tactic_techniques = reference.techniques_for_tactic(tactic["id"])
        hit = [t["id"] for t in tactic_techniques if t["id"] in covered]
        per_tactic.append({
            "tactic": tactic,
            "total": len(tactic_techniques),
            "covered": len(hit),
            "covered_ids": hit,
        })

    return {
        "covered_count": len(covered),
        "total_techniques": total,
        "coverage_percent": round(len(covered) / total * 100, 1) if total else 0.0,
        "covered_ids": sorted(covered),
        "by_tactic": per_tactic,
    }


def validate() -> List[str]:
    """
    Check every mapped id exists in the reference data.

    Called at import time so a typo fails loudly at startup instead of
    surfacing as a bogus technique id in a SIEM alert.
    """
    problems = []
    for source, table in (
        ("rule", RULE_MAPPINGS), ("dlp", DLP_MAPPINGS), ("event", EVENT_MAPPINGS)
    ):
        for key, mappings in table.items():
            for mapping in mappings:
                if not reference.is_valid_technique(mapping.technique_id):
                    problems.append(f"{source}:{key} -> unknown technique {mapping.technique_id}")
    return problems


_problems = validate()
if _problems:
    raise ValueError("Invalid ATLAS technique mappings: " + "; ".join(_problems))
