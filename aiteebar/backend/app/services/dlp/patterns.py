"""
DLP Pattern definitions for detecting sensitive data types.
Each pattern is a compiled regex with metadata for detection.
"""

import re
from enum import Enum
from typing import NamedTuple, Pattern

class DataType(str, Enum):
    """Sensitive data types that DLP can detect"""
    CNIC = "CNIC"
    IBAN = "IBAN"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    API_KEY = "API_KEY"
    PASSWORD = "PASSWORD"
    AWS_SECRET = "AWS_SECRET"
    CREDIT_CARD = "CREDIT_CARD"
    SOURCE_CODE = "SOURCE_CODE"
    CONFIDENTIAL = "CONFIDENTIAL"

class Severity(str, Enum):
    """Severity levels for detected data"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class DLPPattern(NamedTuple):
    """Pattern definition for DLP detection"""
    data_type: DataType
    pattern: Pattern
    severity: Severity
    base_confidence: float
    description: str

# Compile all patterns
PATTERNS = [
    # CNIC: Pakistan's national ID (13 digits: XXXXX-XXXXXXX-X)
    DLPPattern(
        data_type=DataType.CNIC,
        pattern=re.compile(r'\b\d{5}-\d{7}-\d{1}\b'),
        severity=Severity.CRITICAL,
        base_confidence=95.0,
        description="Pakistan National ID (CNIC)"
    ),

    # IBAN: International Bank Account Number (34 chars max)
    DLPPattern(
        data_type=DataType.IBAN,
        pattern=re.compile(r'\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b'),
        severity=Severity.CRITICAL,
        base_confidence=90.0,
        description="International Bank Account Number (IBAN)"
    ),

    # Email addresses
    DLPPattern(
        data_type=DataType.EMAIL,
        pattern=re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'),
        severity=Severity.MEDIUM,
        base_confidence=85.0,
        description="Email address"
    ),

    # Phone numbers (international format)
    DLPPattern(
        data_type=DataType.PHONE,
        pattern=re.compile(r'\+\d{1,3}-?\d{3}-?\d{3}-?\d{4}\b'),
        severity=Severity.MEDIUM,
        base_confidence=80.0,
        description="Phone number (international format)"
    ),

    # API Keys (various patterns)
    DLPPattern(
        data_type=DataType.API_KEY,
        pattern=re.compile(r'\b(sk_live_|pk_test_|api_key|apikey|API_KEY)[_\s]?[a-zA-Z0-9]{20,}\b', re.IGNORECASE),
        severity=Severity.CRITICAL,
        base_confidence=92.0,
        description="API Key or token"
    ),

    # Passwords (quoted or assigned)
    DLPPattern(
        data_type=DataType.PASSWORD,
        pattern=re.compile(r'(?:password|passwd|pwd)["\']?\s*[:=]\s*["\']([^"\']+)["\']', re.IGNORECASE),
        severity=Severity.CRITICAL,
        base_confidence=88.0,
        description="Password or credential"
    ),

    # AWS/Cloud secrets
    DLPPattern(
        data_type=DataType.AWS_SECRET,
        pattern=re.compile(r'(aws_secret_access_key|AKIA[0-9A-Z]{16}|aws_secret)[_\s]?[:=]?\s*[a-zA-Z0-9/+=]{40,}', re.IGNORECASE),
        severity=Severity.CRITICAL,
        base_confidence=98.0,
        description="AWS or cloud secret key"
    ),

    # Credit cards (16-digit with optional separators)
    DLPPattern(
        data_type=DataType.CREDIT_CARD,
        pattern=re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
        severity=Severity.CRITICAL,
        base_confidence=85.0,
        description="Credit card number"
    ),

    # Source code blocks
    DLPPattern(
        data_type=DataType.SOURCE_CODE,
        pattern=re.compile(r'(def |class |function |import |SELECT |INSERT |CREATE TABLE )', re.IGNORECASE),
        severity=Severity.HIGH,
        base_confidence=70.0,
        description="Source code or SQL statement"
    ),

    # Confidential markings
    DLPPattern(
        data_type=DataType.CONFIDENTIAL,
        pattern=re.compile(r'\b(CONFIDENTIAL|PROPRIETARY|SECRET|RESTRICTED|CLASSIFIED|INTERNAL)\b', re.IGNORECASE),
        severity=Severity.HIGH,
        base_confidence=80.0,
        description="Confidential or classified marking"
    ),
]

# Create pattern lookup by data type for quick access
PATTERN_MAP = {pattern.data_type: pattern for pattern in PATTERNS}

def get_pattern(data_type: DataType) -> DLPPattern:
    """Get a pattern by data type"""
    return PATTERN_MAP.get(data_type)

def get_all_patterns() -> list[DLPPattern]:
    """Get all DLP patterns"""
    return PATTERNS
