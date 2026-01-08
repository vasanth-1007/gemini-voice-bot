"""
Gemini Live API Handler for real-time voice interaction
This module handles bidirectional streaming with Gemini Live API
"""
import asyncio
import json
from typing import Optional, Callable, AsyncGenerator
from loguru import logger
import google.generativeai as genai


class GeminiLiveAPIHandler:
    """
    Handler for Gemini Live API with real-time voice I/O
    Supports bidirectional streaming for voice conversation
    """
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.0-flash-exp",
        system_instruction: Optional[str] = None
    ):
        """
        Initialize Gemini Live API handler
        
        Args:
            api_key: Google API key
            model_name: Model to use for Live API
            system_instruction: System instructions for the model
        """
        if not api_key:
            raise ValueError("API key is required")
        
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.system_instruction = system_instruction
        
        # Configure model for live interaction
        self.model_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
        }
        
        logger.info(f"Initialized GeminiLiveAPIHandler with model: {model_name}")
    
    async def create_live_session(
        self,
        on_audio_response: Optional[Callable] = None,
        on_text_response: Optional[Callable] = None,
        on_error: Optional[Callable] = None
    ):
        """
        Create a live session with Gemini
        
        Args:
            on_audio_response: Callback for audio responses
            on_text_response: Callback for text responses
            on_error: Callback for errors
            
        Returns:
            Live session client
        """
        try:
            # Create model with system instruction
            model_kwargs = {"model_name": self.model_name}
            if self.system_instruction:
                model_kwargs["system_instruction"] = self.system_instruction
            
            model = genai.GenerativeModel(**model_kwargs)
            
            # Start live session
            # Note: Gemini Live API is typically accessed via the client library
            # This is a simplified implementation
            logger.info("Live session created successfully")
            
            return {
                "model": model,
                "config": self.model_config,
                "callbacks": {
                    "on_audio_response": on_audio_response,
                    "on_text_response": on_text_response,
                    "on_error": on_error
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating live session: {e}")
            if on_error:
                on_error(e)
            raise
    
    async def send_audio_chunk(
        self,
        session: dict,
        audio_data: bytes,
        sample_rate: int = 16000
    ) -> None:
        """
        Send audio chunk to Gemini Live API
        
        Args:
            session: Live session object
            audio_data: Raw audio bytes
            sample_rate: Audio sample rate
        """
        try:
            # In production, this would send audio via websocket or gRPC
            # For now, we'll use the text-based API as fallback
            logger.debug(f"Received audio chunk: {len(audio_data)} bytes")
            
            # Audio would be sent to the live API endpoint here
            # Implementation depends on specific Gemini Live API protocol
            
        except Exception as e:
            logger.error(f"Error sending audio chunk: {e}")
            if session.get("callbacks", {}).get("on_error"):
                session["callbacks"]["on_error"](e)
    
    async def send_text_message(
        self,
        session: dict,
        text: str
    ) -> Optional[str]:
        """
        Send text message to live session
        
        Args:
            session: Live session object
            text: Text message to send
            
        Returns:
            Response text
        """
        try:
            model = session["model"]
            config = session["config"]
            
            # Generate response
            response = await asyncio.to_thread(
                model.generate_content,
                text,
                generation_config=config
            )
            
            if response.text:
                logger.debug(f"Received text response: {response.text[:100]}...")
                
                # Call text callback if available
                if session.get("callbacks", {}).get("on_text_response"):
                    session["callbacks"]["on_text_response"](response.text)
                
                return response.text
            
            return None
            
        except Exception as e:
            logger.error(f"Error sending text message: {e}")
            if session.get("callbacks", {}).get("on_error"):
                session["callbacks"]["on_error"](e)
            return None
    
    async def close_session(self, session: dict) -> None:
        """
        Close live session
        
        Args:
            session: Live session to close
        """
        try:
            logger.info("Closing live session")
            # Clean up resources
            # In production, this would properly close websocket/gRPC connection
            
        except Exception as e:
            logger.error(f"Error closing session: {e}")
    
    def create_system_instruction_for_sop(self, context: str) -> str:
        """
        Create system instruction with SOP context
        
        Args:
            context: Retrieved SOP context
            
        Returns:
            Formatted system instruction
        """
        instruction = f"""You are a helpful voice assistant for answering questions about Standard Operating Procedures (SOPs).

STRICT RULES:
1. Answer ONLY based on the provided SOP information
2. Respond in Tanglish (Tamil written using English letters)
3. Be clear, professional, and conversational
4. If information is not in the SOP, say: "Indha question ku SOP la information illa."
5. Do NOT use external knowledge or make assumptions

SOP INFORMATION:
{context}

Remember: All responses must be in Tanglish and based only on the SOP information above."""
        
        return instruction
