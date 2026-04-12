#!/bin/bash
# Cleanup Script - Linux/macOS/WSL
# Usage: ./cleanup.sh [all|docker|node|python|test-results]

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== KIU Admission Portal Cleanup ===${NC}"

# Detect Docker Compose command
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

CLEAN_TYPE=${1:-all}

case $CLEAN_TYPE in
    docker|containers)
        echo -e "${RED}Stopping and removing Docker containers...${NC}"
        $DOCKER_COMPOSE -f docker-compose.test.yml down -v 2>/dev/null || true
        docker system prune -f
        echo -e "${GREEN}Docker cleaned!${NC}"
        ;;
    
    node|frontend)
        echo -e "${RED}Cleaning Node.js dependencies and build files...${NC}"
        rm -rf apps/kiu-portal/node_modules
        rm -rf apps/kiu-portal/dist
        rm -rf apps/kiu-portal/playwright-report
        rm -rf apps/kiu-portal/test-results
        echo -e "${GREEN}Frontend cleaned!${NC}"
        ;;
    
    python|backend)
        echo -e "${RED}Cleaning Python virtual environment...${NC}"
        rm -rf apps/flask-api/venv
        rm -rf apps/flask-api/__pycache__
        rm -rf apps/flask-api/.pytest_cache
        find apps/flask-api -name "*.pyc" -delete
        find apps/flask-api -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        echo -e "${GREEN}Backend cleaned!${NC}"
        ;;
    
    test-results|reports)
        echo -e "${RED}Cleaning test results and reports...${NC}"
        rm -rf apps/kiu-portal/playwright-report
        rm -rf apps/kiu-portal/test-results
        rm -rf apps/flask-api/.pytest_cache
        rm -rf apps/flask-api/htmlcov
        rm -f apps/flask-api/.coverage
        echo -e "${GREEN}Test results cleaned!${NC}"
        ;;
    
    all|*)
        echo -e "${RED}Performing FULL cleanup...${NC}"
        
        # Docker
        echo -e "${YELLOW}1. Cleaning Docker...${NC}"
        $DOCKER_COMPOSE -f docker-compose.test.yml down -v 2>/dev/null || true
        docker system prune -f 2>/dev/null || true
        
        # Frontend
        echo -e "${YELLOW}2. Cleaning Frontend (Node.js)...${NC}"
        rm -rf apps/kiu-portal/node_modules
        rm -rf apps/kiu-portal/dist
        rm -rf apps/kiu-portal/playwright-report
        rm -rf apps/kiu-portal/test-results
        
        # Backend
        echo -e "${YELLOW}3. Cleaning Backend (Python)...${NC}"
        rm -rf apps/flask-api/venv
        rm -rf apps/flask-api/__pycache__
        rm -rf apps/flask-api/.pytest_cache
        find apps/flask-api -name "*.pyc" -delete 2>/dev/null || true
        find apps/flask-api -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        
        # Root level
        echo -e "${YELLOW}4. Cleaning root level files...${NC}"
        rm -f .coverage
        rm -rf htmlcov
        rm -rf .pytest_cache
        
        echo -e "${GREEN}✅ FULL cleanup complete!${NC}"
        echo -e "${YELLOW}To reinstall:${NC}"
        echo -e "  Backend: cd apps/flask-api && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        echo -e "  Frontend: cd apps/kiu-portal && npm install"
        ;;
esac

echo -e "${GREEN}Cleanup finished!${NC}"
