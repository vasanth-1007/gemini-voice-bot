"""
Text-to-speech module for generating voice responses
Uses Google Text-to-Speech or Gemini capabilities
"""
from pathlib import Path
from typing import Optional
from loguru import logger
import numpy as np

try:
    from google.cloud import texttospeech
    HAS_TTS = True
except ImportError:
    HAS_TTS = False
    logger.warning("Google Text-to-Speech not available. Install google-cloud-texttospeech")


class TextToSpeech:
    """Convert text to speech audio"""
    
    def __init__(self, language_code: str = "en-US", voice_name: Optional[str] = None):
        """
        Initialize text-to-speech
        
        Args:
            language_code: Language code for speech
            voice_name: Specific voice name to use
        """
        self.language_code = language_code
        self.voice_name = voice_name
        
        if HAS_TTS:
            self.client = texttospeech.TextToSpeechClient()
            logger.info(f"Initialized TextToSpeech: {language_code}")
        else:
            self.client = None
            logger.warning("TTS client not available")
    
    def synthesize_speech(
        self,
        text: str,
        output_path: Optional[Path] = None
    ) -> Optional[bytes]:
        """
        Synthesize speech from text
        
        Args:
            text: Text to convert to speech
            output_path: Optional path to save audio file
            
        Returns:
            Audio content as bytes or None
        """
        if not self.client:
            logger.error("TTS client not initialized")
            return None
        
        try:
            # Set up synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Build voice parameters
            voice_params = {
                "language_code": self.language_code,
            }
            if self.voice_name:
                voice_params["name"] = self.voice_name
            
            voice = texttospeech.VoiceSelectionParams(**voice_params)
            
            # Set audio config
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000
            )
            
            # Perform synthesis
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Save to file if path provided
            if output_path:
                with open(output_path, 'wb') as out:
                    out.write(response.audio_content)
                logger.info(f"Saved speech to {output_path}")
            
            logger.debug(f"Synthesized speech for text: {text[:50]}...")
            return response.audio_content
            
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return None
    
    def get_available_voices(self) -> list:
        """
        Get list of available voices
        
        Returns:
            List of voice objects
        """
        if not self.client:
            return []
        
        try:
            voices = self.client.list_voices()
            return voices.voices
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []


class SimpleTTS:
    """Fallback simple TTS using system commands"""
    
    def __init__(self):
        """Initialize simple TTS"""
        logger.info("Initialized SimpleTTS (fallback)")
    
    def synthesize_speech(self, text: str, output_path: Optional[Path] = None) -> Optional[bytes]:
        """
        Simple TTS fallback (uses system TTS if available)
        
        Args:
            text: Text to speak
            output_path: Output path
            
        Returns:
            None (plays directly)
        """
        logger.info(f"TTS fallback: {text}")
        # In production, could use pyttsx3 or system TTS
        return None
