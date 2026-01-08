# 🚀 Quick Setup Guide - Gemini Voice Bot

This guide will help you set up and run the Gemini Voice Bot in under 10 minutes.

## ⚡ Quick Start (5 Steps)

### Step 1: Get Your API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key

### Step 2: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### Step 3: Configure API Key

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file and add your API key
# Replace 'your_gemini_api_key_here' with your actual key
```

Your `.env` should look like:
```env
GOOGLE_API_KEY=AIzaSyC_your_actual_key_here
```

### Step 4: Add SOP Documents

```bash
# The sops/ folder is already created
# Add your documents (PDF, DOCX, or TXT)
cp /path/to/your/handbook.pdf sops/
cp /path/to/your/procedures.docx sops/
```

### Step 5: Run the Bot

```bash
python main.py
```

On first run:
1. Select option `1` to load and index your SOPs
2. Then select option `2` to ask a test question
3. Try option `4` for live voice interaction!

## 📋 Sample SOP Documents

Don't have SOPs yet? Create a test file:

```bash
cat > sops/sample_sop.txt << 'EOF'
COMPANY LEAVE POLICY

Annual Leave:
Employees are entitled to 15 days of paid annual leave per year.
Leave requests must be submitted 2 weeks in advance through the HR portal.

Sick Leave:
Employees can take up to 10 days of sick leave per year.
Medical certificate required for absences longer than 3 days.

Contact Information:
HR Support: hr@company.com
Phone: +1-555-0123
EOF
```

Now you can test with questions like:
- "How many days of annual leave do I get?"
- "How do I apply for sick leave?"

## 🎤 Testing Voice Features

### Option A: Text-Only Testing (No Microphone Needed)

Use **Option 2** in the menu - perfect for testing without audio hardware.

### Option B: Record Audio File

If you have a microphone, record a test question:

**On Linux:**
```bash
arecord -d 5 -f cd test_question.wav
# Speak your question for 5 seconds
```

**On macOS:**
```bash
rec -r 16000 -c 1 test_question.wav trim 0 5
# Speak your question for 5 seconds
```

**On Windows:**
Use Voice Recorder app or any audio recording tool, save as WAV.

Then use **Option 3** in the menu to process the audio file.

### Option C: Live Voice (Requires Microphone)

Use **Option 4** for real-time conversation. The system will:
1. Record your voice (5 seconds)
2. Transcribe it
3. Find relevant SOP information
4. Respond in Tanglish

## 🔧 Common Installation Issues

### Issue: pip install fails

**Solution:**
```bash
# Upgrade pip first
pip install --upgrade pip

# Try installing again
pip install -r requirements.txt
```

### Issue: sounddevice installation fails

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio sounddevice
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio sounddevice
```

**Windows:**
```bash
# Download PyAudio wheel from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
pip install PyAudio-0.2.11-cp39-cp39-win_amd64.whl
pip install sounddevice
```

### Issue: ChromaDB errors

**Solution:**
```bash
# Upgrade ChromaDB
pip install --upgrade chromadb

# If still issues, try:
pip install chromadb --no-cache-dir
```

## ✅ Verification Checklist

Before asking questions, verify:

- [ ] API key is set in `.env` file
- [ ] SOP documents are in `sops/` folder
- [ ] Option 1 (Load SOPs) completed successfully
- [ ] System shows document count > 0

Check with **Option 5** (System Statistics) to verify everything is working.

## 🎯 Example Usage Flow

### First Time Setup:

```bash
# 1. Run the application
python main.py

# 2. In the menu, type: 1 (Load SOPs)
✓ Indexed 47 document chunks

# 3. Test with text question, type: 2
Ask your question:
> How do I submit leave request?

Response:
Leave request submit panna, HR portal la ponga. "Leave Request" form fill pannunga. 
Minimum 2 weeks advance la submit pannanum.

# 4. Try voice (if you have microphone), type: 4
Starting live voice session...
Recording... (speak now)
[Speak: "What is the sick leave policy?"]
Response spoken in Tanglish!
```

## 🎨 Tanglish Response Examples

The bot will respond naturally mixing Tamil and English:

**Question:** "How many vacation days?"
**Response:** "Annual leave 15 days kudukuranga per year. Advance la 2 weeks munnadiye apply pannanum."

**Question:** "Who handles IT issues?"
**Response:** "IT support ku help@company.com ku email pannunga or extension 4567 ku call pannunga."

**Question:** "Process for reimbursement?"
**Response:** "Expense reimbursement process la first receipt upload pannanum. Then manager approval varum. 2 weeks la amount credit aagum."

## 🔄 Updating SOPs

When you add or update SOP documents:

```bash
# 1. Add new documents to sops/ folder
cp new_policy.pdf sops/

# 2. Run the application
python main.py

# 3. Select option: 6 (Rebuild index)
# This will re-index all documents including new ones
```

## 📊 System Requirements

**Minimum:**
- Python 3.8+
- 4 GB RAM
- 1 GB free disk space
- Internet connection (for Gemini API)

**Recommended:**
- Python 3.10+
- 8 GB RAM
- 2 GB free disk space
- Stable internet connection
- Microphone for voice features

## 🆘 Getting Help

If you encounter issues:

1. **Check logs:**
   ```bash
   tail -f gemini_voice_bot.log
   ```

2. **View statistics (Option 5):**
   Verify configuration and document count

3. **Rebuild index (Option 6):**
   Sometimes fixes indexing issues

4. **Clear and restart:**
   ```bash
   rm -rf chroma_db/
   python main.py
   # Then run option 1 again
   ```

## 🎓 Learning Path

**Beginner:** Start with text questions (Option 2)
↓
**Intermediate:** Try voice files (Option 3)
↓
**Advanced:** Live voice sessions (Option 4)
↓
**Expert:** Customize code for your needs

## 🚀 Next Steps

Once setup is complete:

1. ✅ Test with your actual SOP documents
2. ✅ Try various question types
3. ✅ Experiment with voice features
4. ✅ Monitor logs for improvements
5. ✅ Customize configuration for your needs

---

**Ready to start? Run:** `python main.py`

**Need help?** Check the main README.md for detailed documentation.
