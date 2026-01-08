# 🏗️ Architecture Documentation - Gemini Voice Bot

## System Overview

The Gemini Voice Bot is built using a modular, production-ready architecture that separates concerns into distinct layers:

1. **Document Processing Layer** - SOP loading and parsing
2. **Retrieval Layer** - RAG with vector search
3. **AI Integration Layer** - Gemini API clients
4. **Voice I/O Layer** - Audio processing and speech
5. **Orchestration Layer** - Main assistant logic

## Detailed Architecture

### 1. Document Processing Layer

**Location:** `src/sop_loader/`

**Components:**

#### DocumentParser (`document_parser.py`)
- **Purpose:** Load and parse SOP documents from local folder
- **Supported Formats:** PDF, DOCX, TXT
- **Key Methods:**
  - `load_all_documents()` - Batch load all SOPs
  - `_parse_pdf()` - Extract text from PDFs
  - `_parse_docx()` - Extract text from Word documents
  - `_parse_txt()` - Load plain text files

**Design Decisions:**
- Page-level chunking for PDFs maintains context
- Extensible design allows easy addition of new formats
- Error handling per document prevents cascade failures

**Data Flow:**
```
SOP Files (PDF/DOCX/TXT)
    ↓
DocumentParser
    ↓
List[DocumentChunk]
    ↓
Text Chunker
```

### 2. Retrieval Layer (RAG)

**Location:** `src/retrieval/`

**Components:**

#### TextChunker (`text_chunker.py`)
- **Purpose:** Split large documents into smaller, overlapping chunks
- **Algorithm:** Sliding window with intelligent boundary detection
- **Key Features:**
  - Respects sentence boundaries
  - Configurable chunk size and overlap
  - Maintains source metadata

**Configuration:**
```python
chunk_size = 1000      # characters per chunk
chunk_overlap = 200    # overlapping characters
```

#### VectorStore (`vector_store.py`)
- **Purpose:** Semantic search using embeddings
- **Technology:** ChromaDB with persistent storage
- **Key Methods:**
  - `add_documents()` - Index new documents
  - `search()` - Semantic similarity search
  - `rebuild_index()` - Full index rebuild

**Embedding Strategy:**
- Uses ChromaDB's default embedding function
- Alternatively supports custom embeddings via Google Embedding API
- Persistent storage for fast startup

#### RAGEngine (`rag_engine.py`)
- **Purpose:** Orchestrate retrieval and prompt construction
- **Key Features:**
  - Top-K retrieval with similarity threshold
  - Context assembly from multiple documents
  - Prompt engineering for Tanglish responses

**Retrieval Algorithm:**
```python
1. Convert query to embedding
2. Search vector store (top_k=3)
3. Filter by similarity threshold (0.7)
4. Combine retrieved contexts
5. Build prompt with context
6. Return to generation layer
```

**Design Decisions:**
- Top-K = 3 balances context quality vs token usage
- Similarity threshold prevents irrelevant context
- No context found → explicit "not in SOP" message

### 3. AI Integration Layer

**Location:** `src/gemini_integration/`

**Components:**

#### GeminiClient (`gemini_client.py`)
- **Purpose:** Text generation and embeddings
- **Model:** `gemini-2.0-flash-exp` (configurable)
- **Key Features:**
  - Retry logic with exponential backoff
  - Token counting
  - Safety settings
  - Streaming support

**Safety Configuration:**
```python
safety_settings = [
    HARM_CATEGORY_HARASSMENT: BLOCK_MEDIUM_AND_ABOVE,
    HARM_CATEGORY_HATE_SPEECH: BLOCK_MEDIUM_AND_ABOVE,
    HARM_CATEGORY_SEXUALLY_EXPLICIT: BLOCK_MEDIUM_AND_ABOVE,
    HARM_CATEGORY_DANGEROUS_CONTENT: BLOCK_MEDIUM_AND_ABOVE
]
```

#### GeminiLiveAPIHandler (`live_api_handler.py`)
- **Purpose:** Real-time voice interaction
- **Protocol:** Bidirectional streaming
- **Key Features:**
  - Async/await architecture
  - Audio chunk processing
  - Event-driven callbacks
  - Session management

**Callback Architecture:**
```python
callbacks = {
    'on_audio_response': handle_audio,
    'on_text_response': handle_text,
    'on_error': handle_error
}
```

**Design Decisions:**
- Async design for non-blocking I/O
- Callback pattern for flexible integration
- System instruction injection for SOP context

### 4. Voice I/O Layer

**Location:** `src/voice_handler/`

**Components:**

#### AudioProcessor (`audio_processor.py`)
- **Purpose:** Record and playback audio
- **Technology:** sounddevice + numpy
- **Key Features:**
  - Real-time recording
  - WAV file I/O
  - Silence detection
  - Audio format conversion

**Audio Specifications:**
```python
sample_rate = 16000 Hz  # Standard for speech
channels = 1            # Mono
dtype = int16           # 16-bit PCM
```

#### SpeechRecognizer (`speech_recognition.py`)
- **Purpose:** Convert speech to text
- **Technology:** Gemini API for transcription
- **Process:**
  1. Accept audio file or bytes
  2. Upload to Gemini
  3. Request transcription
  4. Validate clarity

**Design Decisions:**
- Gemini API provides multilingual support
- Quality validation prevents poor transcriptions
- Temporary file handling for byte streams

#### TextToSpeech (`text_to_speech.py`)
- **Purpose:** Generate voice responses
- **Technology:** Google Cloud TTS (with fallback)
- **Key Features:**
  - Multiple voice options
  - Language code support
  - Audio format customization

**Fallback Strategy:**
```python
try:
    tts = TextToSpeech(language_code="en-IN")
except:
    tts = SimpleTTS()  # System TTS fallback
```

### 5. Orchestration Layer

**Location:** `src/voice_assistant.py`

**Component:** `GeminiVoiceAssistant`

**Purpose:** Main orchestrator integrating all layers

**Initialization Flow:**
```
1. Load configuration
2. Initialize document parser
3. Initialize text chunker
4. Initialize vector store
5. Initialize RAG engine
6. Initialize Gemini clients
7. Initialize audio processor
8. Initialize speech recognizer
9. Initialize TTS
```

**Query Processing Flow:**

**Text Query:**
```
User Input (text)
    ↓
RAG Engine (retrieve context)
    ↓
Gemini Client (generate response)
    ↓
Response (Tanglish text)
```

**Voice Query:**
```
User Input (audio file)
    ↓
Speech Recognizer (transcribe)
    ↓
RAG Engine (retrieve context)
    ↓
Gemini Client (generate response)
    ↓
TTS (synthesize speech)
    ↓
Audio Processor (playback)
    ↓
Response (Tanglish audio)
```

**Live Session:**
```
┌─────────────────────────────┐
│     Live Session Loop       │
├─────────────────────────────┤
│ 1. Record audio (5s)        │
│ 2. Transcribe speech        │
│ 3. Validate transcription   │
│ 4. Retrieve SOP context     │
│ 5. Generate response        │
│ 6. Synthesize speech        │
│ 7. Play audio response      │
│ 8. Repeat (or Ctrl+C)       │
└─────────────────────────────┘
```

## Configuration Management

**Location:** `config.py`

**Technology:** Pydantic BaseModel

**Benefits:**
- Type validation
- Default values
- Environment variable loading
- Configuration validation

**Configuration Layers:**
```
1. Hardcoded defaults (in code)
2. .env file (overrides defaults)
3. Environment variables (overrides .env)
```

## Error Handling Strategy

### Layered Error Handling

1. **Component Level:** Try-catch in each method
2. **Module Level:** Module-specific error handlers
3. **Application Level:** Top-level error display

### Error Response Types

| Error Type | Response | Location |
|------------|----------|----------|
| No SOP Info | "Indha question ku SOP la information illa." | RAG Engine |
| Unclear Audio | "Audio clear-a illa. Please repeat pannunga." | Speech Recognizer |
| System Error | "Sorry, error aachu. Please try again." | Voice Assistant |
| API Error | Retry with exponential backoff | Gemini Client |

### Logging Strategy

**Technology:** Loguru

**Log Levels:**
- **DEBUG:** Detailed processing steps
- **INFO:** High-level operations
- **WARNING:** Recoverable issues
- **ERROR:** Failures with stack traces

**Log Output:**
- Console: Colored, formatted logs
- File: Timestamped, rotated (10MB), retained (7 days)

## Data Flow Diagram

```
┌─────────────┐
│ User Input  │
│ (Voice/Text)│
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Speech Recognition  │ (if voice)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Text Preprocessing  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Vector Search      │ ←── ChromaDB
│  (Top-K Retrieval)  │     (SOP Index)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Context Assembly    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Prompt Construction │
│ (with Tanglish      │
│  instructions)      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Gemini API        │
│ (Text Generation)   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Text-to-Speech      │ (if voice mode)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Response Output    │
│  (Voice/Text)       │
└─────────────────────┘
```

## Performance Considerations

### Indexing Performance
- **Cold Start:** 2-5 seconds for loading vector store
- **Warm Start:** <1 second with existing index
- **Indexing Speed:** ~100 chunks per second

### Query Performance
- **Vector Search:** 50-200ms
- **Gemini API:** 1-3 seconds
- **TTS:** 500ms - 1 second
- **Total Response Time:** 2-5 seconds

### Optimization Strategies
1. **Persistent ChromaDB:** Avoids re-indexing on restart
2. **Async Operations:** Non-blocking voice processing
3. **Retry Logic:** Handles transient API failures
4. **Batch Processing:** Efficient document indexing

## Security Architecture

### API Key Management
- Stored in `.env` file (not committed)
- Loaded via environment variables
- Never logged or exposed

### Data Privacy
- All SOP data stays local
- Vector embeddings stored locally
- No data sent to cloud except for:
  - Gemini API calls (query + retrieved context)
  - TTS/STT processing

### Content Filtering
- Gemini safety settings enabled
- Input validation on all user queries
- Output sanitization for voice responses

## Scalability Considerations

### Horizontal Scaling
- Stateless design allows multiple instances
- Shared ChromaDB instance possible
- Load balancer for API requests

### Vertical Scaling
- Increase `top_k` for more context
- Larger chunk size for longer contexts
- More sophisticated embedding models

### Future Enhancements
- Redis for session management
- PostgreSQL for conversation history
- Kubernetes deployment
- Multi-tenant support

## Testing Strategy

### Unit Tests
- Test each component in isolation
- Mock external dependencies
- Focus on business logic

### Integration Tests
- Test component interactions
- Use sample SOP documents
- Validate end-to-end flow

### Voice Testing
- Record sample audio files
- Test various accents
- Validate Tanglish output

## Deployment Architecture

### Local Deployment
```
├── Application Server (Python)
├── ChromaDB (Embedded)
├── Audio I/O (Local Hardware)
└── Gemini API (Cloud)
```

### Cloud Deployment
```
┌─────────────────┐
│  Load Balancer  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│ App 1│  │ App 2│
└───┬──┘  └──┬───┘
    │        │
    └────┬───┘
         │
┌────────▼────────┐
│   ChromaDB      │
│  (Persistent)   │
└─────────────────┘
```

## Monitoring & Observability

### Metrics to Track
- API latency (Gemini calls)
- Query response time
- Transcription accuracy
- Index size and query performance
- Error rates by type

### Logging Best Practices
- Structured logging (JSON format)
- Request ID tracking
- Performance metrics
- Error stack traces

## Maintenance Guidelines

### Regular Tasks
- **Daily:** Monitor logs for errors
- **Weekly:** Review performance metrics
- **Monthly:** Update vector index with new SOPs
- **Quarterly:** Review and update prompts

### Update Procedures
1. Add new SOP documents to `sops/`
2. Run index rebuild (Option 6)
3. Test with sample queries
4. Deploy to production

---

**Version:** 1.0  
**Last Updated:** January 2025  
**Maintained By:** Development Team
