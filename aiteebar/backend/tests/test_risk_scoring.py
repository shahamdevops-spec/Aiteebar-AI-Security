"""
Comprehensive test suite for Multi-Factor Risk Scoring Engine.
"""

import pytest
from datetime import datetime, timedelta
from app.services.risk.engine import RiskScoringEngine
from app.services.risk.calculator import RiskCalculator


class TestRiskCalculator:
    """Test individual risk factor calculations"""

    def setup_method(self):
        self.calculator = RiskCalculator()

    def test_calculate_application_risk_low(self):
        """Test low risk application"""
        app_data = {
            'name': 'TestApp',
            'risk_score': 20,
            'risk_level': 'LOW',
            'privacy_score': 80,
            'security_score': 85,
            'data_handling_score': 80,
        }
        result = self.calculator.calculate_application_risk(app_data)
        assert result.value < 40
        assert 'TestApp' in result.explanation

    def test_calculate_application_risk_critical(self):
        """Test critical risk application"""
        app_data = {
            'name': 'RiskyApp',
            'risk_score': 95,
            'risk_level': 'CRITICAL',
            'privacy_score': 20,
            'security_score': 15,
            'data_handling_score': 10,
        }
        result = self.calculator.calculate_application_risk(app_data)
        assert result.value >= 80
        assert result.value <= 100

    def test_calculate_agent_privilege_no_tools(self):
        """Test agent with no tools"""
        agent_data = {
            'name': 'SimpleAgent',
            'connected_tools': [],
            'data_access': {},
            'status': 'active',
            'risk_level': 'LOW',
        }
        result = self.calculator.calculate_agent_privilege_level(agent_data)
        assert result.value < 50

    def test_calculate_agent_privilege_many_tools(self):
        """Test agent with many tools"""
        agent_data = {
            'name': 'PowerAgent',
            'connected_tools': ['tool1', 'tool2', 'tool3', 'tool4', 'tool5'],
            'data_access': {'types': ['CNIC', 'IBAN', 'API_KEY']},
            'status': 'active',
            'risk_level': 'CRITICAL',
        }
        result = self.calculator.calculate_agent_privilege_level(agent_data)
        assert result.value >= 60

    def test_calculate_data_sensitivity_no_access(self):
        """Test with no sensitive data access"""
        data_access = {'types': []}
        result = self.calculator.calculate_data_sensitivity(data_access)
        assert result.value == 10.0

    def test_calculate_data_sensitivity_critical_data(self):
        """Test with critical data types"""
        data_access = {
            'types': ['CNIC', 'PASSWORD', 'AWS_SECRET', 'CREDIT_CARD']
        }
        result = self.calculator.calculate_data_sensitivity(data_access)
        assert result.value >= 90

    def test_calculate_data_sensitivity_mixed(self):
        """Test with mixed data types"""
        data_access = {
            'types': ['EMAIL', 'PHONE', 'CNIC']
        }
        result = self.calculator.calculate_data_sensitivity(data_access)
        assert 40 < result.value < 90

    def test_calculate_tool_permissions_safe(self):
        """Test with safe tools"""
        tools = [
            {'name': 'ReadFile', 'data_sensitivity': 'LOW'},
            {'name': 'ListFiles', 'data_sensitivity': 'LOW'},
        ]
        result = self.calculator.calculate_tool_permissions(tools)
        assert result.value < 40

    def test_calculate_tool_permissions_dangerous(self):
        """Test with dangerous tools"""
        tools = [
            {'name': 'ExecuteCommand', 'data_sensitivity': 'CRITICAL'},
            {'name': 'ModifyDatabase', 'data_sensitivity': 'CRITICAL'},
        ]
        result = self.calculator.calculate_tool_permissions(tools)
        assert result.value >= 80

    def test_calculate_destination_risk_internal(self):
        """Test internal destination"""
        connections = [
            {'is_internal': True, 'destination_risk_score': 20}
        ]
        result = self.calculator.calculate_destination_risk(connections)
        assert result.value < 40

    def test_calculate_destination_risk_external(self):
        """Test external destination"""
        connections = [
            {'is_external': True, 'is_internal': False, 'destination_risk_score': 80}
        ]
        result = self.calculator.calculate_destination_risk(connections)
        assert result.value >= 50

    def test_calculate_destination_risk_multiple_external(self):
        """Test multiple external destinations"""
        connections = [
            {'is_external': True, 'is_internal': False, 'destination_risk_score': 80},
            {'is_external': True, 'is_internal': False, 'destination_risk_score': 75},
            {'is_external': True, 'is_internal': False, 'destination_risk_score': 85},
        ]
        result = self.calculator.calculate_destination_risk(connections)
        assert result.value >= 70

    def test_calculate_behavior_anomaly_no_threats(self):
        """Test with no threats"""
        result = self.calculator.calculate_behavior_anomaly_score([])
        assert result.value == 10.0

    def test_calculate_behavior_anomaly_critical_threat(self):
        """Test with critical threat"""
        threats = [
            {'severity': 'CRITICAL', 'risk_score': 95, 'timestamp': datetime.utcnow()}
        ]
        result = self.calculator.calculate_behavior_anomaly_score(threats)
        assert result.value >= 75

    def test_calculate_behavior_anomaly_recent_threats(self):
        """Test with recent threats"""
        now = datetime.utcnow()
        threats = [
            {'severity': 'HIGH', 'risk_score': 70, 'timestamp': now},
            {'severity': 'MEDIUM', 'risk_score': 45, 'timestamp': now - timedelta(minutes=30)},
            {'severity': 'HIGH', 'risk_score': 65, 'timestamp': now - timedelta(minutes=45)},
        ]
        result = self.calculator.calculate_behavior_anomaly_score(threats)
        assert result.value >= 50

    def test_calculate_dlp_detection_no_events(self):
        """Test with no DLP events"""
        result = self.calculator.calculate_dlp_detection_score([])
        assert result.value == 5.0

    def test_calculate_dlp_detection_critical_events(self):
        """Test with critical DLP events"""
        dlp_events = [
            {'severity': 'CRITICAL', 'data_type': 'PASSWORD', 'confidence': 98},
            {'severity': 'CRITICAL', 'data_type': 'API_KEY', 'confidence': 92},
        ]
        result = self.calculator.calculate_dlp_detection_score(dlp_events)
        assert result.value >= 80


class TestRiskScoringEngine:
    """Test main risk scoring engine"""

    def setup_method(self):
        self.engine = RiskScoringEngine()

    def test_get_risk_level_critical(self):
        """Test risk level conversion for critical"""
        assert self.engine._get_risk_level(85) == 'CRITICAL'
        assert self.engine._get_risk_level(100) == 'CRITICAL'

    def test_get_risk_level_high(self):
        """Test risk level conversion for high"""
        assert self.engine._get_risk_level(75) == 'HIGH'
        assert self.engine._get_risk_level(60) == 'HIGH'

    def test_get_risk_level_medium(self):
        """Test risk level conversion for medium"""
        assert self.engine._get_risk_level(55) == 'MEDIUM'
        assert self.engine._get_risk_level(40) == 'MEDIUM'

    def test_get_risk_level_low(self):
        """Test risk level conversion for low"""
        assert self.engine._get_risk_level(30) == 'LOW'
        assert self.engine._get_risk_level(0) == 'LOW'

    def test_calculate_application_risk_low_app(self):
        """Test application risk calculation for low-risk app"""
        app_data = {
            'name': 'SafeApp',
            'risk_score': 15,
            'risk_level': 'LOW',
            'privacy_score': 90,
            'security_score': 88,
            'data_handling_score': 85,
        }
        score = self.engine.calculate_application_risk('app_123', app_data)

        assert score.entity_type == 'application'
        assert score.entity_id == 'app_123'
        assert score.overall_score < 40
        assert score.risk_level == 'LOW'
        assert len(score.factors) > 0

    def test_calculate_application_risk_critical_app(self):
        """Test application risk calculation for critical-risk app"""
        app_data = {
            'name': 'DangerousApp',
            'risk_score': 98,
            'risk_level': 'CRITICAL',
            'privacy_score': 5,
            'security_score': 10,
            'data_handling_score': 8,
        }
        score = self.engine.calculate_application_risk('app_456', app_data)

        assert score.overall_score >= 70
        assert score.risk_level in ['HIGH', 'CRITICAL']

    def test_calculate_agent_risk_low_agent(self):
        """Test agent risk calculation for low-risk agent"""
        app_data = {
            'name': 'SafeApp',
            'risk_score': 20,
            'risk_level': 'LOW',
            'privacy_score': 80,
            'security_score': 85,
            'data_handling_score': 80,
        }
        agent_data = {
            'name': 'SafeAgent',
            'risk_score': 10,
            'risk_level': 'LOW',
            'status': 'active',
            'connected_tools': ['read_file'],
            'data_access': {'types': []},
        }

        score = self.engine.calculate_agent_risk(
            'agent_123', agent_data, app_data, [], [], [], []
        )

        assert score.entity_type == 'agent'
        assert score.overall_score < 50
        assert score.risk_level in ['LOW', 'MEDIUM']
        assert len(score.factors) >= 6

    def test_calculate_agent_risk_critical_agent(self):
        """Test agent risk calculation for critical-risk agent"""
        app_data = {
            'name': 'HighRiskApp',
            'risk_score': 90,
            'risk_level': 'CRITICAL',
            'privacy_score': 20,
            'security_score': 25,
            'data_handling_score': 20,
        }
        agent_data = {
            'name': 'DangerousAgent',
            'risk_score': 85,
            'risk_level': 'CRITICAL',
            'status': 'active',
            'connected_tools': ['exec_command', 'drop_database'],
            'data_access': {'types': ['CNIC', 'IBAN', 'PASSWORD', 'API_KEY']},
        }
        tools = [
            {'name': 'exec_command', 'data_sensitivity': 'CRITICAL'},
            {'name': 'drop_database', 'data_sensitivity': 'CRITICAL'},
        ]
        threats = [
            {'severity': 'CRITICAL', 'risk_score': 95, 'timestamp': datetime.utcnow()}
        ]
        dlp_events = [
            {'severity': 'CRITICAL', 'data_type': 'PASSWORD', 'confidence': 98},
            {'severity': 'CRITICAL', 'data_type': 'API_KEY', 'confidence': 95},
        ]

        score = self.engine.calculate_agent_risk(
            'agent_456', agent_data, app_data, tools, [], threats, dlp_events
        )

        assert score.overall_score >= 70
        assert score.risk_level in ['HIGH', 'CRITICAL']
        assert len(score.factors) >= 6

    def test_calculate_tool_risk_low_sensitivity(self):
        """Test tool risk calculation"""
        tool_data = {
            'name': 'ReadFile',
            'data_sensitivity': 'LOW',
            'risk_score': 15,
        }
        score = self.engine.calculate_tool_risk('tool_123', tool_data)

        assert score.entity_type == 'tool'
        assert score.overall_score < 40
        assert score.risk_level == 'LOW'

    def test_calculate_tool_risk_critical_sensitivity(self):
        """Test critical tool risk calculation"""
        tool_data = {
            'name': 'ExecuteCommand',
            'data_sensitivity': 'CRITICAL',
            'risk_score': 95,
        }
        score = self.engine.calculate_tool_risk('tool_456', tool_data)

        assert score.overall_score >= 80
        assert score.risk_level in ['HIGH', 'CRITICAL']

    def test_calculate_destination_risk_internal(self):
        """Test internal destination risk"""
        dest_data = {
            'name': 'InternalDB',
            'is_internal': True,
            'risk_score': 20,
        }
        score = self.engine.calculate_destination_risk('dest_123', dest_data)

        assert score.overall_score < 40
        assert score.risk_level == 'LOW'

    def test_calculate_destination_risk_external(self):
        """Test external destination risk"""
        dest_data = {
            'name': 'ExternalAPI',
            'is_internal': False,
            'risk_score': 85,
        }
        score = self.engine.calculate_destination_risk('dest_456', dest_data)

        assert score.overall_score >= 60
        assert score.risk_level in ['MEDIUM', 'HIGH']

    def test_risk_score_to_dict(self):
        """Test risk score conversion to dict"""
        app_data = {
            'name': 'TestApp',
            'risk_score': 50,
            'risk_level': 'MEDIUM',
            'privacy_score': 50,
            'security_score': 50,
            'data_handling_score': 50,
        }
        score = self.engine.calculate_application_risk('app_123', app_data)

        score_dict = score.to_dict()

        assert 'entity_type' in score_dict
        assert 'overall_score' in score_dict
        assert 'risk_level' in score_dict
        assert 'factors' in score_dict
        assert 'explanation' in score_dict
        assert 'timestamp' in score_dict

    def test_detailed_explanation_generation(self):
        """Test detailed explanation generation"""
        app_data = {
            'name': 'TestApp',
            'risk_score': 50,
            'risk_level': 'MEDIUM',
            'privacy_score': 50,
            'security_score': 50,
            'data_handling_score': 50,
        }
        score = self.engine.calculate_application_risk('app_123', app_data)

        assert score.detailed_explanation is not None
        assert 'Risk Factor Breakdown' in score.detailed_explanation
        assert len(score.detailed_explanation) > 0
