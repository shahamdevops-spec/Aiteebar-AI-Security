"""
Security utilities for authentication, password hashing, and JWT token handling.
Provides password hashing with bcrypt and JWT token generation/validation.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# ============================================================================
# PASSWORD HASHING
# ============================================================================

# Password hashing context with bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)

# HTTP Bearer security scheme
security = HTTPBearer()


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to check against

    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

# ============================================================================
# JWT TOKEN HANDLING
# ============================================================================


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        subject: The subject claim (usually user ID or email)
        expires_delta: Custom expiration time delta
        additional_claims: Additional claims to include in token

    Returns:
        str: Encoded JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.jwt_expiration_hours)

    # Calculate expiration time
    expire = datetime.now(timezone.utc) + expires_delta

    # Build claims
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    # Add additional claims if provided
    if additional_claims:
        to_encode.update(additional_claims)

    # Encode token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def create_refresh_token(subject: str) -> str:
    """
    Create a JWT refresh token.

    Args:
        subject: The subject claim (usually user ID)

    Returns:
        str: Encoded refresh JWT token
    """
    expires_delta = timedelta(days=settings.refresh_token_expiration_days)
    return create_access_token(
        subject=subject,
        expires_delta=expires_delta,
        additional_claims={"type": "refresh"}
    )


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token to decode

    Returns:
        dict: Decoded token claims

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError as e:
        logger.warning(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================================
# DEPENDENCY INJECTION FOR SECURITY
# ============================================================================


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Dependency to get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer credentials from request

    Returns:
        dict: Token claims containing user information

    Raises:
        HTTPException: If token is invalid or missing
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    claims = decode_token(token)

    # Verify token is not a refresh token
    if claims.get("type") == "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cannot use refresh token as access token",
        )

    return claims


async def get_current_user_id(
    current_user: dict = Depends(get_current_user),
) -> str:
    """
    Dependency to get current user's ID.

    Args:
        current_user: Current authenticated user claims

    Returns:
        str: User ID from token subject

    Raises:
        HTTPException: If user ID is missing
    """
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )
    return user_id


async def require_role(required_roles: list):
    """
    Create a dependency that requires specific roles.

    Args:
        required_roles: List of allowed roles

    Returns:
        Callable: Dependency function

    Example:
        @router.get("/admin-only")
        async def admin_endpoint(
            current_user: dict = Depends(require_role(["admin"]))
        ):
            ...
    """
    async def check_role(
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        user_role = current_user.get("role")
        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of roles: {required_roles}",
            )
        return current_user

    return check_role


# ============================================================================
# DECORATORS FOR ROLE-BASED ACCESS CONTROL
# ============================================================================


def require_admin(func):
    """Decorator to require admin role"""
    async def wrapper(
        current_user: dict = Depends(require_role(["admin"])),
    ):
        return await func(current_user)
    return wrapper


def require_analyst(func):
    """Decorator to require analyst role"""
    async def wrapper(
        current_user: dict = Depends(
            require_role(["admin", "analyst"])
        ),
    ):
        return await func(current_user)
    return wrapper
