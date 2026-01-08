#!/bin/bash
# Start Gemini Voice Bot Web Server

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║       🚀 Starting Gemini Voice Bot Web Server 🚀            ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install web dependencies if needed
echo "📥 Installing web dependencies..."
pip install -q Flask Flask-CORS Flask-SocketIO gunicorn eventlet

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
echo "🛡️  Security Note:"
echo "   Make sure port 5000 is open in your firewall"
echo "   For production, use HTTPS and authentication"
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  STARTING SERVER...                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Start the web server
python web_app.py
