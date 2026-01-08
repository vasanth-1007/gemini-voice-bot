"""
Configuration management for Gemini Voice Bot
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config(BaseModel):
    """Main configuration class for the voice bot"""
    
    # API Configuration
    google_api_key: str = Field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))
    gemini_model: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"))
    gemini_processing_model: str = Field(default_factory=lambda: os.getenv("GEMINI_PROCESSING_MODEL", "gemini-2.0-flash-exp"))
    embedding_model: str = Field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "models/embedding-001"))
    
    # SOP Configuration
    sop_folder: Path = Field(default_factory=lambda: Path(os.getenv("SOP_FOLDER", "./sops")))
    chunk_size: int = Field(default_factory=lambda: int(os.getenv("CHUNK_SIZE", "1000")))
    chunk_overlap: int = Field(default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "200")))
    
    # Voice Configuration
    sample_rate: int = Field(default_factory=lambda: int(os.getenv("SAMPLE_RATE", "16000")))
    channels: int = Field(default_factory=lambda: int(os.getenv("CHANNELS", "1")))
    audio_format: str = Field(default_factory=lambda: os.getenv("AUDIO_FORMAT", "int16"))
    
    # Retrieval Configuration
    top_k_results: int = Field(default_factory=lambda: int(os.getenv("TOP_K_RESULTS", "3")))
    similarity_threshold: float = Field(default_factory=lambda: float(os.getenv("SIMILARITY_THRESHOLD", "0.7")))
    
    # Logging Configuration
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_file: str = Field(default_factory=lambda: os.getenv("LOG_FILE", "gemini_voice_bot.log"))
    
    # ChromaDB Configuration
    chroma_persist_dir: Path = Field(default_factory=lambda: Path("./chroma_db"))
    collection_name: str = "sop_documents"
    
    class Config:
        arbitrary_types_allowed = True
    
    def validate_config(self) -> list[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        if not self.google_api_key:
            errors.append("GOOGLE_API_KEY is not set in environment variables")
        
        if not self.sop_folder.exists():
            errors.append(f"SOP folder does not exist: {self.sop_folder}")
        
        return errors


# Global config instance
config = Config()
