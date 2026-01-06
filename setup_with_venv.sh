#!/bin/bash
echo "🚀 Setting up Gemini Voice Bot with Virtual Environment"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install PyMuPDF Pillow

echo ""
echo "✅ Installation complete!"
echo ""
echo "To use the bot:"
echo "  1. source venv/bin/activate"
echo "  2. python main.py"
echo ""
echo "Or simply run: ./run_bot.sh"
