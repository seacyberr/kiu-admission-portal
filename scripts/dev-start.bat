@echo off
REM Windows development environment startup script
REM Usage: scripts\dev-start.bat

echo ==========================================
echo KIU Admission Portal - Dev Environment
echo ==========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Check if docker-compose is available
where docker-compose >nul 2>&1
if errorlevel 1 (
    echo ERROR: docker-compose not found!
    echo Please install Docker Desktop with docker-compose.
    pause
    exit /b 1
)

echo [1/4] Building and starting services...
docker-compose -f docker-compose.dev.yml up --build -d

if errorlevel 1 (
    echo ERROR: Failed to start services!
    pause
    exit /b 1
)

echo.
echo [2/4] Waiting for database to be ready...
timeout /t 10 /nobreak >nul

echo.
echo [3/4] Running database migrations...
docker-compose -f docker-compose.dev.yml exec -T api python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

echo.
echo [4/4] Seeding database (if needed)...
docker-compose -f docker-compose.dev.yml exec -T api python -c "from scripts.seed_data import seed_programs; seed_programs()" 2>nul || echo Seed data skipped or already exists

echo.
echo ==========================================
echo Development environment ready!
echo ==========================================
echo.
echo Services:
echo   - API:      http://localhost:5001
echo   - Frontend: http://localhost:5173
echo   - MySQL:    localhost:3306
echo   - Redis:    localhost:6379
echo.
echo Useful commands:
echo   - View logs:   docker-compose -f docker-compose.dev.yml logs -f
echo   - Stop all:    docker-compose -f docker-compose.dev.yml down
echo   - Restart API: docker-compose -f docker-compose.dev.yml restart api
echo.
echo Database credentials (dev only):
echo   - User: kiu_dev / kiu_dev_password
echo   - Root: root / root_dev_password
echo.
pause
