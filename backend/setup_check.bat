@echo off
REM Quick Setup Verification Script for Windows
REM Run this after completing the GCP setup steps

echo ============================================================
echo   GCP Setup Quick Check
echo ============================================================
echo.

REM Check if key.json exists
if exist "key.json" (
    echo [OK] key.json file found
) else (
    echo [ERROR] key.json NOT found
    echo Please download your service account key and save it as key.json
    echo.
    pause
    exit /b 1
)

REM Check if .env exists
if exist ".env" (
    echo [OK] .env file found
) else (
    echo [WARNING] .env file not found
    echo You can create it from .env.example
    echo Or use system environment variables instead
)

echo.
echo Checking Python installation...
py --version >nul 2>&1
if %errorlevel% equ 0 (
    py --version
    echo [OK] Python is installed
) else (
    echo [ERROR] Python not found
    echo Please install Python 3.11 or higher
    pause
    exit /b 1
)

echo.
echo Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    node --version
    echo [OK] Node.js is installed
) else (
    echo [ERROR] Node.js not found
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Installing Dependencies
echo ============================================================
echo.

echo Installing Python packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)

echo.
echo Installing Node.js packages...
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Node.js dependencies
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Running Setup Verification
echo ============================================================
echo.

py verify_setup.py

echo.
echo ============================================================
echo Setup check complete!
echo.
echo Next steps:
echo 1. Make sure all environment variables are set
echo 2. Run: python app.py
echo 3. Test the API at http://localhost:5000
echo.
echo For detailed instructions, see GCP_MIGRATION_GUIDE.md
echo ============================================================
pause
