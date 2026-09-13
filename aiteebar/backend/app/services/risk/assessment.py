"""
Risk Assessment Service - Provides dimension scores, concerns, and controls.
"""

from datetime import datetime, timedelta


class RiskAssessmentService:
    """Service for building risk assessments from application data."""

    @staticmethod
    def create_dimension_explanations():
        """Create explanations for each risk dimension."""
        return {
            "privacy": "Evaluation of data privacy policies and user consent mechanisms",
            "security": "Assessment of security practices and vulnerability management",
            "data_handling": "Analysis of how sensitive data is stored and processed",
            "enterprise_control": "Enterprise-level governance and compliance controls",
            "integration": "Risk assessment of integrations with other systems",
            "permission": "Analysis of permission scoping and access controls",
        }

    @staticmethod
    def format_dimension_score(score: float) -> dict:
        """
        Format a dimension score for display.

        Returns:
            dict with score, color, and label
        """
        if score >= 80:
            return {"score": score, "color": "#d32f2f", "label": "Critical"}
        elif score >= 60:
            return {"score": score, "color": "#f57c00", "label": "High"}
        elif score >= 40:
            return {"score": score, "color": "#fbc02d", "label": "Medium"}
        else:
            return {"score": score, "color": "#388e3c", "label": "Low"}

    @staticmethod
    def get_key_concerns(app_dict: dict) -> list:
        """Extract key concerns from application data."""
        concerns = []

        if app_dict.get("privacy_score", 0) > 60:
            concerns.append("Privacy controls may be insufficient")
        if app_dict.get("security_score", 0) > 60:
            concerns.append("Security posture needs improvement")
        if app_dict.get("data_handling_score", 0) > 60:
            concerns.append("Data handling practices require review")
        if app_dict.get("enterprise_control_score", 0) < 40:
            concerns.append("Enterprise controls are lacking")
        if app_dict.get("integration_score", 0) > 60:
            concerns.append("Integration risks detected")
        if app_dict.get("permission_score", 0) > 60:
            concerns.append("Permission scoping needs attention")

        return concerns or ["Application meets baseline security standards"]

    @staticmethod
    def get_recommended_controls(app_dict: dict) -> list:
        """Get recommended security controls."""
        controls = []

        if app_dict.get("privacy_score", 0) > 60:
            controls.append("Implement enhanced privacy controls")
        if app_dict.get("security_score", 0) > 60:
            controls.append("Conduct security audit and penetration testing")
        if app_dict.get("data_handling_score", 0) > 60:
            controls.append("Review and strengthen data handling procedures")
        if app_dict.get("enterprise_control_score", 0) < 40:
            controls.append("Establish formal governance framework")
        if app_dict.get("integration_score", 0) > 60:
            controls.append("Review integration security and data flows")
        if app_dict.get("permission_score", 0) > 60:
            controls.append("Implement principle of least privilege")

        if not controls:
            controls.append("Continue current security practices")

        return controls

    @staticmethod
    def calculate_next_assessment_date(days: int = 90) -> datetime:
        """Calculate next assessment date."""
        return datetime.utcnow() + timedelta(days=days)

    @staticmethod
    def categorize_risk_level(score: float) -> str:
        """
        Categorize risk level based on score.

        Args:
            score: Risk score (0-100)

        Returns:
            Risk level: LOW, MEDIUM, HIGH, CRITICAL
        """
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        else:
            return "LOW"

    @staticmethod
    def get_risk_color(score: float) -> str:
        """Get color code for risk level."""
        if score >= 80:
            return "#d32f2f"  # Red
        elif score >= 60:
            return "#f57c00"  # Orange
        elif score >= 40:
            return "#fbc02d"  # Yellow
        else:
            return "#388e3c"  # Green
