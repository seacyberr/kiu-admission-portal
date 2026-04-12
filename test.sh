#!/bin/bash
# Test Runner Script - Docker-based
# Cross-platform: Works on Linux, macOS, and Windows (Git Bash/WSL)
# Usage: ./test.sh [backend|frontend|all]

set -e

COMPOSE_FILE="docker-compose.test.yml"

# Detect OS
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    PLATFORM="windows"
    # Use 'docker-compose' on Windows (older versions)
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    else
        DOCKER_COMPOSE="docker compose"
    fi
else
    PLATFORM="unix"
    # Use 'docker compose' (new) or 'docker-compose' (old)
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
    else
        DOCKER_COMPOSE="docker-compose"
    fi
fi

# Colors for output (disable on Windows if not ANSI supported)
if [[ "$PLATFORM" == "windows" ]] && [[ -z "$FORCE_COLOR" ]]; then
    RED=''
    GREEN=''
    YELLOW=''
    NC=''
else
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
fi

echo -e "${YELLOW}=== KIU Admission Portal Test Runner ===${NC}"
echo -e "Platform: $PLATFORM"
echo -e "Docker Compose: $DOCKER_COMPOSE"

# Function to cleanup
cleanup() {
    echo -e "${YELLOW}Cleaning up...${NC}"
    $DOCKER_COMPOSE -f $COMPOSE_FILE down -v 2>/dev/null || true
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Check Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker is not running or not installed${NC}"
    echo "Please start Docker Desktop first"
    exit 1
fi

# Parse arguments
TEST_TYPE=${1:-all}

case $TEST_TYPE in
    backend)
        echo -e "${GREEN}Running Backend Tests Only...${NC}"
        $DOCKER_COMPOSE -f $COMPOSE_FILE up --build --abort-on-container-exit mysql redis api
        ;;
    
    frontend)
        echo -e "${GREEN}Running Frontend E2E Tests Only...${NC}"
        $DOCKER_COMPOSE -f $COMPOSE_FILE up --build --abort-on-container-exit frontend
        ;;
    
    all|*)
        echo -e "${GREEN}Running All Tests...${NC}"
        $DOCKER_COMPOSE -f $COMPOSE_FILE up --build --abort-on-container-exit
        ;;
esac

echo -e "${GREEN}=== Tests Complete ===${NC}"
echo -e "View Playwright report at: http://localhost:9323"
