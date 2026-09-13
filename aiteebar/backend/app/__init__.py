"""
Aiteebar AI Security - FastAPI Backend Application

A production-ready backend for AI security analysis and threat intelligence.
"""

__version__ = "0.1.0"
__author__ = "Aiteebar Team"

from app.config import settings
from app.database import engine, SessionLocal, Base, get_db
from app.main import app

__all__ = [
    "app",
    "settings",
    "engine",
    "SessionLocal",
    "Base",
    "get_db",
]
