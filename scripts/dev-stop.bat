@echo off
REM Windows development environment stop script

echo Stopping development environment...
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

%COMPOSE_CMD% -f docker-compose.dev.yml down

echo.
echo Development environment stopped.
pause
