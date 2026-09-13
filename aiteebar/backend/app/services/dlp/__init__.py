"""
DLP (Data Loss Prevention) Service Module.
Pattern matching engine for detecting sensitive data in text.
"""

from .detector import DLPDetector, DetectedData
from .patterns import DataType, Severity, PATTERNS, get_pattern, get_all_patterns

__all__ = [
    'DLPDetector',
    'DetectedData',
    'DataType',
    'Severity',
    'PATTERNS',
    'get_pattern',
    'get_all_patterns',
]
