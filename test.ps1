# Test Runner Script - Docker-based (Windows PowerShell)
# Usage: .\test.ps1 [backend|frontend|all]

$ErrorActionPreference = "Stop"

$COMPOSE_FILE = "docker-compose.test.yml"

# Detect Docker Compose command
if (Get-Command "docker-compose" -ErrorAction SilentlyContinue) {
    $DOCKER_COMPOSE = "docker-compose"
} else {
    $DOCKER_COMPOSE = "docker compose"
}

Write-Host "=== KIU Admission Portal Test Runner ===" -ForegroundColor Yellow
Write-Host "Docker Compose: $DOCKER_COMPOSE" -ForegroundColor Yellow

# Function to cleanup
function Cleanup {
    Write-Host "Cleaning up..." -ForegroundColor Yellow
    Invoke-Expression "$DOCKER_COMPOSE -f $COMPOSE_FILE down -v 2>`$null" -ErrorAction SilentlyContinue
}

# Register cleanup
trap { Cleanup }

# Check Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "Error: Docker is not running or not installed" -ForegroundColor Red
    Write-Host "Please start Docker Desktop first"
    exit 1
}

# Parse arguments
$TEST_TYPE = $args[0]
if (-not $TEST_TYPE) { $TEST_TYPE = "all" }

switch ($TEST_TYPE) {
    "backend" {
        Write-Host "Running Backend Tests Only..." -ForegroundColor Green
        Invoke-Expression "$DOCKER_COMPOSE -f $COMPOSE_FILE up --build --abort-on-container-exit mysql redis api"
    }
    "frontend" {
        Write-Host "Running Frontend E2E Tests Only..." -ForegroundColor Green
        Invoke-Expression "$DOCKER_COMPOSE -f $COMPOSE_FILE up --build --abort-on-container-exit frontend"
    }
    default {
        Write-Host "Running All Tests..." -ForegroundColor Green
        Invoke-Expression "$DOCKER_COMPOSE -f $COMPOSE_FILE up --build --abort-on-container-exit"
    }
}

Write-Host "=== Tests Complete ===" -ForegroundColor Green
Write-Host "View Playwright report at: http://localhost:9323"
