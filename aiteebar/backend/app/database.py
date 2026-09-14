"""
Database connection and session management for SQLAlchemy.
Handles engine initialization, session factory, and connection pooling.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool
from typing import Generator
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# ============================================================================
# DATABASE ENGINE CONFIGURATION
# ============================================================================

# SQLite (used for zero-install local development) does not use a server-side
# connection pool and needs check_same_thread disabled so FastAPI's worker
# threads can share the connection. PostgreSQL keeps the tuned QueuePool.
is_sqlite = settings.database_url.startswith("sqlite")

if is_sqlite:
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        pool_pre_ping=settings.database_pool_pre_ping,
        echo=settings.database_echo,
    )
else:
    engine = create_engine(
        settings.database_url,

        # Connection pooling
        poolclass=QueuePool,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_recycle=settings.database_pool_recycle,
        pool_pre_ping=settings.database_pool_pre_ping,

        # Echo SQL in development
        echo=settings.database_echo,
    )

# ============================================================================
# SESSION FACTORY
# ============================================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

# ============================================================================
# DECLARATIVE BASE - Imported from models to ensure all models use same Base
# ============================================================================

# Base will be imported from models after models are defined
Base = None

# ============================================================================
# DATABASE EVENT LISTENERS
# ============================================================================


@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    """Enable foreign keys on SQLite connections"""
    # This is for SQLite only, PostgreSQL has them enabled by default
    pass

# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    Yields a session and ensures cleanup after use.

    Usage in FastAPI routes:
        def my_endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================


def init_db() -> None:
    """
    Initialize database by creating all tables.
    Run this once at application startup.
    """
    try:
        # Import models to register them with their Base
        from app.models import Base as ModelsBase
        ModelsBase.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def close_db() -> None:
    """
    Close database connections.
    Run this at application shutdown.
    """
    try:
        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")
        raise

# ============================================================================
# HEALTH CHECK
# ============================================================================


def check_db_connection() -> bool:
    """
    Check if database connection is healthy.

    Returns:
        bool: True if connection is healthy, False otherwise
    """
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return result is not None
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False
