@echo off
title JobTrack - Fullstack Server
color 0F
cls

echo ===================================================================
echo               AI LEARNING & JOB TRACKER WORKSPACE
echo           Fullstack Django Backend & Modern App UI
echo ===================================================================
echo.

:: 1. Check Python installation
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python was not found in your PATH.
    echo Please install Python 3.10+ and add it to your PATH.
    pause
    exit /b 1
)

:: 2. Apply database migrations
echo [1/3] Checking and applying database migrations...
python manage.py migrate --noinput
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Migration failed. Check your environment settings.
    pause
    exit /b 1
)
echo       Database is up to date!
echo.

:: 3. Seed demo data if not already present
echo [2/3] Checking demo data...
python manage.py seed_demo_data
echo.

:: 4. Launch browser automatically in the background
echo [3/3] Opening web application in your default browser...
start "" "http://127.0.0.1:8000/"

echo.
echo ===================================================================
echo  JobTrack is running at: http://127.0.0.1:8000/
echo  Demo Credentials:
echo    Username: demo
echo    Password: demo1234
echo.
echo  Press Ctrl+C in this terminal window to stop the server.
echo ===================================================================
echo.

:: 5. Start the development server
python manage.py runserver 127.0.0.1:8000
