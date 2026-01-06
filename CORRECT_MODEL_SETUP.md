# ✅ Correct Model Configuration

## Your Model Setup

Your Gemini Voice Bot uses **different specialized models** for different tasks:

---

## 🎯 Model Assignment

### **1. Live Voice (Real-time Audio):**
```
Model: gemini-2.5-flash-native-audio-preview-12-2025
Purpose: Live API voice conversations
Features: Native audio support, fast streaming
Use case: Real-time voice chat with users
```

### **2. SOP Processing (Document Analysis):**
```
Model: gemini-3-pro-preview
Purpose: Document processing, image extraction
Features: Advanced multimodal, image understanding
Use case: Extracting content from image-heavy SOPs
```

### **3. Question Answering (Text Responses):**
```
Model: Uses same as Live Voice
Purpose: Text-based Q&A, Tanglish responses
Use case: Regular chat interface
```

---

## ⚙️ Configuration File

### **Your `.env` File:**

```env
# API Key (same for all models)
GOOGLE_API_KEY=AIzaSyDK9dk2091Kolr0UALNLWjGRwZ6XsC9-p4

# Live voice model (for real-time audio)
GEMINI_MODEL=gemini-2.5-flash-native-audio-preview-12-2025

# SOP processing model (for document analysis and image extraction)
GEMINI_PROCESSING_MODEL=gemini-3-pro-preview

# Embedding model
EMBEDDING_MODEL=models/embedding-001
```

---

## 🔄 Where Each Model is Used

### **`gemini-2.5-flash-native-audio-preview-12-2025`:**
Used in:
- ✅ `web_live_api.py` - Live voice sessions
- ✅ `src/gemini_live/live_session.py` - Real-time streaming
- ✅ `src/gemini_integration/gemini_client.py` - Text responses
- ✅ Voice interactions in CLI

### **`gemini-3-pro-preview`:**
Used in:
- ✅ `src/sop_loader/gemini_processor.py` - SOP processing
- ✅ Document upload and analysis
- ✅ Image extraction and understanding
- ✅ Creating summaries and key points

---

## 📊 How It Works

### **When You Load SOPs:**
```
1. Upload PDF to Gemini API
2. Use gemini-3-pro-preview ✓
3. Extract text + images
4. Create summaries
5. Store in vector DB
```

### **When User Asks Question (Text):**
```
1. Search vector DB
2. Get relevant context
3. Use gemini-2.5-flash-native-audio-preview ✓
4. Generate Tanglish response
5. Return to user
```

### **When User Uses Live Voice:**
```
1. Stream audio to server
2. Use gemini-2.5-flash-native-audio-preview ✓
3. Real-time processing
4. Stream audio response back
5. User hears voice
```

---

## ✅ Verification

### **Check Your Configuration:**

```bash
# View current models
cat .env | grep GEMINI

# Should show:
# GEMINI_MODEL=gemini-2.5-flash-native-audio-preview-12-2025
# GEMINI_PROCESSING_MODEL=gemini-3-pro-preview
```

### **Verify in Logs:**

When you start the bot, you should see:

```
INFO - Using Gemini model for processing: gemini-3-pro-preview
INFO - API key configured: Yes
```

---

## 🚀 Usage

### **Everything Works Automatically:**

```bash
# Process SOPs (uses gemini-3-pro-preview)
python main.py
> Option 1: Load and index SOP documents

# Ask questions (uses gemini-2.5-flash-native-audio-preview)
python main.py
> Option 2: Ask a text question

# Live voice (uses gemini-2.5-flash-native-audio-preview)
python web_live_api.py
# Then use web interface
```

---

## 🎯 Why Different Models?

### **Live Voice Model:**
- **Native audio support** - Built for streaming audio
- **Low latency** - Fast real-time responses
- **Optimized for voice** - Better voice quality

### **Processing Model:**
- **Advanced multimodal** - Better image understanding
- **Higher quality** - More accurate extraction
- **Complex analysis** - Handles image-heavy documents

### **Result:**
Best of both worlds! ✨
- Superior SOP processing
- Excellent live voice quality

---

## 🔧 Configuration Code

### **In `config.py`:**

```python
class Config(BaseModel):
    # Live voice and responses
    gemini_model: str = "gemini-2.5-flash-native-audio-preview-12-2025"
    
    # SOP processing
    gemini_processing_model: str = "gemini-3-pro-preview"
```

### **In `src/voice_assistant.py`:**

```python
# For SOP processing
self.gemini_processor = GeminiSOPProcessor(
    api_key=api_key,
    model_name=config.gemini_processing_model  # gemini-3-pro-preview
)

# For responses
self.gemini_client = GeminiClient(
    api_key=api_key,
    model_name=config.gemini_model  # gemini-2.5-flash-native-audio
)
```

---

## ✨ Summary

### **Your Setup:**

✅ **Live Voice:** `gemini-2.5-flash-native-audio-preview-12-2025`
- Real-time voice conversations
- Fast streaming
- Native audio support

✅ **SOP Processing:** `gemini-3-pro-preview`
- Document analysis
- Image extraction
- Advanced understanding

✅ **Same API Key:** Works for both models

✅ **Automatic:** System uses correct model for each task

---

## 🎯 Ready to Use

Your configuration is now correct!

```bash
# Process SOPs with gemini-3-pro-preview
python main.py
> Option 1

# Use live voice with gemini-2.5-flash-native-audio
python web_live_api.py
```

**Each model is used for its specialized purpose!** 🚀

---

**Do NOT change these model names - they are correct for your use case!** ✅
