"""
Speech recognition module using Gemini API
Converts audio to text using Gemini's capabilities
"""
import base64
from pathlib import Path
from typing import Optional
import google.generativeai as genai
from loguru import logger
import numpy as np


class SpeechRecognizer:
    """Convert speech to text using Gemini API"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize speech recognizer
        
        Args:
            api_key: Google API key
            model_name: Gemini model to use
        """
        if not api_key:
            raise ValueError("API key is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
        logger.info(f"Initialized SpeechRecognizer with model: {model_name}")
    
    def transcribe_audio_file(self, audio_path: Path) -> Optional[str]:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file (WAV format)
            
        Returns:
            Transcribed text or None
        """
        try:
            logger.info(f"Transcribing audio file: {audio_path}")
            
            # Upload audio file
            audio_file = genai.upload_file(path=str(audio_path))
            
            # Create prompt for transcription
            prompt = "Please transcribe this audio. Only provide the transcribed text, nothing else."
            
            # Generate transcription
            response = self.model.generate_content([prompt, audio_file])
            
            if response.text:
                transcribed_text = response.text.strip()
                logger.info(f"Transcribed: {transcribed_text}")
                return transcribed_text
            else:
                logger.warning("No transcription in response")
                return None
                
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
    
    def transcribe_audio_bytes(
        self,
        audio_data: bytes,
        sample_rate: int = 16000
    ) -> Optional[str]:
        """
        Transcribe audio from bytes
        
        Args:
            audio_data: Raw audio bytes
            sample_rate: Audio sample rate
            
        Returns:
            Transcribed text or None
        """
        try:
            # Save to temporary file and transcribe
            import tempfile
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_path = Path(tmp_file.name)
                
                # Write WAV file
                import wave
                with wave.open(str(tmp_path), 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(sample_rate)
                    wf.writeframes(audio_data)
                
                # Transcribe
                result = self.transcribe_audio_file(tmp_path)
                
                # Clean up
                tmp_path.unlink()
                
                return result
                
        except Exception as e:
            logger.error(f"Error transcribing audio bytes: {e}")
            return None
    
    def is_audio_clear(self, transcription: str) -> bool:
        """
        Check if transcription is clear and not empty
        
        Args:
            transcription: Transcribed text
            
        Returns:
            True if audio is clear
        """
        if not transcription or not transcription.strip():
            return False
        
        # Check for common unclear indicators
        unclear_phrases = [
            "[unclear]",
            "[inaudible]",
            "[silence]",
            "..."
        ]
        
        return not any(phrase in transcription.lower() for phrase in unclear_phrases)
