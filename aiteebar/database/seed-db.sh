#!/bin/bash
# Database seeding script for demo data
# This script runs after init-db.sh to populate demo data
# Only runs if database is empty (development only)

set -e

echo "=== Aiteebar Database Seeding ==="
echo "Seeding demo data for development..."

# Check if demo data already exists
TABLE_COUNT=$(psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
    -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null || echo "0")

if [ "$TABLE_COUNT" -gt 0 ]; then
    echo "ℹ️  Database already has tables. Skipping seed (development only)."
    exit 0
fi

echo "No existing data found, proceeding with seed..."

# Seed sample data using SQL (optional - usually done by Python scripts)
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- This is a placeholder for demo data
    -- Actual seeding is typically done by Python ORM and scripts

    -- Example: Create a test user (commented out - use Python script instead)
    -- INSERT INTO users (id, email, password_hash, role) VALUES
    -- (gen_random_uuid(), 'admin@example.com', '\$2b\$12\$...', 'admin');

    -- Log seeding completion
    SELECT now() as "Seed completed at";

EOSQL

echo "✓ Database seeding complete"
echo ""
echo "Note: For comprehensive demo data, run the Python seed script:"
echo "  python scripts/seed_database.py"
echo ""
