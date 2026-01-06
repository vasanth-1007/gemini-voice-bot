#!/bin/bash
# Quick start script for Gemini Voice Bot

echo "🤖 Gemini Voice Bot - Quick Start"
echo "================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if ! python -c "import google.generativeai" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    echo "✓ Dependencies installed"
fi

# Check setup
echo ""
echo "🔍 Verifying setup..."
python test_setup.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 Starting Gemini Voice Bot..."
    echo ""
    python main.py
else
    echo ""
    echo "⚠️  Please fix setup issues before running the bot"
    echo "💡 Tip: Make sure to add your API key to .env file"
fi
