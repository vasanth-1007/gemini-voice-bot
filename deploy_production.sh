#!/bin/bash
# Production Deployment Script for Gemini Voice Bot Web Server

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        🚀 Gemini Voice Bot - Production Deployment 🚀       ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root (not recommended)
if [ "$EUID" -eq 0 ]; then 
    echo "⚠️  Warning: Running as root. Consider using a non-root user."
    echo ""
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install production dependencies
echo "📥 Installing production dependencies..."
pip install -q -r requirements.txt
pip install -q -r requirements_web.txt

# Get system information
EXTERNAL_IP=$(curl -s ifconfig.me || curl -s icanhazip.com || echo "Unable to detect")
INTERNAL_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    DEPLOYMENT INFORMATION                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 External IP: $EXTERNAL_IP"
echo "🏠 Internal IP: $INTERNAL_IP"
echo "🔌 Port: 5000"
echo ""

# Check if port 5000 is open
echo "🔍 Checking port 5000..."
if command -v netstat &> /dev/null; then
    if netstat -tuln | grep -q ":5000 "; then
        echo "⚠️  Port 5000 is already in use"
        echo "   Run: sudo lsof -i :5000 to see what's using it"
    else
        echo "✅ Port 5000 is available"
    fi
fi

# Firewall configuration instructions
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  FIREWALL CONFIGURATION                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "To allow external access, open port 5000:"
echo ""
echo "For UFW (Ubuntu):"
echo "  sudo ufw allow 5000/tcp"
echo "  sudo ufw reload"
echo ""
echo "For firewalld (CentOS/RHEL):"
echo "  sudo firewall-cmd --permanent --add-port=5000/tcp"
echo "  sudo firewall-cmd --reload"
echo ""
echo "For GCP/AWS/Azure:"
echo "  Add firewall rule in cloud console to allow TCP:5000"
echo ""

# Ask if user wants to configure firewall now
read -p "Configure firewall now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v ufw &> /dev/null; then
        echo "Configuring UFW..."
        sudo ufw allow 5000/tcp
        sudo ufw reload
        echo "✅ Firewall configured"
    elif command -v firewall-cmd &> /dev/null; then
        echo "Configuring firewalld..."
        sudo firewall-cmd --permanent --add-port=5000/tcp
        sudo firewall-cmd --reload
        echo "✅ Firewall configured"
    else
        echo "⚠️  Firewall tool not detected. Configure manually."
    fi
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    ACCESS INFORMATION                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📱 Access your bot at:"
echo ""
echo "   Local Network:"
echo "   http://$INTERNAL_IP:5000"
echo ""
echo "   External/Public:"
echo "   http://$EXTERNAL_IP:5000"
echo ""
echo "   From anywhere:"
echo "   http://$(hostname):5000"
echo ""

# Ask deployment mode
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    DEPLOYMENT MODE                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Choose deployment mode:"
echo "  1) Development (Flask built-in server)"
echo "  2) Production (Gunicorn with multiple workers)"
echo "  3) Background (Run as daemon with nohup)"
echo ""
read -p "Enter choice (1-3): " mode

case $mode in
    1)
        echo ""
        echo "🚀 Starting in Development Mode..."
        echo "   Press Ctrl+C to stop"
        echo ""
        python web_app.py
        ;;
    2)
        echo ""
        echo "🚀 Starting in Production Mode with Gunicorn..."
        echo "   Using 4 workers"
        echo "   Press Ctrl+C to stop"
        echo ""
        gunicorn --worker-class eventlet -w 4 -b 0.0.0.0:5000 web_app:app
        ;;
    3)
        echo ""
        echo "🚀 Starting in Background Mode..."
        nohup python web_app.py > web_server.log 2>&1 &
        PID=$!
        echo "✅ Server started with PID: $PID"
        echo "   Logs: tail -f web_server.log"
        echo "   Stop: kill $PID"
        echo ""
        echo "Server is now running in background!"
        echo "Access at: http://$EXTERNAL_IP:5000"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
