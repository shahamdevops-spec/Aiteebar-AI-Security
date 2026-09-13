#!/bin/bash
# Reset database script
# Removes all data and recreates the database from scratch
# WARNING: This will delete all data!

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "⚠️  WARNING: This will DELETE all data from the database!"
echo ""
read -p "Are you sure? Type 'yes' to confirm: " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Aborted."
    exit 1
fi

echo ""
echo "🔄 Resetting database..."
echo ""

# Check if running with Docker
if command -v docker-compose &> /dev/null; then
    echo "1. Stopping containers..."
    cd "$PROJECT_ROOT"
    docker-compose down

    echo ""
    echo "2. Removing volumes..."
    docker-compose down -v

    echo ""
    echo "3. Starting fresh..."
    docker-compose up -d

    echo ""
    echo "4. Waiting for services..."
    sleep 10

    echo ""
    echo "5. Running migrations..."
    docker-compose exec -T backend alembic upgrade head || true

    echo ""
    echo "✅ Database reset complete!"
    echo ""
    echo "Services are running:"
    docker-compose ps
else
    echo "❌ docker-compose not found. Please ensure Docker is installed."
    exit 1
fi

echo ""
echo "Next steps:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Database UI: http://localhost:8080"
echo ""
