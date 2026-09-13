"""
Aiteebar AI Security - FastAPI Application
Main entry point for the backend API server
"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from datetime import datetime

# Initialize FastAPI application
app = FastAPI(
    title="Aiteebar AI Security API",
    description="AI-powered security analysis and threat intelligence platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for the API server"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "aiteebar-api",
        "version": "0.1.0"
    }

@app.get("/health/db", tags=["Health"])
async def database_health_check():
    """Database health check endpoint"""
    try:
        # TODO: Add database connection check
        return {
            "status": "healthy",
            "database": "PostgreSQL",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "PostgreSQL",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root API endpoint"""
    return {
        "message": "Welcome to Aiteebar AI Security API",
        "docs": "/docs",
        "version": "0.1.0"
    }

# API Routes (to be implemented)
# TODO: Add authentication routes
# TODO: Add security scan routes
# TODO: Add threat intelligence routes
# TODO: Add user management routes
# TODO: Add audit logging routes

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "status": 500,
                "timestamp": datetime.utcnow().isoformat(),
                "requestId": getattr(request.state, "request_id", "unknown")
            }
        }
    )

# Application startup/shutdown events
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("🚀 Aiteebar AI Security API starting up...")
    # TODO: Initialize database connections
    # TODO: Initialize cache connections
    # TODO: Load configuration

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("🛑 Aiteebar AI Security API shutting down...")
    # TODO: Close database connections
    # TODO: Close cache connections

if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", 8000))
    debug = os.getenv("BACKEND_DEBUG", "true").lower() == "true"
    workers = int(os.getenv("BACKEND_WORKERS", 4)) if not debug else 1

    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        workers=workers if not debug else 1,
        log_level="info"
    )
