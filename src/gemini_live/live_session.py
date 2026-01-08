"""
Gemini Live API - Real-time Voice Communication
Implements bidirectional streaming with Gemini 2.0 Flash Live
"""
import asyncio
import base64
import json
from typing import Optional, Callable, AsyncGenerator
from pathlib import Path
from loguru import logger
import numpy as np

try:
    from google import genai
    from google.genai import types
    HAS_NEW_SDK = True
except ImportError:
    HAS_NEW_SDK = False
    logger.warning("New google-genai SDK not installed. Install with: pip install google-genai")


class GeminiLiveSession:
    """
    Real-time voice communication with Gemini Live API
    Supports bidirectional audio streaming
    """
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.0-flash-exp",
        sample_rate: int = 16000
    ):
        """
        Initialize Gemini Live Session
        
        Args:
            api_key: Google API key
            model_name: Gemini model (must support Live API)
            sample_rate: Audio sample rate (16kHz recommended)
        """
        if not HAS_NEW_SDK:
            raise ImportError("google-genai SDK required. Install: pip install google-genai")
        
        self.api_key = api_key
        self.model_name = model_name
        self.sample_rate = sample_rate
        
        # Initialize client
        self.client = genai.Client(api_key=api_key)
        
        # Session state
        self.session = None
        self.is_active = False
        
        # Callbacks
        self.on_audio_callback = None
        self.on_text_callback = None
        self.on_error_callback = None
        
        logger.info(f"Initialized GeminiLiveSession: {model_name} @ {sample_rate}Hz")
    
    async def start_session(
        self,
        system_instruction: Optional[str] = None,
        tools: Optional[list] = None
    ):
        """
        Start a new live session
        
        Args:
            system_instruction: System instruction for the model
            tools: List of tools/functions the model can use
        """
        try:
            logger.info("Starting Gemini Live session...")
            
            # Configure session
            config = types.LiveConnectConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Kore"  # Natural voice
                        )
                    )
                ),
                # Enable realtime audio input with automatic activity detection (VAD)
                realtime_input_config=types.RealtimeInputConfig()
            )
            
            # Add system instruction if provided
            if system_instruction:
                config.system_instruction = system_instruction
            
            # Create live session - properly enter async context
            session_manager = self.client.aio.live.connect(
                model=self.model_name,
                config=config
            )
            
            # Enter the context manager to get the actual session
            self.session = await session_manager.__aenter__()
            self._session_manager = session_manager  # Store for cleanup
            
            self.is_active = True
            logger.info("✅ Live session started successfully")
            
            # Start receiving responses
            asyncio.create_task(self._receive_responses())
            
        except Exception as e:
            logger.error(f"Error starting live session: {e}")
            if self.on_error_callback:
                await self.on_error_callback(str(e))
            raise
    
    async def send_audio(self, audio_data: bytes):
        """
        Send audio data to Gemini Live API
        
        Args:
            audio_data: Raw audio bytes (16-bit PCM, mono, 16kHz)
        """
        if not self.is_active or not self.session:
            logger.warning("Session not active. Cannot send audio.")
            return
        
        try:
            # Create a Blob object with the audio data
            # mime_type must include the sample rate for PCM audio
            audio_blob = types.Blob(
                data=audio_data,
                mime_type=f'audio/pcm;rate={self.sample_rate}'
            )
            
            # Use send_realtime_input for continuous audio streaming
            # This method is optimized for real-time audio with VAD
            await self.session.send_realtime_input(audio=audio_blob)
            
            logger.debug(f"Sent audio chunk: {len(audio_data)} bytes")
            
        except Exception as e:
            logger.error(f"Error sending audio: {e}")
            if self.on_error_callback:
                await self.on_error_callback(str(e))
    
    async def send_text(self, text: str):
        """
        Send text message to Gemini Live API
        
        Args:
            text: Text message to send
        """
        if not self.is_active or not self.session:
            logger.warning("Session not active. Cannot send text.")
            return
        
        try:
            # Send text with proper parameter
            await self.session.send(input=text, end_of_turn=True)
            
            logger.info(f"Sent text: {text}")
            
        except Exception as e:
            logger.error(f"Error sending text: {e}")
            if self.on_error_callback:
                await self.on_error_callback(str(e))
    
    async def _receive_responses(self):
        """Receive and process responses from Gemini Live API"""
        try:
            async for response in self.session.receive():
                if response.server_content:
                    await self._process_server_content(response.server_content)
                
                if response.tool_call:
                    logger.info(f"Tool call received: {response.tool_call}")
                
        except Exception as e:
            logger.error(f"Error receiving responses: {e}")
            if self.on_error_callback:
                await self.on_error_callback(str(e))
    
    async def _process_server_content(self, content):
        """Process server content (audio/text responses)"""
        try:
            if content.model_turn:
                for part in content.model_turn.parts:
                    # Handle audio response
                    if part.inline_data and part.inline_data.mime_type.startswith("audio"):
                        audio_data = base64.b64decode(part.inline_data.data)
                        logger.debug(f"Received audio: {len(audio_data)} bytes")
                        
                        if self.on_audio_callback:
                            await self.on_audio_callback(audio_data)
                    
                    # Handle text response
                    if part.text:
                        logger.info(f"Received text: {part.text}")
                        
                        if self.on_text_callback:
                            await self.on_text_callback(part.text)
        
        except Exception as e:
            logger.error(f"Error processing server content: {e}")
    
    async def end_session(self):
        """End the live session"""
        try:
            if self.session:
                # Properly exit the context manager
                if hasattr(self, '_session_manager'):
                    await self._session_manager.__aexit__(None, None, None)
                self.session = None
                self.is_active = False
                logger.info("Live session ended")
        except Exception as e:
            logger.error(f"Error ending session: {e}")
    
    def set_callbacks(
        self,
        on_audio: Optional[Callable] = None,
        on_text: Optional[Callable] = None,
        on_error: Optional[Callable] = None
    ):
        """
        Set callback functions for responses
        
        Args:
            on_audio: Callback for audio responses
            on_text: Callback for text responses
            on_error: Callback for errors
        """
        self.on_audio_callback = on_audio
        self.on_text_callback = on_text
        self.on_error_callback = on_error


class LiveVoiceChat:
    """
    High-level interface for live voice chat with SOP context
    """
    
    def __init__(
        self,
        api_key: str,
        sop_context: Optional[str] = None,
        sample_rate: int = 16000
    ):
        """
        Initialize live voice chat
        
        Args:
            api_key: Google API key
            sop_context: SOP context to provide to model
            sample_rate: Audio sample rate
        """
        self.api_key = api_key
        self.sop_context = sop_context
        self.sample_rate = sample_rate
        
        # Create session
        self.session = GeminiLiveSession(
            api_key=api_key,
            sample_rate=sample_rate
        )
        
        # Audio buffer
        self.audio_buffer = []
        
        logger.info("Initialized LiveVoiceChat")
    
    async def start(self):
        """Start live voice chat session"""
        # Prepare system instruction with SOP context
        system_instruction = self._prepare_system_instruction()
        
        # Set up callbacks
        self.session.set_callbacks(
            on_audio=self._handle_audio_response,
            on_text=self._handle_text_response,
            on_error=self._handle_error
        )
        
        # Start session
        await self.session.start_session(system_instruction=system_instruction)
    
    def _prepare_system_instruction(self) -> str:
        """Prepare system instruction with SOP context"""
        base_instruction = """You are a helpful voice assistant that answers questions about Standard Operating Procedures (SOPs).

IMPORTANT RULES:
1. Respond in Tanglish (Tamil written in English letters)
2. Be clear, professional, and conversational
3. Keep responses concise for voice
4. If information is not in the SOP, say: "Indha question ku SOP la information illa."
"""
        
        if self.sop_context:
            base_instruction += f"\n\nSOP INFORMATION:\n{self.sop_context}\n"
            base_instruction += "\nAnswer questions based ONLY on the above SOP information."
        
        return base_instruction
    
    async def send_audio_chunk(self, audio_data: bytes):
        """Send audio chunk to live session"""
        await self.session.send_audio(audio_data)
    
    async def send_text(self, text: str):
        """Send text message to live session"""
        await self.session.send_text(text)
    
    async def _handle_audio_response(self, audio_data: bytes):
        """Handle audio response from model"""
        # Store in buffer for playback
        self.audio_buffer.append(audio_data)
        logger.info(f"Received audio response: {len(audio_data)} bytes")
    
    async def _handle_text_response(self, text: str):
        """Handle text response from model"""
        logger.info(f"Model response (text): {text}")
    
    async def _handle_error(self, error: str):
        """Handle error from model"""
        logger.error(f"Live session error: {error}")
    
    def get_audio_buffer(self) -> list:
        """Get accumulated audio responses"""
        buffer = self.audio_buffer.copy()
        self.audio_buffer.clear()
        return buffer
    
    async def stop(self):
        """Stop live voice chat session"""
        await self.session.end_session()
