"""
Gemini Embedding Function for ChromaDB
Uses Google's Gemini Embedding API for high-quality embeddings
"""
from typing import List, Union
from loguru import logger
import time

try:
    from chromadb.api.types import EmbeddingFunction
    HAS_CHROMADB = True
except ImportError:
    # Fallback if chromadb types not available
    class EmbeddingFunction:
        pass
    HAS_CHROMADB = False

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False
    logger.warning("google-generativeai not installed")


class GeminiEmbeddingFunction(EmbeddingFunction):
    """
    Embedding function for ChromaDB using Gemini API
    Provides 768-dimensional embeddings optimized for retrieval
    """
    
    def __init__(
        self, 
        api_key: str,
        model_name: str = "models/embedding-001",
        task_type: str = "retrieval_document"
    ):
        """
        Initialize Gemini embedding function
        
        Args:
            api_key: Google API key
            model_name: Embedding model to use
            task_type: Task type for embeddings
        """
        if not HAS_GENAI:
            raise ImportError("google-generativeai required. Install: pip install google-generativeai")
        
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.model_name = model_name
        self.task_type = task_type
        self._model = model_name  # Store original model name
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        logger.info(f"Initialized GeminiEmbeddingFunction: {model_name}")
        logger.info(f"Task type: {task_type}")
    
    def __call__(self, input: Union[List[str], str]) -> List[List[float]]:
        """
        Generate embeddings for input texts
        
        Args:
            input: Single text or list of texts
            
        Returns:
            List of embedding vectors
        """
        # Ensure input is a list
        if isinstance(input, str):
            texts = [input]
        else:
            texts = input
        
        embeddings = []
        
        # Process in batches to handle rate limits
        batch_size = 100  # Gemini API limit
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                # Generate embeddings for batch
                batch_embeddings = self._generate_batch_embeddings(batch)
                embeddings.extend(batch_embeddings)
                
                # Small delay to avoid rate limits
                if i + batch_size < len(texts):
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error generating embeddings for batch {i}: {e}")
                # Return zero vectors for failed batch
                embeddings.extend([[0.0] * 768 for _ in batch])
        
        logger.debug(f"Generated {len(embeddings)} embeddings")
        return embeddings
    
    def _generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts"""
        embeddings = []
        
        for text in texts:
            try:
                # Generate embedding using Gemini API
                result = genai.embed_content(
                    model=self.model_name,
                    content=text,
                    task_type=self.task_type
                )
                
                embeddings.append(result['embedding'])
                
            except Exception as e:
                logger.warning(f"Error embedding text (length {len(text)}): {e}")
                # Return zero vector for failed text
                embeddings.append([0.0] * 768)
        
        return embeddings


class GeminiQueryEmbeddingFunction(GeminiEmbeddingFunction):
    """
    Specialized embedding function for queries
    Uses retrieval_query task type for better search
    """
    
    def __init__(self, api_key: str, model_name: str = "models/embedding-001"):
        super().__init__(
            api_key=api_key,
            model_name=model_name,
            task_type="retrieval_query"
        )
        logger.info("Initialized GeminiQueryEmbeddingFunction")


def create_gemini_embedding_function(api_key: str) -> GeminiEmbeddingFunction:
    """
    Factory function to create Gemini embedding function
    
    Args:
        api_key: Google API key
        
    Returns:
        GeminiEmbeddingFunction instance
    """
    return GeminiEmbeddingFunction(
        api_key=api_key,
        model_name="models/embedding-001",
        task_type="retrieval_document"
    )
