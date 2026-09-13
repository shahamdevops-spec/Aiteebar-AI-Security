#!/bin/bash
# Database initialization script for PostgreSQL
# This script runs automatically when the PostgreSQL container starts
# It creates initial database structures and extensions

set -e

echo "=== Aiteebar Database Initialization ==="
echo "Initializing database: $POSTGRES_DB"

# Enable PostgreSQL extensions
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Enable UUID extension
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    -- Enable JSON/JSONB support (usually enabled by default)
    CREATE EXTENSION IF NOT EXISTS "json";

    -- Enable full-text search
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";

    -- Enable hstore for key-value storage
    CREATE EXTENSION IF NOT EXISTS "hstore";

    -- Create schema for application
    CREATE SCHEMA IF NOT EXISTS public;

    -- Set search path
    ALTER ROLE "$POSTGRES_USER" SET search_path TO public;

    -- Grant privileges
    GRANT USAGE ON SCHEMA public TO "$POSTGRES_USER";
    GRANT CREATE ON SCHEMA public TO "$POSTGRES_USER";

EOSQL

echo "✓ Database extensions enabled"

# Create indexes and base tables (optional - usually done by ORM)
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Base tables will be created by Alembic migrations
    -- This script just sets up the database structure

    -- Log initialization completion
    SELECT now() as "Database initialized at",
           version() as "PostgreSQL version";

EOSQL

echo "✓ Database initialization complete"
echo ""
