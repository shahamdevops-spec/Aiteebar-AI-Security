"""
Risk assessment service for calculating and explaining risk scores.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class RiskAssessmentService:
    """Service for risk assessment calculations and explanations"""

    # Dimension weights for overall score calculation
    DIMENSION_WEIGHTS = {
        "privacy": 0.20,
        "security": 0.25,
        "data_handling": 0.20,
        "enterprise_control": 0.15,
        "integration": 0.10,
        "permission": 0.10,
    }

    # Risk level thresholds
    RISK_THRESHOLDS = {
        "LOW": (0, 25),
        "MEDIUM": (26, 50),
        "HIGH": (51, 75),
        "CRITICAL": (76, 100),
    }

    @staticmethod
    def calculate_overall_score(dimensions: Dict[str, float]) -> float:
        """
        Calculate overall risk score from dimension scores using weighted average.

        Args:
            dimensions: Dict with keys like 'privacy', 'security', etc.

        Returns:
            Overall risk score (0-100)
        """
        if not dimensions:
            return 0.0

        weighted_sum = 0.0
        total_weight = 0.0

        for dimension, weight in RiskAssessmentService.DIMENSION_WEIGHTS.items():
            if dimension in dimensions and dimensions[dimension] is not None:
                score = float(dimensions[dimension])
                weighted_sum += score * weight
                total_weight += weight

        if total_weight == 0:
            return 0.0

        overall = weighted_sum / total_weight
        return round(min(100, max(0, overall)), 2)

    @staticmethod
    def categorize_risk_level(score: float) -> str:
        """
        Categorize risk level based on score.

        Args:
            score: Risk score (0-100)

        Returns:
            Risk level: 'LOW', 'MEDIUM', 'HIGH', or 'CRITICAL'
        """
        score = float(score)

        if score <= 25:
            return "LOW"
        elif score <= 50:
            return "MEDIUM"
        elif score <= 75:
            return "HIGH"
        else:
            return "CRITICAL"

    @staticmethod
    def get_risk_color(score: float) -> str:
        """Get CSS color for risk score"""
        level = RiskAssessmentService.categorize_risk_level(score)
        colors = {
            "LOW": "#10b981",      # Green
            "MEDIUM": "#f59e0b",   # Amber
            "HIGH": "#ef5350",     # Orange
            "CRITICAL": "#dc2626", # Red
        }
        return colors.get(level, "#6b7280")

    @staticmethod
    def get_key_concerns(application_dict: Dict) -> List[str]:
        """
        Generate key concerns based on dimension scores.

        Args:
            application_dict: Application data with dimension scores

        Returns:
            List of concern strings
        """
        concerns = []

        privacy_score = float(application_dict.get("privacy_score", 0) or 0)
        if privacy_score > 70:
            concerns.append("High privacy risk: Limited data protection measures")

        security_score = float(application_dict.get("security_score", 0) or 0)
        if security_score > 70:
            concerns.append("Security vulnerabilities: Limited security certifications")

        data_handling_score = float(application_dict.get("data_handling_score", 0) or 0)
        if data_handling_score > 70:
            concerns.append("Data handling: Weak encryption or retention policies")

        enterprise_control_score = float(application_dict.get("enterprise_control_score", 0) or 0)
        if enterprise_control_score > 65:
            concerns.append("Enterprise controls: Limited admin capabilities")

        integration_score = float(application_dict.get("integration_score", 0) or 0)
        if integration_score > 70:
            concerns.append("Integration security: Limited API security controls")

        permission_score = float(application_dict.get("permission_score", 0) or 0)
        if permission_score > 65:
            concerns.append("Permissions: Requests broad data access")

        # Generic concerns if overall score is high
        overall_score = float(application_dict.get("risk_score", 0) or 0)
        if overall_score > 75 and len(concerns) < 3:
            concerns.append("Requires executive review before deployment")

        return concerns if concerns else ["No critical concerns identified"]

    @staticmethod
    def get_recommended_controls(application_dict: Dict) -> List[str]:
        """
        Generate recommended security controls based on dimension scores.

        Args:
            application_dict: Application data with dimension scores

        Returns:
            List of control recommendations
        """
        controls = []

        privacy_score = float(application_dict.get("privacy_score", 0) or 0)
        if privacy_score > 60:
            controls.append("Implement data minimization policies and DLP controls")

        security_score = float(application_dict.get("security_score", 0) or 0)
        if security_score > 65:
            controls.append("Require SOC2 Type II or equivalent certification")

        data_handling_score = float(application_dict.get("data_handling_score", 0) or 0)
        if data_handling_score > 60:
            controls.append("Enforce end-to-end encryption for data in transit and at rest")

        enterprise_control_score = float(application_dict.get("enterprise_control_score", 0) or 0)
        if enterprise_control_score > 60:
            controls.append("Require SSO/SAML integration and advanced audit logging")

        integration_score = float(application_dict.get("integration_score", 0) or 0)
        if integration_score > 60:
            controls.append("Implement API rate limiting and request signing")

        permission_score = float(application_dict.get("permission_score", 0) or 0)
        if permission_score > 60:
            controls.append("Enforce least privilege access and scope-based permissions")

        overall_score = float(application_dict.get("risk_score", 0) or 0)
        if overall_score > 75:
            controls.append("Conduct regular security audits (quarterly)")
            controls.append("Establish incident response procedures")
        elif overall_score > 50:
            controls.append("Conduct annual security assessments")

        # Always recommend monitoring
        controls.append("Enable continuous monitoring and threat detection")

        return controls[:6]  # Return top 6 recommendations

    @staticmethod
    def create_dimension_explanations() -> Dict[str, str]:
        """Get explanations for each dimension"""
        return {
            "privacy": "How well the application protects user privacy and respects data collection policies",
            "security": "Security posture, certifications, and track record of vulnerability management",
            "data_handling": "Data encryption, retention policies, and secure deletion practices",
            "enterprise_control": "Administrative controls, SSO support, and audit logging capabilities",
            "integration": "API security, safe integration options, and third-party access controls",
            "permission": "Scope of required permissions and ability to restrict access",
        }

    @staticmethod
    def format_dimension_score(score: Optional[float]) -> Dict:
        """Format a dimension score with color and label"""
        if score is None:
            score = 0

        score = float(score)

        if score <= 25:
            color = "green"
            label = "Low Risk"
        elif score <= 50:
            color = "yellow"
            label = "Medium Risk"
        elif score <= 75:
            color = "orange"
            label = "High Risk"
        else:
            color = "red"
            label = "Critical Risk"

        return {
            "score": round(score, 2),
            "color": color,
            "label": label,
        }

    @staticmethod
    def calculate_next_assessment_date(days: int = 90) -> datetime:
        """
        Calculate next assessment date (default 90 days from now).

        Args:
            days: Number of days until next assessment

        Returns:
            Next assessment datetime
        """
        return datetime.utcnow() + timedelta(days=days)
