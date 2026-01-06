# 🌐 Web Interface Guide - Gemini Voice Bot

## Overview

You now have a complete **web-based interface** for your Gemini Voice Bot, accessible from any device via your VM's external IP!

---

## 🎯 What You Have

### ✅ Features:
- **Modern Web UI** - Beautiful, responsive design
- **Real-time Chat** - Ask questions and get Tanglish responses
- **Audio Upload** - Upload WAV files for voice queries
- **Statistics Dashboard** - View system stats
- **SOP Management** - Load and rebuild document index
- **Example Questions** - Quick-start templates
- **External Access** - Available from anywhere via external IP

### 📁 Files Created:

**Backend:**
- `web_app.py` - Flask application server
- `requirements_web.txt` - Web dependencies

**Frontend:**
- `templates/index.html` - Main web interface
- `static/css/style.css` - Modern dark theme styling
- `static/js/app.js` - Interactive JavaScript

**Deployment:**
- `start_web_server.sh` - Quick start script
- `deploy_production.sh` - Production deployment script

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Web Dependencies

```bash
source venv/bin/activate
pip install Flask Flask-CORS Flask-SocketIO gunicorn eventlet
```

### Step 2: Start the Server

```bash
./start_web_server.sh
```

### Step 3: Access in Browser

```
http://YOUR_EXTERNAL_IP:5000
```

---

## 🌍 Finding Your External IP

### Method 1: Using the Start Script
The script automatically shows your external IP when you run it.

### Method 2: Manual Check
```bash
curl ifconfig.me
# or
curl icanhazip.com
```

### Method 3: GCP/AWS/Azure Console
Check your VM instance details in the cloud console.

---

## 🔧 Deployment Options

### Option 1: Quick Development Start

```bash
./start_web_server.sh
```

**Use for:**
- Testing
- Development
- Local network only

### Option 2: Production Deployment

```bash
./deploy_production.sh
```

**Features:**
- Multiple deployment modes
- Firewall configuration
- Gunicorn with workers
- Background daemon mode

**Choose from:**
1. **Development Mode** - Flask built-in server
2. **Production Mode** - Gunicorn with 4 workers
3. **Background Mode** - Runs as daemon

---

## 🔐 Firewall Configuration

### Open Port 5000 for External Access

**Ubuntu/Debian (UFW):**
```bash
sudo ufw allow 5000/tcp
sudo ufw reload
```

**CentOS/RHEL (firewalld):**
```bash
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

**GCP:**
```bash
gcloud compute firewall-rules create allow-gemini-bot \
    --allow tcp:5000 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow Gemini Voice Bot web access"
```

**AWS:**
1. Go to EC2 → Security Groups
2. Edit inbound rules
3. Add rule: Type=Custom TCP, Port=5000, Source=0.0.0.0/0

**Azure:**
1. Go to Virtual Machine → Networking
2. Add inbound port rule
3. Port=5000, Protocol=TCP, Source=Any

---

## 📱 Access URLs

Once running, access from:

### Local Machine:
```
http://localhost:5000
```

### Same Network:
```
http://YOUR_INTERNAL_IP:5000
```

### External/Public:
```
http://YOUR_EXTERNAL_IP:5000
```

**Example:**
```
http://34.123.45.67:5000
```

---

## 🎨 Web Interface Features

### 1. Dashboard
- **Document Count** - Number of indexed chunks
- **Image Support Status** - Enabled/Disabled
- **AI Model** - Current Gemini model

### 2. Actions
- **Load SOPs** - Index documents from sops/ folder
- **Rebuild Index** - Force rebuild of all indices
- **Refresh Stats** - Update dashboard statistics

### 3. Chat Interface
- **Text Input** - Type questions directly
- **Audio Upload** - Upload WAV files for voice queries
- **Real-time Responses** - Instant answers in Tanglish
- **Chat History** - View conversation history

### 4. Example Questions
Quick-start templates:
- Leave request process
- Expense reimbursement
- IT support contacts
- Escalation flowcharts
- Remote work policy
- Password reset

---

## 💬 Using the Chat Interface

### Text Questions:

1. Type your question in the input box
2. Click "Send" or press Enter
3. Get Tanglish response instantly

**Example:**
```
You: How do I submit leave request?

Bot: Leave request submit panna, HR portal ku ponga. 
     Form fill pannunga. Manager approval venumnu 
     remember pannunga. 2 weeks advance la submit pannanum.
```

### Voice Questions:

1. Click "Upload Audio (WAV)"
2. Select your WAV file
3. System transcribes and responds

**Format:** WAV, 16kHz recommended

---

## 🛡️ Security Considerations

### ⚠️ Important Notes:

**This is a basic setup. For production:**

1. **Add Authentication**
   - Username/password login
   - OAuth integration
   - API key authentication

2. **Use HTTPS**
   - Get SSL certificate (Let's Encrypt)
   - Configure reverse proxy (Nginx)
   - Force HTTPS redirect

3. **Restrict Access**
   - Firewall rules for specific IPs
   - VPN requirement
   - Private network only

4. **Rate Limiting**
   - Prevent API abuse
   - Limit requests per IP
   - Add CAPTCHA for public access

### Quick Security Setup:

**Add Basic Auth (Simple):**

Edit `web_app.py` and add:

```python
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash

auth = HTTPBasicAuth()

users = {
    "admin": "pbkdf2:sha256:your_hashed_password"
}

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

# Then add @auth.login_required to routes
```

---

## 🚀 Production Deployment

### Recommended Setup:

```
Internet
    ↓
Nginx (HTTPS, Port 443)
    ↓
Gunicorn (Port 5000)
    ↓
Flask App
    ↓
Voice Assistant
```

### Nginx Configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Run with Gunicorn:

```bash
gunicorn --worker-class eventlet \
         -w 4 \
         -b 0.0.0.0:5000 \
         --access-logfile access.log \
         --error-logfile error.log \
         web_app:app
```

### Systemd Service:

Create `/etc/systemd/system/gemini-bot.service`:

```ini
[Unit]
Description=Gemini Voice Bot Web Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/gemini-voice-bot
Environment="PATH=/path/to/gemini-voice-bot/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn --worker-class eventlet -w 4 -b 0.0.0.0:5000 web_app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable gemini-bot
sudo systemctl start gemini-bot
sudo systemctl status gemini-bot
```

---

## 📊 Monitoring

### Check Server Status:

```bash
# View logs
tail -f web_app.log

# Check if running
ps aux | grep web_app

# Check port
netstat -tuln | grep 5000

# View access logs (if using gunicorn)
tail -f access.log
```

### Health Check Endpoint:

```bash
curl http://localhost:5000/health
```

---

## 🐛 Troubleshooting

### Issue: Can't access from external IP

**Solutions:**
1. Check firewall: `sudo ufw status`
2. Verify port is open: `netstat -tuln | grep 5000`
3. Check cloud firewall rules (GCP/AWS/Azure)
4. Confirm server is listening on 0.0.0.0, not 127.0.0.1

### Issue: Port 5000 already in use

**Solution:**
```bash
# Find what's using it
sudo lsof -i :5000

# Kill the process
kill <PID>

# Or use different port
export PORT=8080
python web_app.py
```

### Issue: Server crashes or errors

**Check logs:**
```bash
tail -f web_app.log
tail -f gemini_voice_bot.log
```

**Restart server:**
```bash
pkill -f web_app
./start_web_server.sh
```

### Issue: Slow responses

**Causes:**
- Large PDFs with many images
- API rate limits
- Network latency

**Solutions:**
- Process SOPs in advance (Option 1)
- Use production mode with workers
- Add caching layer

---

## 📈 Performance Tips

1. **Pre-index SOPs**
   - Load documents before sharing URL
   - Faster first-time responses

2. **Use Production Mode**
   - Gunicorn with multiple workers
   - Better concurrent request handling

3. **Add Caching**
   - Cache common queries
   - Reduce API calls

4. **Optimize Images**
   - Process images during low traffic
   - Limit image count if needed

---

## 🎯 Usage Examples

### Example 1: Team Access

```
Share with team:
http://your-vm-ip:5000

Team members can:
- Ask questions about SOPs
- Get instant Tanglish responses
- Upload voice queries
- View system stats
```

### Example 2: Customer Support

```
Deploy publicly:
https://sop-bot.your-domain.com

Features for support team:
- Quick SOP lookups
- Consistent Tanglish responses
- No training needed
- 24/7 availability
```

### Example 3: Mobile Access

```
Access from phone:
http://your-vm-ip:5000

Responsive design works on:
- Smartphones
- Tablets
- Desktops
- Any modern browser
```

---

## 🌟 Next Steps

### 1. **Test Locally First**
```bash
./start_web_server.sh
# Access: http://localhost:5000
```

### 2. **Configure Firewall**
```bash
sudo ufw allow 5000/tcp
```

### 3. **Access Externally**
```
http://YOUR_EXTERNAL_IP:5000
```

### 4. **Add Security** (Recommended)
- Set up authentication
- Use HTTPS
- Restrict IP access

### 5. **Monitor & Maintain**
- Check logs regularly
- Update dependencies
- Backup vector database

---

## ✅ Summary

You now have:

✓ **Complete web interface** for voice bot  
✓ **External IP access** from anywhere  
✓ **Modern, responsive UI** with dark theme  
✓ **Real-time chat** with Tanglish responses  
✓ **Audio upload** capability  
✓ **Production-ready** deployment scripts  
✓ **Security guidelines** for public access  

**Start now:**
```bash
./start_web_server.sh
```

**Then access:**
```
http://YOUR_EXTERNAL_IP:5000
```

---

## 📞 Support

**Documentation:**
- `WEB_INTERFACE_GUIDE.md` - This file
- `README.md` - Main documentation
- `ARCHITECTURE.md` - Technical details

**Logs:**
- `web_app.log` - Web server logs
- `gemini_voice_bot.log` - Bot logs

**Scripts:**
- `start_web_server.sh` - Quick start
- `deploy_production.sh` - Production deployment

---

**Your Gemini Voice Bot is now accessible via web from anywhere! 🌐🎤🤖**
