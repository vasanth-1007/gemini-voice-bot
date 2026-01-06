# 🤖 Model Configuration Guide

## Current Model Setup

Your Gemini Voice Bot uses the **latest Gemini 2.0 models** from Google.

---

## 📋 Available Gemini Models

### **Gemini 2.0 Flash (Latest):**
- **Model:** `gemini-2.0-flash-exp`
- **Features:** Fast, efficient, multimodal
- **Best for:** Production use, SOP processing
- **Supports:** Text, images, audio, video
- **Cost:** Lower than Pro models

### **Gemini 1.5 Pro:**
- **Model:** `gemini-1.5-pro-latest`
- **Features:** High quality, large context
- **Best for:** Complex analysis
- **Context:** 2M tokens
- **Cost:** Higher

### **Gemini 1.5 Flash:**
- **Model:** `gemini-1.5-flash-latest`
- **Features:** Fast, good quality
- **Best for:** Quick responses
- **Cost:** Low

---

## ⚙️ Your Current Configuration

### **File:** `.env`

```env
# API Key (from your .env file)
GOOGLE_API_KEY=your_actual_key_here

# Model for responses and generation
GEMINI_MODEL=gemini-2.0-flash-exp

# Model specifically for SOP processing
GEMINI_PROCESSING_MODEL=gemini-2.0-flash-exp

# Embedding model for RAG
EMBEDDING_MODEL=models/embedding-001
```

---

## 🔧 How to Change Models

### **Option 1: Edit .env File**

```bash
nano .env
```

Change to:
```env
# Use Gemini 2.0 Flash (Recommended)
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_PROCESSING_MODEL=gemini-2.0-flash-exp

# Or use Gemini 1.5 Pro (Higher quality, slower)
GEMINI_MODEL=gemini-1.5-pro-latest
GEMINI_PROCESSING_MODEL=gemini-1.5-pro-latest

# Or use Gemini 1.5 Flash (Faster, lower cost)
GEMINI_MODEL=gemini-1.5-flash-latest
GEMINI_PROCESSING_MODEL=gemini-1.5-flash-latest
```

### **Option 2: Export Environment Variables**

```bash
export GEMINI_MODEL=gemini-2.0-flash-exp
export GEMINI_PROCESSING_MODEL=gemini-2.0-flash-exp
```

---

## 🎯 Model Usage in Your Bot

### **1. SOP Processing (First Time):**
Uses `GEMINI_PROCESSING_MODEL`:
- Upload documents
- Extract all content
- Create summaries
- Generate key points

### **2. Question Answering:**
Uses `GEMINI_MODEL`:
- Process user queries
- Generate Tanglish responses
- Real-time voice interaction

### **3. Embeddings:**
Uses `EMBEDDING_MODEL`:
- Create vector embeddings
- Semantic search
- Retrieval

---

## 📊 Model Comparison

| Feature | Flash 2.0 | Pro 1.5 | Flash 1.5 |
|---------|-----------|---------|-----------|
| **Speed** | Fast ⚡ | Slower 🐢 | Fastest ⚡⚡ |
| **Quality** | Excellent ✨ | Best 🌟 | Good ✓ |
| **Cost** | Low 💰 | High 💰💰💰 | Lowest 💰 |
| **Multimodal** | Yes ✓ | Yes ✓ | Yes ✓ |
| **Context** | 1M tokens | 2M tokens | 1M tokens |
| **Recommended** | ✅ | For complex tasks | For speed |

---

## 💡 Recommendations

### **For Your Use Case (SOPs):**

**Best Choice:** `gemini-2.0-flash-exp`
- ✅ Fast processing
- ✅ Excellent quality
- ✅ Good for multimodal (images)
- ✅ Cost-effective
- ✅ Latest features

**Alternative:** `gemini-1.5-pro-latest`
- ✅ Highest quality
- ✅ Best for complex SOPs
- ⚠️ Slower processing
- ⚠️ Higher cost

**Budget Option:** `gemini-1.5-flash-latest`
- ✅ Fastest
- ✅ Lowest cost
- ⚠️ Slightly lower quality

---

## 🔍 Verify Your Configuration

### **Check Current Model:**

```bash
# View your .env file
cat .env | grep GEMINI

# Should show:
# GEMINI_MODEL=gemini-2.0-flash-exp
# GEMINI_PROCESSING_MODEL=gemini-2.0-flash-exp
```

### **Test in Python:**

```python
from config import Config

config = Config()
print(f"API Key configured: {bool(config.google_api_key)}")
print(f"Model: {config.gemini_model}")
print(f"Processing Model: {config.gemini_processing_model}")
```

---

## 🚀 After Changing Models

### **Restart Your Application:**

```bash
# For CLI
python main.py

# For Web
python web_app.py

# For Live API
python web_live_api.py
```

### **Rebuild Index (If Needed):**

```bash
python main.py
> Option 6: Rebuild index

# This will use the new processing model
```

---

## 📝 Important Notes

### **About "Gemini 3":**
- **Currently:** Gemini 3 does not exist yet
- **Latest:** Gemini 2.0 (December 2024)
- **Best model:** `gemini-2.0-flash-exp`

### **Model Names:**
Always use the exact model names as specified by Google:
- ✅ `gemini-2.0-flash-exp`
- ✅ `gemini-1.5-pro-latest`
- ✅ `gemini-1.5-flash-latest`
- ❌ `gemini-3-pro-preview` (doesn't exist)

### **API Key:**
- Same API key works for all models
- Configured in `.env` file
- Used automatically by all components

---

## 🎯 Your Current Setup

Based on your `.env` file, you're using:

```
API Key: ✓ Configured from .env
Model: gemini-2.0-flash-exp (Latest)
Processing: gemini-2.0-flash-exp (Latest)
Status: ✅ Optimal configuration
```

---

## 🔧 Quick Commands

### **View Current Config:**
```bash
cat .env | grep GEMINI
```

### **Change to Pro Model:**
```bash
sed -i 's/gemini-2.0-flash-exp/gemini-1.5-pro-latest/g' .env
```

### **Reset to Default:**
```bash
cp .env.example .env
# Then add your API key
```

---

## 📊 Cost Estimates

### **Gemini 2.0 Flash:**
- Input: ~$0.075 per 1M tokens
- Output: ~$0.30 per 1M tokens
- **Your SOPs:** ~$0.10 one-time

### **Gemini 1.5 Pro:**
- Input: ~$1.25 per 1M tokens
- Output: ~$5.00 per 1M tokens
- **Your SOPs:** ~$1.50 one-time

### **Gemini 1.5 Flash:**
- Input: ~$0.075 per 1M tokens
- Output: ~$0.30 per 1M tokens
- **Your SOPs:** ~$0.08 one-time

---

## ✅ Summary

### **Your Configuration:**
- ✅ Using latest Gemini 2.0 Flash
- ✅ API key from .env file
- ✅ Optimal for your use case
- ✅ Cost-effective
- ✅ Production-ready

### **No Changes Needed:**
Your current setup is already using the best available model!

---

**Your bot is configured with the latest Gemini 2.0 model!** 🚀

