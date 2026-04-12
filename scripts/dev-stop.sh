#!/bin/bash
# Unix/Linux/macOS development environment stop script

echo "Stopping development environment..."
docker-compose -f docker-compose.dev.yml down

echo
echo "Development environment stopped."
