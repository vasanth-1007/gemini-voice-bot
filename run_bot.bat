@echo off
REM Quick start script for Gemini Voice Bot (Windows)

echo 🤖 Gemini Voice Bot - Quick Start
echo =================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies if needed
python -c "import google.generativeai" 2>nul
if errorlevel 1 (
    echo 📥 Installing dependencies...
    pip install -r requirements.txt
    echo ✓ Dependencies installed
)

REM Check setup
echo.
echo 🔍 Verifying setup...
python test_setup.py

REM Run bot if setup is successful
if %errorlevel% equ 0 (
    echo.
    echo 🚀 Starting Gemini Voice Bot...
    echo.
    python main.py
) else (
    echo.
    echo ⚠️  Please fix setup issues before running the bot
    echo 💡 Tip: Make sure to add your API key to .env file
    pause
)
