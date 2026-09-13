"""
SOC Alerting Service
Generates SIEM-compatible alerts from security events and delivers them
to webhook and email destinations.
"""

from .generator import AlertGenerator
from .notifier import AlertNotifier

__all__ = ['AlertGenerator', 'AlertNotifier']
