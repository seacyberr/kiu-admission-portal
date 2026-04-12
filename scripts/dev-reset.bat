@echo off
REM Windows development environment reset script
REM WARNING: This will delete all data and rebuild everything

echo ==========================================
echo KIU Admission Portal - Dev Environment Reset
echo ==========================================
echo.
echo WARNING: This will DELETE all:
echo   - Database data
echo   - Uploaded files
echo   - Local development files
echo.
echo Are you sure you want to continue? (Y/N)
set /p confirm=
if /I not "%confirm%"=="Y" (
    echo Reset cancelled.
    pause
    exit /b 0
)

echo.
echo [1/4] Stopping all services...
docker-compose -f docker-compose.dev.yml down

echo.
echo [2/4] Removing all volumes (data)...
docker volume rm kiu-admission-portal_mysql_data 2>nul || echo MySQL volume not found
docker volume rm kiu-admission-portal_redis_data 2>nul || echo Redis volume not found
docker volume rm kiu-admission-portal_api_uploads 2>nul || echo Uploads volume not found
docker volume rm kiu-admission-portal_api_logs 2>nul || echo Logs volume not found
docker volume rm kiu-admission-portal_api_venv 2>nul || echo Venv volume not found
docker volume rm kiu-admission-portal_frontend_node_modules 2>nul || echo Node modules volume not found

echo.
echo [3/4] Removing unused Docker resources...
docker system prune -f --volumes

echo.
echo [4/4] Rebuilding and starting fresh environment...
call scripts\dev-start.bat

echo.
echo ==========================================
echo Environment reset complete!
echo ==========================================
pause
