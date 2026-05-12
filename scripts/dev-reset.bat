@echo off
REM WARNING: removes Docker Compose volumes for the dev stack (all DB data in that stack).
cd /d "%~dp0.."

echo This will run: docker compose -f scripts\docker-compose.dev.yml down -v
echo Then it will call scripts\dev-start.bat
echo.
set /p confirm="Continue? (Y/N): "
if /I not "%confirm%"=="Y" (
  echo Cancelled.
  pause
  exit /b 0
)

docker compose version >nul 2>&1
if %errorlevel%==0 (
  set COMPOSE_CMD=docker compose
) else (
  where docker-compose >nul 2>&1
  if errorlevel 1 (
    echo ERROR: docker compose is not available.
    pause
    exit /b 1
  )
  set COMPOSE_CMD=docker-compose
)

%COMPOSE_CMD% -f scripts\docker-compose.dev.yml down -v
call scripts\dev-start.bat
