"""
MITRE ATLAS integration.

reference  the ATLAS tactics and techniques, loaded from authoritative data
mapping    which Aiteebar detections correspond to which ATLAS techniques
"""

from . import mapping, reference

__all__ = ["mapping", "reference"]
