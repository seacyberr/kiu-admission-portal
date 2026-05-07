#!/bin/bash
# Unix/Linux/macOS development environment reset script
# WARNING: This will delete all data and rebuild everything

set -e

echo "=========================================="
echo "KIU Admission Portal - Dev Environment Reset"
echo "=========================================="
echo
echo "WARNING: This will DELETE all:"
echo "  - Database data"
echo "  - Uploaded files"
echo "  - Local development files"
echo

read -p "Are you sure you want to continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Reset cancelled."
    exit 0
fi

# Get project name from directory
PROJECT_NAME=$(basename "$PWD")

echo
echo "[1/4] Stopping all services..."
if command -v docker compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
else
    echo "ERROR: docker compose is not available."
    exit 1
fi
$COMPOSE_CMD -f docker-compose.dev.yml down

echo
echo "[2/4] Removing all volumes (data)..."
docker volume rm ${PROJECT_NAME}_mysql_data 2>/dev/null || echo "MySQL volume not found"
docker volume rm ${PROJECT_NAME}_redis_data 2>/dev/null || echo "Redis volume not found"
docker volume rm ${PROJECT_NAME}_api_uploads 2>/dev/null || echo "Uploads volume not found"
docker volume rm ${PROJECT_NAME}_api_logs 2>/dev/null || echo "Logs volume not found"
docker volume rm ${PROJECT_NAME}_api_venv 2>/dev/null || echo "Venv volume not found"
docker volume rm ${PROJECT_NAME}_frontend_node_modules 2>/dev/null || echo "Node modules volume not found"

echo
echo "[3/4] Removing unused Docker resources..."
docker system prune -f --volumes

echo
echo "[4/4] Rebuilding and starting fresh environment..."
./scripts/dev-start.sh

echo
echo "=========================================="
echo "Environment reset complete!"
echo "=========================================="
