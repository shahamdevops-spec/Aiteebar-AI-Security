"""
DLP Detection Service - Core pattern matching engine for sensitive data detection.
Provides deterministic, fast pattern-based detection with confidence scoring.
"""

import re
from typing import NamedTuple
from dataclasses import dataclass, field
from datetime import datetime

from .patterns import PATTERNS, DataType, Severity


@dataclass
class DetectedData:
    """Represents a single detected sensitive data instance"""
    data_type: DataType
    confidence: float
    severity: Severity
    matched_content: str
    context: str
    position: int

    def to_dict(self):
        return {
            'data_type': self.data_type.value,
            'confidence': self.confidence,
            'severity': self.severity.value,
            'matched_content': self.matched_content[:20] + '...' if len(self.matched_content) > 20 else self.matched_content,
            'context': self.context,
            'position': self.position,
        }


class DLPDetector:
    """
    Deterministic pattern-based DLP detector.
    Uses compiled regex patterns for fast, reliable detection.
    """

    def __init__(self, overlap_threshold: int = 5):
        self.patterns = PATTERNS
        self.overlap_threshold = overlap_threshold
        self._detection_cache = {}

    def detect_sensitive_data(self, text: str, max_context_chars: int = 50) -> list[DetectedData]:
        """
        Scan text for sensitive data using pattern matching.

        Args:
            text: Text to scan
            max_context_chars: Characters of context around match to include

        Returns:
            List of DetectedData objects sorted by severity (CRITICAL first)
        """
        if not text:
            return []

        detections = []
        processed_ranges = set()

        for pattern in self.patterns:
            matches = pattern.pattern.finditer(text)

            for match in matches:
                start, end = match.span()

                # Skip overlapping detections if they're very close
                if self._is_overlapping(start, end, processed_ranges):
                    continue

                matched_text = match.group(0)
                confidence = self._calculate_confidence(
                    pattern, matched_text, text, start
                )

                # Only include high-confidence detections
                if confidence >= 50.0:
                    context = self._extract_context(text, start, end, max_context_chars)

                    detection = DetectedData(
                        data_type=pattern.data_type,
                        confidence=min(confidence, 100.0),
                        severity=pattern.severity,
                        matched_content=matched_text,
                        context=context,
                        position=start,
                    )

                    detections.append(detection)
                    processed_ranges.add((start, end))

        # Sort by severity (CRITICAL first) then by confidence
        severity_order = {Severity.CRITICAL: 0, Severity.HIGH: 1, Severity.MEDIUM: 2, Severity.LOW: 3}
        detections.sort(
            key=lambda d: (severity_order.get(d.severity, 4), -d.confidence)
        )

        return detections

    def _calculate_confidence(self, pattern, matched_text: str, full_text: str, position: int) -> float:
        """
        Calculate confidence score based on pattern and context.

        Factors:
        - Base confidence from pattern definition
        - Pattern match quality (length, entropy)
        - Contextual factors (presence of keywords, structure)
        """
        confidence = pattern.base_confidence

        # Boost confidence for longer matches (more specific)
        if len(matched_text) > 20:
            confidence += 5.0

        # Reduce confidence for very common data
        if pattern.data_type == DataType.EMAIL:
            # Reduce false positives for common email patterns
            if self._looks_like_example(matched_text):
                confidence -= 20.0
        elif pattern.data_type == DataType.PHONE:
            # Reduce confidence for incomplete phone patterns
            if len(matched_text) < 10:
                confidence -= 15.0

        # Contextual boost: check for confidentiality markers nearby
        context_window = 100
        context_start = max(0, position - context_window)
        context_end = min(len(full_text), position + context_window)
        surrounding_text = full_text[context_start:context_end]

        if any(marker in surrounding_text.upper() for marker in ['CONFIDENTIAL', 'SECRET', 'RESTRICTED']):
            confidence += 10.0

        return min(100.0, max(0.0, confidence))

    def _is_overlapping(self, start: int, end: int, processed_ranges: set) -> bool:
        """Check if position overlaps with already processed ranges"""
        for proc_start, proc_end in processed_ranges:
            if (start < proc_end and end > proc_start):
                return True
        return False

    def _extract_context(self, text: str, start: int, end: int, max_chars: int) -> str:
        """Extract surrounding context for matched data"""
        context_start = max(0, start - max_chars)
        context_end = min(len(text), end + max_chars)

        context = text[context_start:context_end]

        # Add ellipsis if truncated
        if context_start > 0:
            context = "..." + context
        if context_end < len(text):
            context = context + "..."

        return context.replace('\n', ' ')[:200]

    def _looks_like_example(self, email: str) -> bool:
        """Check if email looks like an example/test email"""
        example_patterns = ['example@', 'test@', 'demo@', 'user@example', '@test.', 'foo@', 'bar@']
        return any(pattern in email.lower() for pattern in example_patterns)

    def scan_and_report(self, text: str) -> dict:
        """
        Scan text and return a structured report.

        Returns:
            Dict with detection summary and details
        """
        detections = self.detect_sensitive_data(text)

        severity_counts = {}
        data_types_found = set()

        for detection in detections:
            severity_counts[detection.severity.value] = severity_counts.get(detection.severity.value, 0) + 1
            data_types_found.add(detection.data_type.value)

        return {
            'total_detections': len(detections),
            'severity_breakdown': severity_counts,
            'data_types_found': list(data_types_found),
            'detections': [d.to_dict() for d in detections],
        }
