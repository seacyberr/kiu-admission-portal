@echo off
REM Windows development environment stop script

echo Stopping development environment...
docker-compose -f docker-compose.dev.yml down

echo.
echo Development environment stopped.
pause
