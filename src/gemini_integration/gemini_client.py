"""
Gemini API client for text generation and embeddings
"""
from typing import Optional, Dict, Any
import google.generativeai as genai
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential


class GeminiClient:
    """Client for interacting with Google Gemini API"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize Gemini client
        
        Args:
            api_key: Google API key
            model_name: Name of the Gemini model to use
        """
        if not api_key:
            raise ValueError("API key is required")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model_name = model_name
        
        # Initialize model
        self.model = genai.GenerativeModel(model_name)
        
        # Safety settings for production use
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        logger.info(f"Initialized GeminiClient with model: {model_name}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Optional[str]:
        """
        Generate text using Gemini
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text or None if error
        """
        try:
            generation_config = {
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40,
            }
            
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=self.safety_settings
            )
            
            if response.text:
                logger.debug(f"Generated response: {response.text[:100]}...")
                return response.text
            else:
                logger.warning("No text in response")
                return None
                
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise
    
    def generate_streaming(self, prompt: str, temperature: float = 0.7):
        """
        Generate text with streaming (for real-time responses)
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            
        Yields:
            Text chunks as they are generated
        """
        try:
            generation_config = {
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40,
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=self.safety_settings,
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"Error in streaming generation: {e}")
            raise
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text
        
        Args:
            text: Input text
            
        Returns:
            Token count
        """
        try:
            result = self.model.count_tokens(text)
            return result.total_tokens
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            return 0
    
    def create_chat_session(self) -> Any:
        """
        Create a chat session for multi-turn conversation
        
        Returns:
            Chat session object
        """
        return self.model.start_chat(history=[])
