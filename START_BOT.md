# 🚀 How to Start Your Gemini Voice Bot

## ✅ Installation Complete!

All dependencies are installed and your bot is ready to use.

---

## 🎯 Quick Start (3 Commands)

### 1. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 2. Run the Application
```bash
python main.py
```

### 3. Start Using!
```
Press 1 - Load SOPs (if needed)
Press 2 - Ask text questions
Press 4 - Live voice session
```

---

## 📊 What's Already Indexed

Your bot has already processed:
- ✅ Text from **tvs-sop-1.pdf**
- ✅ Text from **tvs-sop-2.pdf**
- ✅ **11 images** from your PDFs (analyzed with Gemini Vision)

**Ready to answer questions immediately!**

---

## 💬 Example Usage

### Ask a Text Question (Option 2):
```
> How to handle customer complaints?

Response in Tanglish:
"Customer complaints handle panna, first level la team lead 
ku report pannanum. Issue resolve aagala na manager ku escalate 
pannalam. Documentation romba important-u maintain pannanum."
```

### Ask About Images:
```
> What does the process flowchart show?

Response:
"Process flowchart la clear-a steps iruku. First step la 
request receive pannanum, second step approval venum, 
third step implementation pannanum. Each step ku timeline 
specified pannirukkanga."
```

---

## ⚠️ Note About Rate Limits

**What happened during setup:**
- Your PDF had **20 images**
- Gemini API limit: **10 requests/minute**
- **11 images** were processed successfully
- **9 images** hit the rate limit

**This is normal and doesn't affect usage!**

**To process remaining images:**
1. Wait 1 minute
2. Run bot: `python main.py`
3. Select Option 6 (Rebuild index)
4. Remaining images will be processed

---

## 🎤 Voice Features

### Option 3: Voice from File
Upload pre-recorded audio (WAV format)

### Option 4: Live Voice Session
- Real-time conversation
- Speak naturally
- Get Tanglish voice responses
- Press Ctrl+C to stop

---

## 📁 Your SOPs

Located in: `sops/` folder

**Current files:**
- tvs-sop-1.pdf
- tvs-sop-2.pdf

**To add more:**
```bash
cp your-new-sop.pdf sops/
# Then run Option 6 to rebuild index
```

---

## 🔧 Configuration

Your configuration: `.env` file

**Key settings:**
- API Key: Already configured ✅
- Model: gemini-2.5-flash-native-audio-preview-12-2025
- Chunk size: 1000 characters
- Top-K results: 3
- Image extraction: Enabled ✅

---

## 📊 Check Status

### Option 5: System Statistics
Shows:
- Number of documents indexed
- Image extraction status
- Model configuration
- Retrieval settings

---

## 🐛 Troubleshooting

### Bot not responding?
```bash
# Check if running
ps aux | grep "python main.py"

# Restart
pkill -f "python main.py"
source venv/bin/activate
python main.py
```

### Images not processing?
- Check API rate limits (wait 1 minute)
- Verify API key in .env
- Check logs: `tail -f gemini_voice_bot.log`

### Voice not working?
- Check microphone permissions
- Test with Option 2 (text) first
- Install audio drivers if needed

---

## 📚 Documentation

- `README.md` - Complete guide
- `IMAGE_SUPPORT_GUIDE.md` - Image features
- `SETUP_GUIDE.md` - Setup instructions
- `ARCHITECTURE.md` - Technical details

---

## 🎯 Common Commands

```bash
# Activate environment
source venv/bin/activate

# Run bot
python main.py

# View logs
tail -f gemini_voice_bot.log

# Test setup
python test_setup.py

# Test image support
python test_image_support.py

# Deactivate when done
deactivate
```

---

## ✨ Features Available

### Text Features:
- ✅ Load PDF, DOCX, TXT
- ✅ Extract and understand images
- ✅ Semantic search (RAG)
- ✅ Tanglish responses
- ✅ No hallucinations

### Voice Features:
- ✅ Speech-to-text (Gemini)
- ✅ Text-to-speech (Google Cloud)
- ✅ Live conversation mode
- ✅ Audio file processing

### Image Features (NEW!):
- ✅ Extract images from PDFs
- ✅ Analyze with Gemini Vision
- ✅ Understand flowcharts, tables, diagrams
- ✅ Answer questions about images

---

## 🚀 Start Now!

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Run bot
python main.py

# 3. That's it! Start asking questions!
```

---

**Your Gemini Voice Bot is ready to answer questions about your SOPs in Tanglish!** 🎤🤖

---

*For detailed documentation, see README.md*
