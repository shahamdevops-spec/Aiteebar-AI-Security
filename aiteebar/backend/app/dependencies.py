"""
Dependency injection utilities for FastAPI endpoints.
Common dependencies for database access, authentication, and validation.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.security import get_current_user, get_current_user_id


# ============================================================================
# DATABASE DEPENDENCIES
# ============================================================================


async def get_database() -> Session:
    """
    Get database session.

    Usage:
        @app.get("/items")
        async def read_items(db: Session = Depends(get_database)):
            ...
    """
    db = get_db()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# AUTHENTICATION DEPENDENCIES
# ============================================================================


async def get_authenticated_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Get current authenticated user.

    Requires valid JWT token in Authorization header.

    Usage:
        @app.get("/profile")
        async def get_profile(user: dict = Depends(get_authenticated_user)):
            ...
    """
    return current_user


async def get_user_id(
    user_id: str = Depends(get_current_user_id),
) -> str:
    """
    Get current user's ID.

    Usage:
        @app.get("/my-data")
        async def get_my_data(user_id: str = Depends(get_user_id)):
            ...
    """
    return user_id


async def require_admin_role(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Require admin role.

    Usage:
        @app.delete("/users/{user_id}")
        async def delete_user(
            user_id: str,
            admin: dict = Depends(require_admin_role)
        ):
            ...
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return current_user


async def require_analyst_role(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Require analyst or admin role.

    Usage:
        @app.post("/scans")
        async def create_scan(
            scan: ScanCreate,
            analyst: dict = Depends(require_analyst_role)
        ):
            ...
    """
    if current_user.get("role") not in ["admin", "analyst"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analyst role required",
        )
    return current_user


# ============================================================================
# COMMON VALIDATIONS
# ============================================================================


async def validate_positive_int(value: int = 1) -> int:
    """
    Validate that an integer is positive.

    Usage:
        @app.get("/items")
        async def read_items(skip: int = Depends(validate_positive_int)):
            ...
    """
    if value < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Value must be positive",
        )
    return value


async def validate_limit(limit: int = 100) -> int:
    """
    Validate pagination limit.

    Usage:
        @app.get("/items")
        async def list_items(limit: int = Depends(validate_limit)):
            ...
    """
    if limit < 1:
        limit = 1
    elif limit > 1000:
        limit = 1000
    return limit


# ============================================================================
# OPTIONAL DEPENDENCIES
# ============================================================================


async def get_optional_user(
    credentials: Optional[dict] = None,
) -> Optional[dict]:
    """
    Get current user if authenticated, otherwise None.

    Usage for endpoints that allow both authenticated and unauthenticated:
        @app.get("/public-items")
        async def list_public_items(
            user: Optional[dict] = Depends(get_optional_user)
        ):
            # user will be None if not authenticated
            ...
    """
    return credentials


# ============================================================================
# QUERY PARAMETER DEPENDENCIES
# ============================================================================


class CommonQueryParams:
    """Common query parameters for list endpoints"""

    def __init__(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):
        self.skip = max(0, skip)
        self.limit = min(1000, max(1, limit))
        self.search = search
        self.sort_by = sort_by
        self.sort_order = sort_order.lower() if sort_order.lower() in ["asc", "desc"] else "desc"


# ============================================================================
# COMPOSITE DEPENDENCIES
# ============================================================================


async def get_current_user_with_db(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
) -> tuple:
    """
    Get both database session and current user.

    Usage:
        @app.get("/profile")
        async def get_profile(
            deps: tuple = Depends(get_current_user_with_db)
        ):
            db, user = deps
            ...
    """
    return db, user
