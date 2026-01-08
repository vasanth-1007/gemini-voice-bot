"""
Main Voice Assistant Orchestrator
Integrates all components: SOP loading, RAG retrieval, Gemini API, and voice I/O
"""
import asyncio
from pathlib import Path
from typing import Optional, Dict, List
from loguru import logger

# Import local modules
from config import Config
from src.sop_loader import DocumentParser, DocumentChunk
from src.retrieval import TextChunker, VectorStore, RAGEngine
from src.gemini_integration import GeminiClient, GeminiLiveAPIHandler
from src.voice_handler import AudioProcessor, SpeechRecognizer, TextToSpeech, SimpleTTS


class GeminiVoiceAssistant:
    """
    Main Voice Assistant class that orchestrates all components
    Provides real-time voice interaction with SOP-based knowledge
    """
    
    def __init__(self, config: Config):
        """
        Initialize voice assistant
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.is_initialized = False
        
        # Initialize components
        self._init_components()
        
        logger.info("GeminiVoiceAssistant initialized successfully")
    
    def _init_components(self) -> None:
        """Initialize all assistant components"""
        try:
            # 1. Gemini SOP Processor (NEW: Process SOPs through Gemini first)
            logger.info("Initializing Gemini SOP processor...")
            from src.sop_loader.gemini_processor import GeminiSOPProcessor
            
            # Use the API key from .env
            api_key = self.config.google_api_key
            processing_model = self.config.gemini_processing_model
            
            logger.info(f"Using Gemini model for processing: {processing_model}")
            logger.info(f"API key configured: {'Yes' if api_key else 'No'}")
            
            self.gemini_processor = GeminiSOPProcessor(
                api_key=api_key,
                model_name=processing_model
            )
            
            # 2. Document Parser (with image extraction)
            logger.info("Initializing document parser...")
            self.document_parser = DocumentParser(
                sop_folder=self.config.sop_folder,
                api_key=self.config.google_api_key,
                extract_images=True  # Enable image extraction for image-heavy SOPs
            )
            
            # 3. Text Chunker
            logger.info("Initializing text chunker...")
            self.text_chunker = TextChunker(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap
            )
            
            # 4. Vector Store (with Gemini embeddings)
            logger.info("Initializing vector store with Gemini embeddings...")
            from src.retrieval.gemini_embeddings import create_gemini_embedding_function
            
            # Create Gemini embedding function
            embedding_function = create_gemini_embedding_function(self.config.google_api_key)
            logger.info("✅ Using Gemini API for embeddings (768 dimensions)")
            
            self.vector_store = VectorStore(
                persist_directory=self.config.chroma_persist_dir,
                collection_name=self.config.collection_name,
                embedding_function=embedding_function
            )
            
            # 5. RAG Engine
            logger.info("Initializing RAG engine...")
            self.rag_engine = RAGEngine(
                vector_store=self.vector_store,
                top_k=self.config.top_k_results,
                similarity_threshold=self.config.similarity_threshold
            )
            
            # 6. Gemini Client
            logger.info("Initializing Gemini client...")
            self.gemini_client = GeminiClient(
                api_key=self.config.google_api_key,
                model_name=self.config.gemini_model
            )
            
            # 7. Gemini Live API Handler
            logger.info("Initializing Gemini Live API handler...")
            self.live_api_handler = GeminiLiveAPIHandler(
                api_key=self.config.google_api_key,
                model_name=self.config.gemini_model
            )
            
            # 8. Audio Processor
            logger.info("Initializing audio processor...")
            self.audio_processor = AudioProcessor(
                sample_rate=self.config.sample_rate,
                channels=self.config.channels,
                dtype=self.config.audio_format
            )
            
            # 9. Speech Recognizer
            logger.info("Initializing speech recognizer...")
            self.speech_recognizer = SpeechRecognizer(
                api_key=self.config.google_api_key,
                model_name=self.config.gemini_model
            )
            
            # 10. Text-to-Speech
            logger.info("Initializing text-to-speech...")
            try:
                self.tts = TextToSpeech(language_code="en-IN")  # Indian English for Tanglish
            except Exception as e:
                logger.warning(f"Cloud TTS not available, using fallback: {e}")
                self.tts = SimpleTTS()
            
            self.is_initialized = True
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            raise
    
    def load_and_index_sops(self, force_rebuild: bool = False, use_gemini_processing: bool = True) -> Dict:
        """
        Load SOP documents and build vector index
        
        Args:
            force_rebuild: Force rebuilding the index even if it exists
            use_gemini_processing: Use Gemini to process and extract text first
            
        Returns:
            Dictionary with indexing statistics
        """
        logger.info("Loading and indexing SOP documents...")
        
        try:
            # Check if index already exists
            existing_count = self.vector_store.get_collection_stats()['document_count']
            
            if existing_count > 0 and not force_rebuild:
                logger.info(f"Using existing index with {existing_count} documents")
                return {
                    'status': 'existing',
                    'document_count': existing_count,
                    'rebuilt': False,
                    'gemini_processed': False
                }
            
            all_chunks = []
            
            if use_gemini_processing:
                # NEW APPROACH: Process through Gemini first
                logger.info("🚀 Processing SOPs through Gemini for intelligent extraction...")
                
                # Get all SOP files
                files = [f for f in self.config.sop_folder.iterdir() 
                        if f.is_file() and f.suffix.lower() in ['.pdf', '.docx', '.txt']]
                
                if not files:
                    logger.warning("No documents found in SOP folder")
                    return {
                        'status': 'empty',
                        'document_count': 0,
                        'rebuilt': False,
                        'gemini_processed': False
                    }
                
                logger.info(f"Found {len(files)} documents to process")
                
                # Process each document through Gemini
                for file_path in files:
                    try:
                        logger.info(f"Processing {file_path.name} through Gemini...")
                        
                        # Process document with Gemini
                        processed_contents = self.gemini_processor.process_document(file_path)
                        
                        if not processed_contents:
                            logger.warning(f"No content extracted from {file_path.name}")
                            continue
                        
                        # Convert processed content to vector chunks
                        for processed in processed_contents:
                            chunks = self.gemini_processor.create_vector_chunks(
                                processed,
                                chunk_size=self.config.chunk_size,
                                include_summary=True
                            )
                            all_chunks.extend(chunks)
                            
                            logger.info(f"✅ Created {len(chunks)} chunks from {file_path.name}")
                            logger.info(f"   Summary: {processed.summary[:100]}...")
                            logger.info(f"   Key Points: {len(processed.key_points)}")
                            logger.info(f"   Topics: {len(processed.topics)}")
                        
                    except Exception as e:
                        logger.error(f"Error processing {file_path.name} with Gemini: {e}")
                        logger.info(f"Falling back to standard extraction for {file_path.name}")
                        # Fallback to standard processing
                        continue
                
                stats_extra = {
                    'gemini_processed': True,
                    'processing_method': 'gemini'
                }
                
            else:
                # ORIGINAL APPROACH: Standard text extraction
                logger.info("Using standard text extraction...")
                
                document_chunks = self.document_parser.load_all_documents()
                
                if not document_chunks:
                    logger.warning("No documents found in SOP folder")
                    return {
                        'status': 'empty',
                        'document_count': 0,
                        'rebuilt': False,
                        'gemini_processed': False
                    }
                
                # Convert to dict format for chunking
                doc_dicts = [
                    {
                        'content': chunk.content,
                        'source': chunk.source,
                        'page_number': chunk.page_number,
                        'metadata': chunk.metadata or {}
                    }
                    for chunk in document_chunks
                ]
                
                # Chunk documents
                logger.info("Chunking documents...")
                all_chunks = self.text_chunker.chunk_documents(doc_dicts)
                
                stats_extra = {
                    'gemini_processed': False,
                    'processing_method': 'standard'
                }
            
            if not all_chunks:
                logger.warning("No chunks created")
                return {
                    'status': 'empty',
                    'document_count': 0,
                    'rebuilt': False,
                    **stats_extra
                }
            
            # Build vector index
            logger.info(f"Building vector index with {len(all_chunks)} chunks...")
            if force_rebuild:
                self.vector_store.rebuild_index(all_chunks)
            else:
                self.vector_store.add_documents(all_chunks)
            
            stats = {
                'status': 'success',
                'document_count': len(all_chunks),
                'source_documents': len(set(d['source'] for d in all_chunks)),
                'rebuilt': force_rebuild,
                **stats_extra
            }
            
            logger.info(f"✅ Indexing complete: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error loading and indexing SOPs: {e}")
            raise
    
    def process_text_query(self, query: str) -> str:
        """
        Process a text query and return response
        
        Args:
            query: User query text
            
        Returns:
            Response text in Tanglish
        """
        logger.info(f"Processing query: {query}")
        
        try:
            # Retrieve relevant context
            retrieval_result = self.rag_engine.retrieve_context(query)
            
            if not retrieval_result['found']:
                logger.info("No relevant SOP information found")
                return self.rag_engine.format_no_context_response()
            
            # Generate response using Gemini
            prompt = self.rag_engine.format_prompt_with_context(
                query=query,
                context=retrieval_result['context']
            )
            
            response = self.gemini_client.generate_text(
                prompt=prompt,
                temperature=0.7
            )
            
            if not response:
                logger.warning("No response from Gemini")
                return "Sorry, response generate panna mudiyala. Please try again."
            
            logger.info(f"Generated response: {response[:100]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return "Sorry, error aachu. Please try again."
    
    def process_voice_query(self, audio_path: Path) -> tuple[str, str]:
        """
        Process a voice query from audio file
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Tuple of (transcribed_query, response_text)
        """
        logger.info(f"Processing voice query from {audio_path}")
        
        try:
            # Transcribe audio
            logger.info("Transcribing audio...")
            transcribed_text = self.speech_recognizer.transcribe_audio_file(audio_path)
            
            if not transcribed_text:
                logger.warning("Could not transcribe audio")
                return "", "Sorry, audio puriyala. Please speak clearly."
            
            if not self.speech_recognizer.is_audio_clear(transcribed_text):
                logger.warning("Audio transcription unclear")
                return transcribed_text, "Audio clear-a illa. Please repeat pannunga."
            
            logger.info(f"Transcribed: {transcribed_text}")
            
            # Process query
            response = self.process_text_query(transcribed_text)
            
            return transcribed_text, response
            
        except Exception as e:
            logger.error(f"Error processing voice query: {e}")
            return "", "Sorry, error aachu. Please try again."
    
    async def start_live_session(self) -> None:
        """
        Start a live voice conversation session
        Uses Gemini Live API for real-time interaction
        """
        logger.info("Starting live voice session...")
        
        try:
            # Create callbacks for live session
            async def on_text_response(text: str):
                logger.info(f"Received response: {text}")
                # Synthesize and play audio
                if self.tts:
                    audio_content = self.tts.synthesize_speech(text)
                    if audio_content:
                        audio_array = self.audio_processor.convert_from_bytes(audio_content)
                        self.audio_processor.play_audio(audio_array)
            
            async def on_error(error: Exception):
                logger.error(f"Live session error: {error}")
            
            # Create live session
            session = await self.live_api_handler.create_live_session(
                on_text_response=on_text_response,
                on_error=on_error
            )
            
            logger.info("Live session started. Press Ctrl+C to stop.")
            
            # Main conversation loop
            while True:
                try:
                    # Record audio
                    logger.info("Recording... (speak now)")
                    audio_data = self.audio_processor.record_audio(duration=5.0)
                    
                    # Convert to bytes
                    audio_bytes = self.audio_processor.convert_to_bytes(audio_data)
                    
                    # Transcribe
                    transcribed = self.speech_recognizer.transcribe_audio_bytes(
                        audio_bytes,
                        sample_rate=self.config.sample_rate
                    )
                    
                    if not transcribed:
                        logger.warning("No speech detected")
                        continue
                    
                    logger.info(f"You said: {transcribed}")
                    
                    # Process query
                    response = self.process_text_query(transcribed)
                    
                    # Send to live session for voice response
                    await self.live_api_handler.send_text_message(session, response)
                    
                except KeyboardInterrupt:
                    logger.info("Stopping live session...")
                    break
                except Exception as e:
                    logger.error(f"Error in conversation loop: {e}")
                    continue
            
            # Close session
            await self.live_api_handler.close_session(session)
            logger.info("Live session ended")
            
        except Exception as e:
            logger.error(f"Error in live session: {e}")
            raise
    
    def get_system_stats(self) -> Dict:
        """
        Get statistics about the system
        
        Returns:
            Dictionary with system statistics
        """
        return {
            'is_initialized': self.is_initialized,
            'sop_stats': self.document_parser.get_document_stats(),
            'retrieval_stats': self.rag_engine.get_retrieval_stats(),
            'config': {
                'model': self.config.gemini_model,
                'sop_folder': str(self.config.sop_folder),
                'chunk_size': self.config.chunk_size,
                'top_k': self.config.top_k_results
            }
        }
