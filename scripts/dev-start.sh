#!/bin/bash
# Unix/Linux/macOS development environment startup script
# Usage: ./scripts/dev-start.sh

set -e

echo "=========================================="
echo "KIU Admission Portal - Dev Environment"
echo "=========================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}ERROR: Docker is not running!${NC}"
    echo "Please start Docker Desktop or Docker service first."
    exit 1
fi

# Determine Docker Compose command
if command -v docker compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
else
    echo -e "${RED}ERROR: docker compose is not available!${NC}"
    echo "Install Docker Desktop or docker-compose."
    exit 1
fi

echo -e "${YELLOW}[1/4] Building and starting services...${NC}"
$COMPOSE_CMD -f docker-compose.dev.yml up --build -d

echo
echo -e "${YELLOW}[2/4] Waiting for database to be ready...${NC}"
sleep 10

echo
echo -e "${YELLOW}[3/4] Running database migrations...${NC}"
$COMPOSE_CMD -f docker-compose.dev.yml exec -T api python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()" || true

echo
echo -e "${YELLOW}[4/4] Seeding database (if needed)...${NC}"
$COMPOSE_CMD -f docker-compose.dev.yml exec -T api python -c "from scripts.seed_data import seed_programs; seed_programs()" 2>/dev/null || echo "Seed data skipped or already exists"

echo
echo -e "${GREEN}=========================================="
echo "Development environment ready!"
echo "==========================================${NC}"
echo
echo "Services:"
echo "  - API:      http://localhost:5001"
echo "  - Frontend: http://localhost:5173"
echo "  - MySQL:    localhost:3307"
echo "  - Redis:    localhost:6379"
echo
echo "Useful commands:"
echo "  - View logs:   $COMPOSE_CMD -f docker-compose.dev.yml logs -f"
echo "  - Stop all:    $COMPOSE_CMD -f docker-compose.dev.yml down"
echo "  - Restart API: $COMPOSE_CMD -f docker-compose.dev.yml restart api"
echo
echo "Database credentials (dev only):"
echo "  - User: kiu_dev / kiu_dev_password"
echo "  - Root: root / root_dev_password"
echo
