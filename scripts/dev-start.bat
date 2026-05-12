@echo off
REM Windows — Docker dev stack (DB + Redis + API + Vite). Run from anywhere.
cd /d "%~dp0.."

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

REM Check if docker compose or docker-compose is available
where docker >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not in PATH.
    pause
    exit /b 1
)

docker compose version >nul 2>&1
if %errorlevel%==0 (
    set COMPOSE_CMD=docker compose
) else (
    where docker-compose >nul 2>&1
    if errorlevel 1 (
        echo ERROR: docker compose or docker-compose is not available.
        pause
        exit /b 1
    ) else (
        set COMPOSE_CMD=docker-compose
    )
)

echo [1/4] Building and starting services...
%COMPOSE_CMD% -f scripts\docker-compose.dev.yml up --build -d

if errorlevel 1 (
    echo ERROR: Failed to start services!
    pause
    exit /b 1
)

echo.
echo [2/4] Waiting for database to be ready...
timeout /t 10 /nobreak >nul

echo.
echo [3/4] Ensuring DB tables...
%COMPOSE_CMD% -f scripts\docker-compose.dev.yml exec -T api python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

echo.
echo [4/4] Done (seed runs inside API container when SEED_DATABASE=true).

echo.
echo ==========================================
echo Development environment ready!
echo ==========================================
echo.
echo Services:
echo   - API:      http://localhost:5001
echo   - Frontend: http://localhost:5173
echo   - MySQL:    localhost:3307
echo   - Redis:    localhost:6379
echo.
echo Useful commands:
echo   - View logs:   %COMPOSE_CMD% -f scripts\docker-compose.dev.yml logs -f
echo   - Stop all:    %COMPOSE_CMD% -f scripts\docker-compose.dev.yml down
echo   - Restart API: %COMPOSE_CMD% -f scripts\docker-compose.dev.yml restart api
echo.
echo Database credentials (dev only):
echo   - User: kiu_dev / kiu_dev_password
echo   - Root: root / root_dev_password
echo.
pause
