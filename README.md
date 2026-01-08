# 🎤 Gemini Voice Bot - SOP Assistant

A production-ready real-time voice assistant powered by **Gemini Live API** and **RAG (Retrieval Augmented Generation)**. The bot answers questions based on your Standard Operating Procedure (SOP) documents and responds in **Tanglish** (Tamil written in English letters).

## ✨ Features

- 🎯 **SOP-Based Knowledge**: Answers strictly from your local SOP documents (PDF, DOCX, TXT)
- 📸 **Image Support (NEW!)**: Understands diagrams, flowcharts, tables, and screenshots in PDFs
- 🗣️ **Real-Time Voice Interaction**: Powered by Gemini Live API for natural conversations
- 🌐 **Tanglish Responses**: Natural, conversational responses in Tamil-English mix
- 🧠 **RAG Architecture**: Semantic search with ChromaDB for accurate context retrieval
- 🔒 **No Hallucinations**: Explicitly trained to respond only from SOP documents
- 🎨 **Interactive CLI**: User-friendly command-line interface with colored output
- 📊 **Comprehensive Logging**: Detailed logging for debugging and monitoring

## 🏗️ Architecture

```
┌─────────────────┐
│  User Voice     │
│  Input          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Audio Processor │
│ (Recording)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Speech          │
│ Recognition     │
│ (Gemini API)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ RAG Engine      │
│ - Vector Search │
│ - Context       │
│   Retrieval     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Gemini Client   │
│ (Text Gen)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Text-to-Speech  │
│ (Audio Output)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Voice Response │
│  in Tanglish    │
└─────────────────┘
```

## 📁 Project Structure

```
gemini-voice-bot/
├── config.py                          # Configuration management
├── main.py                            # Main entry point
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── README.md                          # This file
│
├── sops/                              # 📂 SOP documents folder
│   ├── example.pdf                    # Place your SOP files here
│   ├── example.docx
│   └── example.txt
│
├── src/
│   ├── sop_loader/                    # 📄 Document loading module
│   │   ├── __init__.py
│   │   └── document_parser.py         # Parse PDF/DOCX/TXT files
│   │
│   ├── retrieval/                     # 🔍 RAG retrieval module
│   │   ├── __init__.py
│   │   ├── text_chunker.py            # Text chunking logic
│   │   ├── vector_store.py            # ChromaDB vector storage
│   │   └── rag_engine.py              # RAG orchestration
│   │
│   ├── gemini_integration/            # 🤖 Gemini API module
│   │   ├── __init__.py
│   │   ├── gemini_client.py           # Text generation client
│   │   └── live_api_handler.py        # Live API handler
│   │
│   ├── voice_handler/                 # 🎙️ Voice I/O module
│   │   ├── __init__.py
│   │   ├── audio_processor.py         # Audio recording/playback
│   │   ├── speech_recognition.py      # Speech-to-text
│   │   └── text_to_speech.py          # Text-to-speech
│   │
│   └── voice_assistant.py             # 🎯 Main orchestrator
│
└── chroma_db/                         # 💾 Vector database (auto-created)
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Google Cloud API key with Gemini API access
- Microphone and speakers for voice interaction
- **For image-heavy SOPs:** PyMuPDF and Pillow (see [Image Support Guide](IMAGE_SUPPORT_GUIDE.md))

### Installation

1. **Clone or create the project directory**

```bash
mkdir gemini-voice-bot
cd gemini-voice-bot
```

2. **Install dependencies**

```bash
# Basic installation
pip install -r requirements.txt

# For image-heavy SOPs (highly recommended)
pip install PyMuPDF Pillow
```

3. **Configure environment variables**

```bash
# Copy example to .env
cp .env.example .env

# Edit .env and add your API key
nano .env  # or use any text editor
```

Required in `.env`:
```env
GOOGLE_API_KEY=your_actual_api_key_here
```

4. **Add your SOP documents**

```bash
# Place your SOP files in the sops/ folder
cp /path/to/your/sop.pdf sops/
cp /path/to/your/sop.docx sops/
```

Supported formats: **PDF** (with image support), **DOCX**, **TXT**

**📸 New: Image-Heavy PDFs Supported!**
The bot automatically extracts and analyzes images (flowcharts, tables, diagrams, screenshots) using Gemini Vision. See [Image Support Guide](IMAGE_SUPPORT_GUIDE.md) for details.

### Running the Application

```bash
python main.py
```

## 📖 Usage Guide

### Interactive Menu

When you run the application, you'll see an interactive menu:

```
Available Commands:
  1 - Load and index SOP documents
  2 - Ask a text question
  3 - Ask a voice question (from file)
  4 - Start live voice session
  5 - Show system statistics
  6 - Rebuild index (force)
  q - Quit
```

### Option 1: Load and Index SOPs

Loads all documents from the `sops/` folder and builds a vector index for semantic search.

**First-time setup**: Run this before asking questions.

### Option 2: Text Question (Testing)

Type your question to test the system without voice:

```
Ask your question:
> How do I reset the password?

Response:
Password reset panna, admin portal ku ponga. Settings la "Reset Password" option iruku. 
Adha click pannunga, apro email verification varum.
```

### Option 3: Voice Question (from File)

Upload a pre-recorded audio file (WAV format):

```
Enter path to audio file (WAV format):
> /path/to/question.wav

Transcribed: What is the escalation process?
Response:
Escalation process nalladha follow pannanum. First level la team lead kitta report pannunga...
```

### Option 4: Live Voice Session

**Real-time voice conversation** using your microphone:

1. Press `4` to start
2. Speak your question when prompted
3. System will transcribe, process, and respond with voice
4. Press `Ctrl+C` to stop

### Option 5: System Statistics

View configuration and index statistics:

```
Configuration:
  model: gemini-2.0-flash-exp
  sop_folder: ./sops
  chunk_size: 1000
  top_k: 3

SOP Documents:
  total_files: 5
  supported_files: 5
  
Retrieval System:
  document_count: 127
  collection_name: sop_documents
```

### Option 6: Rebuild Index

Force rebuild of the entire vector index (useful after adding/updating SOPs).

## 🔧 Configuration

Edit `config.py` or `.env` file to customize:

### Core Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `GOOGLE_API_KEY` | Required | Your Google Gemini API key |
| `GEMINI_MODEL` | `gemini-2.0-flash-exp` | Gemini model to use |
| `SOP_FOLDER` | `./sops` | Folder containing SOP documents |

### RAG Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `CHUNK_SIZE` | `1000` | Characters per chunk |
| `CHUNK_OVERLAP` | `200` | Overlapping characters |
| `TOP_K_RESULTS` | `3` | Number of documents to retrieve |
| `SIMILARITY_THRESHOLD` | `0.7` | Minimum similarity score |

### Audio Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SAMPLE_RATE` | `16000` | Audio sample rate (Hz) |
| `CHANNELS` | `1` | Audio channels (mono) |

## 🧪 Testing

### Test with Sample Questions

Create a test file `test_queries.txt`:

```text
How do I submit a leave request?
What is the process for expense reimbursement?
Who should I contact for IT support?
```

Then test each query:

```bash
python main.py
# Select option 2 and enter each question
```

### Test Voice Input

Record a test audio file:

```bash
# Use your system's audio recorder or:
# On Linux:
arecord -d 5 -f cd test_question.wav

# On macOS:
rec -r 16000 -c 1 test_question.wav trim 0 5

# Then test with option 3
```

## 🛡️ Error Handling

The system handles various error scenarios:

### No SOP Information Available

**Response**: `"Indha question ku SOP la information illa."`

Occurs when:
- Query is outside SOP scope
- Similarity score too low
- No relevant documents found

### Audio Unclear

**Response**: `"Audio clear-a illa. Please repeat pannunga."`

Occurs when:
- Poor audio quality
- Background noise
- Unclear speech

### System Errors

**Response**: `"Sorry, error aachu. Please try again."`

Occurs when:
- API errors
- Network issues
- Internal exceptions

All errors are logged to `gemini_voice_bot.log` for debugging.

## 📊 Monitoring & Logs

### Log Files

- **Location**: `gemini_voice_bot.log`
- **Rotation**: 10 MB per file
- **Retention**: 7 days
- **Format**: Timestamped with level and context

### Log Levels

```python
# View all logs
tail -f gemini_voice_bot.log

# View errors only
grep "ERROR" gemini_voice_bot.log

# View specific component
grep "RAGEngine" gemini_voice_bot.log
```

## 🔐 Security & Privacy

- **API Keys**: Never commit `.env` file to version control
- **Local Processing**: All SOP documents stay on your machine
- **No External DB**: Vector database stored locally in `chroma_db/`
- **Safe Responses**: Content filtering via Gemini safety settings

## 🐛 Troubleshooting

### Issue: "GOOGLE_API_KEY not set"

**Solution**: 
```bash
# Make sure .env file exists and contains your key
echo "GOOGLE_API_KEY=your_key_here" > .env
```

### Issue: "No documents found in SOP folder"

**Solution**:
```bash
# Add documents to sops/ folder
cp your_document.pdf sops/
# Then run option 1 to index
```

### Issue: "Audio device not found"

**Solution**:
```bash
# Install system audio libraries
# Ubuntu/Debian:
sudo apt-get install portaudio19-dev python3-pyaudio

# macOS:
brew install portaudio
```

### Issue: ChromaDB errors

**Solution**:
```bash
# Clear the database and rebuild
rm -rf chroma_db/
# Run option 6 to rebuild index
```

## 🚀 Advanced Usage

### Custom Document Processing

Extend `DocumentParser` to support more formats:

```python
# In src/sop_loader/document_parser.py
def _parse_markdown(self, file_path: Path) -> List[DocumentChunk]:
    # Add custom parsing logic
    pass
```

### Custom Embedding Models

Use different embedding models:

```python
# In config.py
EMBEDDING_MODEL = "models/text-embedding-004"
```

### Adjust Retrieval Parameters

Fine-tune retrieval for your use case:

```python
# In .env
TOP_K_RESULTS=5          # Retrieve more documents
SIMILARITY_THRESHOLD=0.6  # Lower threshold for more results
```

## 📚 Dependencies

Key libraries used:

- **google-generativeai**: Gemini API client
- **chromadb**: Vector database
- **sentence-transformers**: Text embeddings
- **sounddevice**: Audio I/O
- **PyPDF2**: PDF parsing
- **python-docx**: DOCX parsing
- **loguru**: Advanced logging
- **pydantic**: Configuration validation

## 🤝 Contributing

This is a production-ready template. To extend:

1. Add new document formats in `src/sop_loader/`
2. Implement custom retrieval strategies in `src/retrieval/`
3. Add new voice providers in `src/voice_handler/`
4. Extend Gemini integration in `src/gemini_integration/`

## 📄 License

This project is provided as-is for educational and commercial use.

## 🆘 Support

For issues or questions:

1. Check the logs: `gemini_voice_bot.log`
2. Review configuration: Option 5 in menu
3. Rebuild index: Option 6 in menu
4. Check API key and quota

## 🎯 Roadmap

Potential enhancements:

- [ ] Web UI with real-time streaming
- [ ] Multi-language support beyond Tanglish
- [ ] Document version tracking
- [ ] User authentication and sessions
- [ ] Cloud deployment guides
- [ ] Conversation history persistence
- [ ] Advanced analytics dashboard

---

**Built with ❤️ using Gemini AI and Python**

*For enterprise support and customization, please contact your AI solutions provider.*
