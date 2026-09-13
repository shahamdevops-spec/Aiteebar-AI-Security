"""
Custom exception classes for Aiteebar API.
Structured exceptions for consistent error handling.
"""

from fastapi import HTTPException, status
from typing import Optional, Any


class AiteebarException(Exception):
    """Base exception for all Aiteebar exceptions"""

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[dict] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AiteebarException):
    """Raised when input validation fails"""

    def __init__(
        self,
        message: str,
        details: Optional[dict] = None,
    ):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class AuthenticationError(AiteebarException):
    """Raised when authentication fails"""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[dict] = None,
    ):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_FAILED",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class AuthorizationError(AiteebarException):
    """Raised when user lacks required permissions"""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        details: Optional[dict] = None,
    ):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_FAILED",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class ResourceNotFoundError(AiteebarException):
    """Raised when a requested resource is not found"""

    def __init__(
        self,
        resource_type: str,
        resource_id: Any = None,
    ):
        message = f"{resource_type} not found"
        if resource_id:
            message += f" (ID: {resource_id})"

        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={
                "resource_type": resource_type,
                "resource_id": str(resource_id) if resource_id else None,
            },
        )


class ConflictError(AiteebarException):
    """Raised when there is a resource conflict"""

    def __init__(
        self,
        message: str,
        details: Optional[dict] = None,
    ):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class DatabaseError(AiteebarException):
    """Raised when a database operation fails"""

    def __init__(
        self,
        message: str = "Database operation failed",
        details: Optional[dict] = None,
    ):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class ExternalServiceError(AiteebarException):
    """Raised when an external service call fails"""

    def __init__(
        self,
        service_name: str,
        message: str = "External service error",
        details: Optional[dict] = None,
    ):
        super().__init__(
            message=f"{service_name}: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"service": service_name, **(details or {})},
        )


class RateLimitError(AiteebarException):
    """Raised when rate limit is exceeded"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        details: Optional[dict] = None,
    ):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details,
        )


def create_error_response(exception: AiteebarException) -> dict:
    """
    Create a standardized error response from an exception.

    Args:
        exception: AiteebarException instance

    Returns:
        dict: Formatted error response
    """
    from datetime import datetime, timezone

    return {
        "error": {
            "code": exception.error_code,
            "message": exception.message,
            "status": exception.status_code,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": exception.details,
        }
    }
