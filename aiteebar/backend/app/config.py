"""
Configuration management for Aiteebar AI Security FastAPI application.
Uses Pydantic Settings for environment variable loading and validation.
"""

import json
from functools import lru_cache
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # ========================================================================
    # APPLICATION SETTINGS
    # ========================================================================

    app_name: str = Field(default="Aiteebar AI Security API", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")

    # ========================================================================
    # SERVER SETTINGS
    # ========================================================================

    backend_host: str = Field(default="0.0.0.0", env="BACKEND_HOST")
    backend_port: int = Field(default=8000, env="BACKEND_PORT")
    backend_workers: int = Field(default=4, env="BACKEND_WORKERS")

    # ========================================================================
    # DATABASE SETTINGS
    # ========================================================================

    database_url: str = Field(
        default="postgresql://aiteebar:aiteebar_password@localhost:5432/aiteebar_db",
        env="DATABASE_URL"
    )
    database_pool_size: int = Field(default=5, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")
    database_pool_recycle: int = Field(default=3600, env="DATABASE_POOL_RECYCLE")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    database_pool_pre_ping: bool = Field(default=True, env="DATABASE_POOL_PRE_PING")

    # ========================================================================
    # JWT SETTINGS
    # ========================================================================

    jwt_secret_key: str = Field(
        default="change-me-in-production-32-chars-min",
        env="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    refresh_token_expiration_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRATION_DAYS")

    # ========================================================================
    # CORS SETTINGS
    # ========================================================================

    # Stored as raw strings so a plain comma-separated .env value (the format the
    # setup docs use, e.g. CORS_ORIGINS=http://localhost:3000,http://localhost:3001)
    # loads cleanly. pydantic-settings tries to JSON-decode a List[str] env value
    # and would crash on the comma-separated form. The parsed lists are exposed via
    # the cors_origins / cors_methods / cors_headers properties defined below.
    cors_origins_raw: str = Field(
        default="http://localhost:3000,http://localhost:3001",
        validation_alias="CORS_ORIGINS"
    )
    cors_credentials: bool = Field(default=True, env="CORS_CREDENTIALS")
    cors_methods_raw: str = Field(default="*", validation_alias="CORS_METHODS")
    cors_headers_raw: str = Field(default="*", validation_alias="CORS_HEADERS")

    # ========================================================================
    # SECURITY SETTINGS
    # ========================================================================

    encryption_key: str = Field(
        default="your-encryption-key-32-chars-long",
        env="ENCRYPTION_KEY"
    )
    password_min_length: int = Field(default=8, env="PASSWORD_MIN_LENGTH")

    # ========================================================================
    # API SETTINGS
    # ========================================================================

    api_version: str = Field(default="v1", env="API_VERSION")
    api_docs_enabled: bool = Field(default=True, env="API_DOCS_ENABLED")
    openapi_url: str = Field(default="/openapi.json", env="OPENAPI_URL")
    docs_url: str = Field(default="/docs", env="DOCS_URL")
    redoc_url: str = Field(default="/redoc", env="REDOC_URL")

    # ========================================================================
    # RATE LIMITING
    # ========================================================================

    rate_limit_requests: int = Field(default=1000, env="RATE_LIMIT_REQUESTS")
    rate_limit_window_seconds: int = Field(default=3600, env="RATE_LIMIT_WINDOW_SECONDS")
    rate_limit_burst: int = Field(default=50, env="RATE_LIMIT_BURST")

    # ========================================================================
    # LOGGING
    # ========================================================================

    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")

    # ========================================================================
    # AI/ML SETTINGS
    # ========================================================================

    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="mistral", env="OLLAMA_MODEL")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")

    # ========================================================================
    # SOC ALERTING
    # ========================================================================

    # Severity at or above which an event auto-generates an alert
    alert_auto_generate_severity: str = Field(default="CRITICAL", env="ALERT_AUTO_GENERATE_SEVERITY")

    # Webhook delivery (Splunk HEC, Sentinel, generic HTTPS collector)
    alert_webhook_enabled: bool = Field(default=False, env="ALERT_WEBHOOK_ENABLED")
    alert_webhook_url: Optional[str] = Field(default=None, env="ALERT_WEBHOOK_URL")
    alert_webhook_auth_header: Optional[str] = Field(default=None, env="ALERT_WEBHOOK_AUTH_HEADER")
    alert_webhook_timeout_seconds: int = Field(default=10, env="ALERT_WEBHOOK_TIMEOUT_SECONDS")

    # Email delivery
    alert_email_enabled: bool = Field(default=False, env="ALERT_EMAIL_ENABLED")
    alert_email_from: str = Field(default="soc@aiteebar.ai", env="ALERT_EMAIL_FROM")
    alert_email_recipients_raw: str = Field(default="", validation_alias="ALERT_EMAIL_RECIPIENTS")
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")

    # ========================================================================
    # FEATURE FLAGS
    # ========================================================================

    feature_api_docs: bool = Field(default=True, env="FEATURE_API_DOCS")
    feature_health_check: bool = Field(default=True, env="FEATURE_HEALTH_CHECK")
    feature_metrics: bool = Field(default=True, env="FEATURE_METRICS")

    class Config:
        """Pydantic Config"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Ignore unrelated keys that commonly share a .env (e.g. BACKEND_DEBUG,
        # frontend NEXT_PUBLIC_* vars) instead of raising "extra inputs are not
        # permitted" and crashing startup.
        extra = "ignore"

    @staticmethod
    def _parse_list(value) -> List[str]:
        """Parse a list from an env value.

        Accepts a JSON array (e.g. ["a","b"]) or a plain comma-separated
        string (e.g. a,b). Returns [] for an empty value.
        """
        if isinstance(value, (list, tuple)):
            return [str(item).strip() for item in value]
        if not value:
            return []
        text = str(value).strip()
        if text.startswith("["):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed]
            except ValueError:
                pass
        return [item.strip() for item in text.split(",") if item.strip()]

    @property
    def cors_origins(self) -> List[str]:
        """Allowed CORS origins as a list."""
        return self._parse_list(self.cors_origins_raw)

    @property
    def cors_methods(self) -> List[str]:
        """Allowed CORS methods as a list."""
        return self._parse_list(self.cors_methods_raw)

    @property
    def cors_headers(self) -> List[str]:
        """Allowed CORS headers as a list."""
        return self._parse_list(self.cors_headers_raw)

    @property
    def alert_email_recipients(self) -> List[str]:
        """SOC alert email recipients as a list."""
        return self._parse_list(self.alert_email_recipients_raw)

    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses LRU cache to avoid reloading settings multiple times.
    """
    return Settings()


# Export settings for import
settings = get_settings()
