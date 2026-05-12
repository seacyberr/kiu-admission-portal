#!/usr/bin/env bash
# Unix/Linux/macOS — start Docker-based dev stack (DB + Redis + API + Vite).
# Usage: from repo root → ./scripts/dev-start.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

COMPOSE_FILE="scripts/docker-compose.dev.yml"

echo "=========================================="
echo "KIU Admission Portal - Dev Environment"
echo "=========================================="
echo

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker is not running. Start Docker Desktop or the Docker daemon."
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  echo "ERROR: docker compose is not installed."
  exit 1
fi

echo "[1/3] Building and starting services (${COMPOSE_FILE})..."
"${COMPOSE_CMD[@]}" -f "$COMPOSE_FILE" up --build -d

echo
echo "[2/3] Waiting for database..."
sleep 10

echo
echo "[3/3] Ensuring tables exist (API container)..."
"${COMPOSE_CMD[@]}" -f "$COMPOSE_FILE" exec -T api python -c \
  "from app import create_app, db; app = create_app(); ctx = app.app_context(); ctx.push(); db.create_all()" \
  || true

echo
echo "=========================================="
echo "Development stack is up."
echo "=========================================="
echo
echo "URLs:"
echo "  - API:       http://localhost:5001"
echo "  - Frontend:  http://localhost:5173"
echo "  - MySQL:     localhost:3307 (user kiu_dev / kiu_dev_password)"
echo "  - Redis:     localhost:6379"
echo
echo "Logs:    ${COMPOSE_CMD[*]} -f $COMPOSE_FILE logs -f"
echo "Stop:    ${COMPOSE_CMD[*]} -f $COMPOSE_FILE down"
echo
