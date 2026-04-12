# Cleanup Script - Windows PowerShell
# Usage: .\cleanup.ps1 [all|docker|node|python|test-results]

$ErrorActionPreference = "Stop"

# Colors
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"

Write-Host "=== KIU Admission Portal Cleanup ===" -ForegroundColor $Yellow

# Detect Docker Compose command
if (Get-Command "docker-compose" -ErrorAction SilentlyContinue) {
    $DOCKER_COMPOSE = "docker-compose"
} else {
    $DOCKER_COMPOSE = "docker compose"
}

$CLEAN_TYPE = $args[0]
if (-not $CLEAN_TYPE) { $CLEAN_TYPE = "all" }

switch ($CLEAN_TYPE) {
    "docker" {
        Write-Host "Stopping and removing Docker containers..." -ForegroundColor $Red
        Invoke-Expression "$DOCKER_COMPOSE -f docker-compose.test.yml down -v 2>`$null" -ErrorAction SilentlyContinue
        docker system prune -f
        Write-Host "Docker cleaned!" -ForegroundColor $Green
    }
    
    "node" {
        Write-Host "Cleaning Node.js dependencies and build files..." -ForegroundColor $Red
        Remove-Item -Recurse -Force -Path "apps\kiu-portal\node_modules" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force -Path "apps\kiu-portal\dist" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force -Path "apps\kiu-portal\playwright-report" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force -Path "apps\kiu-portal\test-results" -ErrorAction SilentlyContinue
        Write-Host "Frontend cleaned!" -ForegroundColor $Green
    }
    
    "python" {
        Write-Host "Cleaning Python virtual environment..." -ForegroundColor $Red
        Remove-Item -Recurse -Force -Path "apps\flask-api\venv" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force -Path "apps\flask-api\__pycache__" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force -Path "apps\flask-api\.pytest_cache" -ErrorAction SilentlyContinue
        Get-ChildItem -Path "apps\flask-api" -Recurse -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
        Write-Host "Backend cleaned!" -ForegroundColor $Green
    }
    
    "test-results" {
        Write-Host "Cleaning test results and reports..." -ForegroundColor $Red
        Remove-Item -Recurse -Force -Path "apps\kiu-portal\playwright-report" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force -Path "apps\kiu-portal\test-results" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force -Path "apps\flask-api\.pytest_cache" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force -Path "apps\flask-api\htmlcov" -ErrorAction SilentlyContinue
        Remove-Item -Force -Path "apps\flask-api\.coverage" -ErrorAction SilentlyContinue
        Write-Host "Test results cleaned!" -ForegroundColor $Green
    }
    
    default {
        Write-Host "Performing FULL cleanup..." -ForegroundColor $Red
        
        # Docker
        Write-Host "1. Cleaning Docker..." -ForegroundColor $Yellow
        Invoke-Expression "$DOCKER_COMPOSE -f docker-compose.test.yml down -v 2>`$null" -ErrorAction SilentlyContinue
        docker system prune -f 2>$null
        
        # Frontend
        Write-Host "2. Cleaning Frontend (Node.js)..." -ForegroundColor $Yellow
        Remove-Item -Recurse -Force -Path "apps\kiu-portal\node_modules" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force -Path "apps\kiu-portal\dist" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force -Path "apps\kiu-portal\playwright-report" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force -Path "apps\kiu-portal\test-results" -ErrorAction SilentlyContinue
        
        # Backend
        Write-Host "3. Cleaning Backend (Python)..." -ForegroundColor $Yellow
        Remove-Item -Recurse -Force -Path "apps\flask-api\venv" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force -Path "apps\flask-api\__pycache__" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force -Path "apps\flask-api\.pytest_cache" -ErrorAction SilentlyContinue
        Get-ChildItem -Path "apps\flask-api" -Recurse -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
        
        # Root level
        Write-Host "4. Cleaning root level files..." -ForegroundColor $Yellow
        Remove-Item -Force -Path ".coverage" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force -Path "htmlcov" -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force -Path ".pytest_cache" -ErrorAction SilentlyContinue
        
        Write-Host "✅ FULL cleanup complete!" -ForegroundColor $Green
        Write-Host "To reinstall:" -ForegroundColor $Yellow
        Write-Host "  Backend: cd apps\flask-api; python -m venv venv; .\venv\Scripts\activate; pip install -r requirements.txt"
        Write-Host "  Frontend: cd apps\kiu-portal; npm install"
    }
}

Write-Host "Cleanup finished!" -ForegroundColor $Green
