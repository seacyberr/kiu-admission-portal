#!/bin/bash
# Unix/Linux/macOS development environment stop script

echo "Stopping development environment..."
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
echo "Development environment stopped."
