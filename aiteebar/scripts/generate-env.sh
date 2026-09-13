#!/bin/bash
# Generate .env file from .env.example
# This script creates a .env file with secure defaults

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

ENV_EXAMPLE="$PROJECT_ROOT/.env.example"
ENV_FILE="$PROJECT_ROOT/.env"

if [ ! -f "$ENV_EXAMPLE" ]; then
    echo "❌ Error: .env.example not found at $ENV_EXAMPLE"
    exit 1
fi

if [ -f "$ENV_FILE" ]; then
    echo "⚠️  .env file already exists. Creating backup..."
    cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%s)"
fi

echo "📝 Generating .env file from .env.example..."

# Copy example to .env
cp "$ENV_EXAMPLE" "$ENV_FILE"

# Generate secure random values for secrets
JWT_SECRET=$(openssl rand -base64 32 | tr -d '\n')
POSTGRES_PASSWORD=$(openssl rand -base64 16 | tr -d '\n')
REDIS_PASSWORD=$(openssl rand -base64 16 | tr -d '\n')

# Update .env with generated secrets (if running on macOS/Linux)
if command -v sed &> /dev/null; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET/" "$ENV_FILE"
        sed -i '' "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" "$ENV_FILE"
        sed -i '' "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PASSWORD/" "$ENV_FILE"
    else
        # Linux
        sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET/" "$ENV_FILE"
        sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" "$ENV_FILE"
        sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PASSWORD/" "$ENV_FILE"
    fi
    echo "✓ Secrets generated and inserted"
else
    echo "⚠️  sed not found. Please manually update .env with secure values:"
    echo "  JWT_SECRET_KEY=$JWT_SECRET"
    echo "  POSTGRES_PASSWORD=$POSTGRES_PASSWORD"
    echo "  REDIS_PASSWORD=$REDIS_PASSWORD"
fi

echo ""
echo "✅ .env file generated successfully!"
echo ""
echo "Next steps:"
echo "  1. Review .env file and update any values as needed"
echo "  2. Run: docker-compose up -d"
echo ""
