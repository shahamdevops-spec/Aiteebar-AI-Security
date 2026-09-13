"""
Main FastAPI application for Aiteebar AI Security.
Entry point with middleware, exception handlers, and route setup.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import time
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db, close_db, check_db_connection
from app.exceptions import (
    AiteebarException,
    create_error_response,
    DatabaseError,
)
from app.routers import (
    auth, dashboard, applications, risk, dlp, threats, risk_score,
    policies, simulation, events, alerts,
)

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# LIFESPAN EVENTS
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan events (startup/shutdown).
    """
    # STARTUP
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")

    try:
        init_db()
        logger.info("Database initialized")

        if not check_db_connection():
            logger.warning("Database connection check failed")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

    yield

    # SHUTDOWN
    logger.info("Shutting down application")
    try:
        close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================


app = FastAPI(
    title=settings.app_name,
    description="AI-powered security analysis and threat intelligence platform",
    version=settings.app_version,
    docs_url=settings.docs_url if settings.api_docs_enabled else None,
    redoc_url=settings.redoc_url if settings.api_docs_enabled else None,
    openapi_url=settings.openapi_url if settings.api_docs_enabled else None,
    lifespan=lifespan,
)

# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses"""
    request_id = request.headers.get("X-Request-ID", str(time.time()))

    # Log request
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} - "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )

    # Process request
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Add custom headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id

    # Log response
    logger.info(
        f"[{request_id}] {response.status_code} - "
        f"Duration: {process_time:.2f}s"
    )

    return response

# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================


@app.exception_handler(AiteebarException)
async def aiteebar_exception_handler(request: Request, exc: AiteebarException):
    """Handle custom Aiteebar exceptions"""
    logger.error(f"Aiteebar error: {exc.error_code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(exc),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    logger.warning(f"Validation error: {exc}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "status": 422,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": exc.errors(),
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # This handler runs in ServerErrorMiddleware, which sits outside
    # CORSMiddleware, so the response would otherwise carry no CORS headers and
    # a browser would surface the 500 as an opaque network failure instead of
    # the message below. Echo the headers here when the origin is allowed.
    headers = {}
    origin = request.headers.get("origin")
    if origin and (origin in settings.cors_origins or "*" in settings.cors_origins):
        headers["Access-Control-Allow-Origin"] = origin
        headers["Vary"] = "Origin"
        if settings.cors_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "status": 500,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
        headers=headers,
    )

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify API is running.

    Returns:
        dict: Health status and timestamp
    """
    db_healthy = check_db_connection()

    if not db_healthy:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "aiteebar-api",
                "version": settings.app_version,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "components": {
                    "database": "unhealthy",
                }
            },
        )

    return {
        "status": "healthy",
        "service": "aiteebar-api",
        "version": settings.app_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": settings.environment,
        "components": {
            "database": "healthy",
        }
    }


@app.get("/health/db", tags=["Health"])
async def health_check_db():
    """
    Database health check endpoint.

    Returns:
        dict: Database health status
    """
    try:
        db_healthy = check_db_connection()
        status_str = "healthy" if db_healthy else "unhealthy"

        return {
            "status": status_str,
            "database": "PostgreSQL",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "PostgreSQL",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

# ============================================================================
# ROOT ENDPOINT
# ============================================================================


@app.get("/", tags=["Root"])
async def root():
    """
    Root API endpoint with service information.

    Returns:
        dict: API information and documentation links
    """
    return {
        "message": "Welcome to Aiteebar AI Security API",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "documentation": {
            "swagger": settings.docs_url if settings.api_docs_enabled else None,
            "redoc": settings.redoc_url if settings.api_docs_enabled else None,
        },
        "health": "/health",
    }

# ============================================================================
# ROUTE REGISTRATION
# ============================================================================

# Authentication routes
app.include_router(auth.router)

# Dashboard routes
app.include_router(dashboard.router)

app.include_router(applications.router)
app.include_router(risk.router)

# DLP routes
app.include_router(dlp.router)

# Threat Detection routes
app.include_router(threats.router)

# Risk Scoring routes
app.include_router(risk_score.router)

# Policy Management routes
app.include_router(policies.router)

# Simulation routes
app.include_router(simulation.router)

# Security event logging
app.include_router(events.router)

# SOC alerting
app.include_router(alerts.router)

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
