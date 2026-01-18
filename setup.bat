@echo off
echo ========================================
echo Job Optimizer - 4 Day Progress Demo
echo Quick Setup Script
echo ========================================
echo.

echo [1/3] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/3] Activating environment and installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall --no-cache-dir
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [3/3] Checking .env file...
if not exist ".env" (
    echo WARNING: .env file not found
    echo Please copy .env.template to .env and add your GROQ_API_KEY
    copy .env.template .env
)

echo.
echo ========================================
echo ✅ Setup Complete!
echo ========================================
echo.
echo To run the demo:
echo 1. Run: venv\Scripts\activate
echo 2. Run: streamlit run ui\app.py
echo.
pause
