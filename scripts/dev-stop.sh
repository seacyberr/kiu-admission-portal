#!/usr/bin/env bash
# Stop Docker-based dev stack. Usage: ./scripts/dev-stop.sh (from repo root)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

COMPOSE_FILE="scripts/docker-compose.dev.yml"

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  echo "ERROR: docker compose is not installed."
  exit 1
fi

echo "Stopping development environment..."
"${COMPOSE_CMD[@]}" -f "$COMPOSE_FILE" down
echo "Stopped."
