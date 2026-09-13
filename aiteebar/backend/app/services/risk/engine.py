"""
Risk Scoring Engine - Multi-factor explainable risk assessment.
Combines multiple risk factors with weighted scoring and detailed explanations.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime

from .calculator import RiskCalculator, FactorCalculation


@dataclass
class RiskFactor:
    """Individual risk factor contribution"""
    name: str
    value: float  # 0-100
    weight: float  # 0-1 (contribution to total)
    explanation: str
    contributing_factors: Dict[str, Any] = field(default_factory=dict)
    weighted_contribution: float = 0.0

    def calculate_contribution(self):
        """Calculate this factor's contribution to overall score"""
        self.weighted_contribution = self.value * self.weight


@dataclass
class RiskScore:
    """Complete risk assessment result"""
    entity_type: str  # 'application', 'agent', 'tool', 'destination'
    entity_id: str
    overall_score: float  # 0-100
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    factors: List[RiskFactor]
    explanation: str  # Human-readable summary
    detailed_explanation: str  # Detailed breakdown
    timestamp: datetime

    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'overall_score': round(self.overall_score, 2),
            'risk_level': self.risk_level,
            'factors': [
                {
                    'name': f.name,
                    'value': round(f.value, 2),
                    'weight': f.weight,
                    'weighted_contribution': round(f.weighted_contribution, 2),
                    'explanation': f.explanation,
                    'contributing_factors': f.contributing_factors,
                }
                for f in self.factors
            ],
            'explanation': self.explanation,
            'detailed_explanation': self.detailed_explanation,
            'timestamp': self.timestamp.isoformat(),
        }


class RiskScoringEngine:
    """
    Multi-factor risk scoring engine.
    Combines application, agent, data, tool, network, and behavioral factors.
    """

    def __init__(self):
        self.calculator = RiskCalculator()

    def calculate_application_risk(self, app_id: str, app_data: Dict[str, Any]) -> RiskScore:
        """
        Calculate risk score for an application.

        Factors considered:
        - Application risk score
        - Security assessment dimensions
        - Risk level classification
        """
        factors = []

        # Factor 1: Application Risk (weighted 0.25)
        app_risk_factor = self.calculator.calculate_application_risk(app_data)
        factor = self._create_risk_factor(app_risk_factor)
        factors.append(factor)

        # For application-only scoring, other factors are baseline
        # Factor 2: Data Sensitivity (weighted 0.25)
        data_sensitivity = FactorCalculation(
            name="Data Sensitivity Level",
            value=50.0,  # Baseline for app without agent context
            explanation="Data sensitivity not applicable at application level",
            contributing_factors={},
            weight=0.25
        )
        factors.append(self._create_risk_factor(data_sensitivity))

        # Calculate overall score
        overall_score = sum(f.weighted_contribution for f in factors)
        risk_level = self._get_risk_level(overall_score)

        explanation = f"Application '{app_data.get('name')}' has {risk_level} overall risk"
        detailed = self._generate_detailed_explanation(factors)

        return RiskScore(
            entity_type='application',
            entity_id=app_id,
            overall_score=overall_score,
            risk_level=risk_level,
            factors=factors,
            explanation=explanation,
            detailed_explanation=detailed,
            timestamp=datetime.utcnow(),
        )

    def calculate_agent_risk(
        self,
        agent_id: str,
        agent_data: Dict[str, Any],
        app_data: Dict[str, Any],
        tools_data: List[Dict[str, Any]],
        connections: List[Dict[str, Any]],
        threats: List[Dict[str, Any]],
        dlp_events: List[Dict[str, Any]],
    ) -> RiskScore:
        """
        Calculate comprehensive risk score for an agent.

        Considers all 7 risk factors:
        1. Application Risk (25%)
        2. Agent Privilege Level (20%)
        3. Data Sensitivity Level (25%)
        4. Tool Permission Scope (15%)
        5. Destination Risk (10%)
        6. Behavior Anomaly Score (5%)
        (+ implicit DLP Detection Score)
        """
        factors = []

        # Factor 1: Application Risk (0.25)
        app_factor = self.calculator.calculate_application_risk(app_data)
        factors.append(self._create_risk_factor(app_factor))

        # Factor 2: Agent Privilege Level (0.20)
        privilege_factor = self.calculator.calculate_agent_privilege_level(agent_data)
        factors.append(self._create_risk_factor(privilege_factor))

        # Factor 3: Data Sensitivity Level (0.25)
        data_sensitivity = agent_data.get('data_access', {})
        sensitivity_factor = self.calculator.calculate_data_sensitivity(data_sensitivity)
        factors.append(self._create_risk_factor(sensitivity_factor))

        # Factor 4: Tool Permission Scope (0.15)
        tools_factor = self.calculator.calculate_tool_permissions(tools_data)
        factors.append(self._create_risk_factor(tools_factor))

        # Factor 5: Destination Risk (0.10)
        destination_factor = self.calculator.calculate_destination_risk(connections)
        factors.append(self._create_risk_factor(destination_factor))

        # Factor 6: Behavior Anomaly Score (0.05)
        behavior_factor = self.calculator.calculate_behavior_anomaly_score(threats)
        factors.append(self._create_risk_factor(behavior_factor))

        # Implicit Factor: DLP Detection Score (from overall DLP events)
        dlp_factor = self.calculator.calculate_dlp_detection_score(dlp_events)
        # DLP is implicit in data sensitivity but also tracked separately

        # Calculate overall score using weighted average
        overall_score = sum(f.weighted_contribution for f in factors)
        risk_level = self._get_risk_level(overall_score)

        agent_name = agent_data.get('name', f'Agent {agent_id}')
        explanation = f"Agent '{agent_name}' has {risk_level} overall risk score ({overall_score:.1f}/100)"
        detailed = self._generate_detailed_explanation(factors)

        return RiskScore(
            entity_type='agent',
            entity_id=agent_id,
            overall_score=overall_score,
            risk_level=risk_level,
            factors=factors,
            explanation=explanation,
            detailed_explanation=detailed,
            timestamp=datetime.utcnow(),
        )

    def calculate_tool_risk(self, tool_id: str, tool_data: Dict[str, Any]) -> RiskScore:
        """
        Calculate risk score for a specific tool.

        Based on:
        - Tool sensitivity level
        - Permissions
        - Usage context
        """
        factors = []

        # Tool sensitivity is primary factor
        sensitivity = tool_data.get('data_sensitivity', 'MEDIUM')
        severity_scores = {'LOW': 20, 'MEDIUM': 50, 'HIGH': 75, 'CRITICAL': 100}
        tool_risk_value = severity_scores.get(sensitivity, 50)

        # Create factor with full weight (since this is tool-only assessment)
        tool_factor = FactorCalculation(
            name="Tool Risk Level",
            value=tool_risk_value,
            explanation=f"Tool has {sensitivity} data sensitivity level",
            contributing_factors={
                'sensitivity': sensitivity,
                'risk_value': tool_risk_value,
            },
            weight=1.0
        )
        factors.append(self._create_risk_factor(tool_factor))

        overall_score = tool_risk_value
        risk_level = self._get_risk_level(overall_score)

        tool_name = tool_data.get('name', f'Tool {tool_id}')
        explanation = f"Tool '{tool_name}' has {risk_level} risk due to {sensitivity} data sensitivity"
        detailed = f"This tool can access or modify data with {sensitivity} sensitivity level."

        return RiskScore(
            entity_type='tool',
            entity_id=tool_id,
            overall_score=overall_score,
            risk_level=risk_level,
            factors=factors,
            explanation=explanation,
            detailed_explanation=detailed,
            timestamp=datetime.utcnow(),
        )

    def calculate_destination_risk(
        self,
        destination_id: str,
        destination_data: Dict[str, Any],
    ) -> RiskScore:
        """
        Calculate risk score for a network destination.

        Based on:
        - Internal vs External
        - Destination risk assessment
        - Connection patterns
        """
        factors = []

        is_internal = destination_data.get('is_internal', True)
        risk_score_value = destination_data.get('risk_score', 50)

        # Internal destinations have lower baseline risk
        if is_internal:
            explanation = "Internal destination with standard security controls"
            risk_value = min(40.0, risk_score_value)
        else:
            explanation = "External destination with elevated risk"
            risk_value = max(60.0, risk_score_value)

        dest_factor = FactorCalculation(
            name="Destination Risk",
            value=risk_value,
            explanation=explanation,
            contributing_factors={
                'is_internal': is_internal,
                'risk_score': risk_score_value,
            },
            weight=1.0
        )
        factors.append(self._create_risk_factor(dest_factor))

        overall_score = risk_value
        risk_level = self._get_risk_level(overall_score)

        dest_name = destination_data.get('name', f'Destination {destination_id}')
        dest_type = "Internal" if is_internal else "External"
        explanation = f"Destination '{dest_name}' is {dest_type} with {risk_level} risk"
        detailed = f"This is an {dest_type.lower()} destination with risk score {risk_score_value}/100"

        return RiskScore(
            entity_type='destination',
            entity_id=destination_id,
            overall_score=overall_score,
            risk_level=risk_level,
            factors=factors,
            explanation=explanation,
            detailed_explanation=detailed,
            timestamp=datetime.utcnow(),
        )

    def _create_risk_factor(self, calculation: FactorCalculation) -> RiskFactor:
        """Convert FactorCalculation to RiskFactor with weighted contribution"""
        factor = RiskFactor(
            name=calculation.name,
            value=calculation.value,
            weight=calculation.weight,
            explanation=calculation.explanation,
            contributing_factors=calculation.contributing_factors,
        )
        factor.calculate_contribution()
        return factor

    def _get_risk_level(self, score: float) -> str:
        """Convert numerical score to risk level"""
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_detailed_explanation(self, factors: List[RiskFactor]) -> str:
        """Generate detailed explanation of risk factors"""
        lines = ["Risk Factor Breakdown:\n"]

        # Sort by contribution (descending)
        sorted_factors = sorted(
            factors,
            key=lambda f: f.weighted_contribution,
            reverse=True
        )

        for i, factor in enumerate(sorted_factors, 1):
            contribution_pct = (factor.weighted_contribution / sum(f.value * f.weight for f in factors) * 100) if sum(f.value * f.weight for f in factors) > 0 else 0
            lines.append(
                f"{i}. {factor.name} ({factor.value:.1f}/100) - Weight: {factor.weight*100:.0f}% - "
                f"Contribution: {factor.weighted_contribution:.1f}/100\n"
                f"   → {factor.explanation}\n"
            )

        return "".join(lines)

    def compare_risk_scores(
        self,
        score1: RiskScore,
        score2: RiskScore,
    ) -> Dict[str, Any]:
        """
        Compare two risk scores and identify differences.

        Returns analysis of what factors differ and why.
        """
        comparison = {
            'entity1': {
                'type': score1.entity_type,
                'id': score1.entity_id,
                'score': score1.overall_score,
                'level': score1.risk_level,
            },
            'entity2': {
                'type': score2.entity_type,
                'id': score2.entity_id,
                'score': score2.overall_score,
                'level': score2.risk_level,
            },
            'score_difference': abs(score1.overall_score - score2.overall_score),
            'factor_differences': [],
        }

        # Compare matching factors
        for f1 in score1.factors:
            f2_match = next((f for f in score2.factors if f.name == f1.name), None)
            if f2_match:
                diff = abs(f1.value - f2_match.value)
                comparison['factor_differences'].append({
                    'factor': f1.name,
                    'entity1_value': f1.value,
                    'entity2_value': f2_match.value,
                    'difference': diff,
                })

        return comparison
