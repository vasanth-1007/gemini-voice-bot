#!/bin/bash
# Start Gemini Live Voice Bot Server

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║    🎙️ Starting Gemini Live Voice Bot Server 🎙️            ║"
echo "║         Real-time Voice Communication Enabled                ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install Live API dependencies
echo "📥 Installing Live API dependencies..."
pip install -q google-genai websockets

# Get external IP
EXTERNAL_IP=$(curl -s ifconfig.me || curl -s icanhazip.com || echo "Unable to detect")

echo ""
echo "✅ Setup complete!"
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    SERVER INFORMATION                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 External IP: $EXTERNAL_IP"
echo "🔌 Port: 5000"
echo ""
echo "📱 Access URLs:"
echo "   • Local:    http://localhost:5000"
echo "   • Network:  http://$(hostname -I | awk '{print $1}'):5000"
echo "   • External: http://$EXTERNAL_IP:5000"
echo ""
echo "🎙️  Features:"
echo "   • Real-time voice streaming"
echo "   • Bidirectional audio"
echo "   • Natural conversations"
echo "   • Tanglish responses"
echo "   • Audio visualization"
echo ""
echo "🛡️  Security Note:"
echo "   • Port 5000 must be open in firewall"
echo "   • Use HTTPS in production"
echo "   • Add authentication for public access"
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              STARTING LIVE API SERVER...                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Start the Live API server
python web_live_api.py
