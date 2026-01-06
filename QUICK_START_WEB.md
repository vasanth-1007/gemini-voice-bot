# 🚀 Quick Start - Web Interface

## 3-Step Setup

### Step 1: Install Web Dependencies (30 seconds)

```bash
source venv/bin/activate
pip install Flask Flask-CORS Flask-SocketIO gunicorn eventlet
```

### Step 2: Start the Server (10 seconds)

```bash
./start_web_server.sh
```

### Step 3: Access in Browser (Now!)

```
http://YOUR_EXTERNAL_IP:5000
```

Get your IP: `curl ifconfig.me`

---

## 🔥 Firewall Setup (If Needed)

**Ubuntu/Debian:**
```bash
sudo ufw allow 5000/tcp
sudo ufw reload
```

**GCP:**
```bash
gcloud compute firewall-rules create allow-gemini-bot \
    --allow tcp:5000 --source-ranges 0.0.0.0/0
```

---

## 📱 Access URLs

- **Local:** http://localhost:5000
- **Network:** http://INTERNAL_IP:5000
- **External:** http://EXTERNAL_IP:5000

---

## 🎯 What You Can Do

1. **Ask Questions** - Type in chat interface
2. **Upload Audio** - WAV files for voice queries
3. **View Stats** - See indexed documents
4. **Manage SOPs** - Load and rebuild index
5. **Example Questions** - Quick-start templates

---

## 🌟 Features

✓ Real-time chat interface  
✓ Tanglish responses  
✓ Audio file upload  
✓ Image-heavy SOP support  
✓ Statistics dashboard  
✓ Mobile responsive  

---

## 🐛 Troubleshooting

**Can't access externally?**
- Check firewall: `sudo ufw status`
- Verify cloud firewall rules
- Confirm port 5000 is open

**Port already in use?**
```bash
sudo lsof -i :5000
kill <PID>
```

**View logs:**
```bash
tail -f web_app.log
```

---

## 📚 Full Documentation

See `WEB_INTERFACE_GUIDE.md` for:
- Complete feature list
- Production deployment
- Security configuration
- Advanced settings

---

**Start now:** `./start_web_server.sh`
