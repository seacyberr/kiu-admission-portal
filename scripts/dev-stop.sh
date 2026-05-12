#!/usr/bin/env bash
# KIU Admission Portal - Stop Docker Development Environment
# Stops KIU Database, Redis, API, and Frontend services
# Usage: from KIU repo root → ./scripts/dev-stop.sh

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

echo "Stopping KIU Admission Portal development environment..."
"${COMPOSE_CMD[@]}" -f "$COMPOSE_FILE" down
echo "KIU development environment stopped."
