#!/usr/bin/env bash
# WARNING: removes dev Compose volumes (database data). Usage: ./scripts/dev-reset.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

COMPOSE_FILE="scripts/docker-compose.dev.yml"

echo "=========================================="
echo "KIU Admission Portal - Dev Environment Reset"
echo "=========================================="
echo "This runs: docker compose down -v (deletes Compose volumes for this project)."
echo

read -r -p "Continue? (y/N) " reply
if [[ ! "${reply:-}" =~ ^[Yy]$ ]]; then
  echo "Cancelled."
  exit 0
fi

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  echo "ERROR: docker compose is not installed."
  exit 1
fi

"${COMPOSE_CMD[@]}" -f "$COMPOSE_FILE" down -v
echo "Volumes removed. Re-run ./scripts/dev-start.sh to rebuild."
