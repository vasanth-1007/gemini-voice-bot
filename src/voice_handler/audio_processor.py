"""
Audio processing module for voice input and output
Handles recording, playback, and audio format conversion
"""
import wave
import struct
import tempfile
from pathlib import Path
from typing import Optional, Callable
import numpy as np
from loguru import logger

try:
    import sounddevice as sd
except ImportError:
    logger.warning("sounddevice not installed. Audio functionality may be limited.")


class AudioProcessor:
    """Handle audio recording and playback for voice interaction"""
    
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        dtype: str = 'int16'
    ):
        """
        Initialize audio processor
        
        Args:
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels (1=mono, 2=stereo)
            dtype: Audio data type
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        self.is_recording = False
        self.recorded_frames = []
        
        logger.info(f"Initialized AudioProcessor: {sample_rate}Hz, {channels}ch, {dtype}")
    
    def record_audio(
        self,
        duration: Optional[float] = None,
        on_chunk: Optional[Callable] = None
    ) -> np.ndarray:
        """
        Record audio from microphone
        
        Args:
            duration: Recording duration in seconds (None for manual stop)
            on_chunk: Callback for processing audio chunks in real-time
            
        Returns:
            Recorded audio as numpy array
        """
        try:
            logger.info(f"Starting audio recording (duration: {duration or 'manual stop'})")
            
            if duration:
                # Record for fixed duration
                recording = sd.rec(
                    int(duration * self.sample_rate),
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    dtype=self.dtype
                )
                sd.wait()
                logger.info("Recording completed")
                return recording
            else:
                # Record until stopped (would need stream implementation)
                logger.warning("Continuous recording not implemented in this version")
                return np.array([])
                
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            raise
    
    def play_audio(self, audio_data: np.ndarray) -> None:
        """
        Play audio through speakers
        
        Args:
            audio_data: Audio data as numpy array
        """
        try:
            logger.debug(f"Playing audio: {len(audio_data)} samples")
            sd.play(audio_data, self.sample_rate)
            sd.wait()
            logger.debug("Playback completed")
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            raise
    
    def save_audio(self, audio_data: np.ndarray, file_path: Path) -> None:
        """
        Save audio to WAV file
        
        Args:
            audio_data: Audio data as numpy array
            file_path: Output file path
        """
        try:
            with wave.open(str(file_path), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())
            
            logger.info(f"Saved audio to {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            raise
    
    def load_audio(self, file_path: Path) -> np.ndarray:
        """
        Load audio from WAV file
        
        Args:
            file_path: Input file path
            
        Returns:
            Audio data as numpy array
        """
        try:
            with wave.open(str(file_path), 'rb') as wf:
                frames = wf.readframes(wf.getnframes())
                audio_data = np.frombuffer(frames, dtype=self.dtype)
            
            logger.info(f"Loaded audio from {file_path}")
            return audio_data
            
        except Exception as e:
            logger.error(f"Error loading audio: {e}")
            raise
    
    def convert_to_bytes(self, audio_data: np.ndarray) -> bytes:
        """
        Convert numpy array to bytes
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Audio data as bytes
        """
        return audio_data.tobytes()
    
    def convert_from_bytes(self, audio_bytes: bytes) -> np.ndarray:
        """
        Convert bytes to numpy array
        
        Args:
            audio_bytes: Audio data as bytes
            
        Returns:
            Audio data as numpy array
        """
        return np.frombuffer(audio_bytes, dtype=self.dtype)
    
    def detect_silence(
        self,
        audio_data: np.ndarray,
        threshold: float = 0.01,
        min_silence_duration: float = 1.0
    ) -> bool:
        """
        Detect if audio contains silence
        
        Args:
            audio_data: Audio data to analyze
            threshold: Amplitude threshold for silence
            min_silence_duration: Minimum silence duration in seconds
            
        Returns:
            True if silence detected
        """
        # Calculate RMS amplitude
        rms = np.sqrt(np.mean(audio_data ** 2))
        
        if rms < threshold:
            logger.debug(f"Silence detected: RMS={rms:.4f}")
            return True
        
        return False
    
    def get_audio_stats(self, audio_data: np.ndarray) -> dict:
        """
        Get statistics about audio data
        
        Args:
            audio_data: Audio data to analyze
            
        Returns:
            Dictionary with audio statistics
        """
        return {
            'duration': len(audio_data) / self.sample_rate,
            'samples': len(audio_data),
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'rms_amplitude': float(np.sqrt(np.mean(audio_data ** 2))),
            'max_amplitude': float(np.max(np.abs(audio_data)))
        }
