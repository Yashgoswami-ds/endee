@echo off
REM Setup script for AI Knowledge Assistant

echo.
echo ================================
echo AI Knowledge Assistant Setup
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

REM Create virtual environment if not exists
if not exist "venv\" (
    echo [1] Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo [2] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [3] Installing dependencies from requirements.txt...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

REM Create .env file if not exists
if not exist ".env" (
    echo [4] Creating .env configuration file...
    (
        echo ENDEE_BASE_URL=https://api.endee.ai/v1
        echo ENDEE_API_KEY=your_api_key_here
        echo FLASK_ENV=development
        echo FLASK_DEBUG=False
    ) > .env
    echo [!] .env created - UPDATE with your Endee API key
)

REM Create data directories
if not exist "data\uploads" (
    echo [5] Creating data directories...
    mkdir data\uploads
)

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo Next steps:
echo 1. Edit .env file and add your Endee API key
echo 2. Run: python app.py
echo 3. Open http://127.0.0.1:5000 in your browser
echo.
pause
