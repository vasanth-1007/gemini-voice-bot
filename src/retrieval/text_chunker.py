"""
Text chunking module for splitting documents into smaller pieces
"""
from typing import List
from loguru import logger


class TextChunker:
    """Split text into overlapping chunks for better retrieval"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize text chunker
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        if chunk_overlap >= chunk_size:
            raise ValueError("Chunk overlap must be less than chunk size")
        
        logger.info(f"Initialized TextChunker: size={chunk_size}, overlap={chunk_overlap}")
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Calculate end position
            end = start + self.chunk_size
            
            # If this is not the last chunk, try to break at sentence boundary
            if end < text_length:
                # Look for sentence endings near the chunk boundary
                sentence_ends = ['. ', '! ', '? ', '\n\n', '\n']
                best_break = end
                
                # Search within last 100 characters for a good break point
                search_start = max(end - 100, start)
                for sentence_end in sentence_ends:
                    pos = text.rfind(sentence_end, search_start, end)
                    if pos != -1:
                        best_break = pos + len(sentence_end)
                        break
                
                end = best_break
            
            # Extract chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move to next chunk with overlap
            start = end - self.chunk_overlap
            
            # Avoid infinite loop
            if start <= 0 or end >= text_length:
                break
        
        logger.debug(f"Created {len(chunks)} chunks from text of length {text_length}")
        return chunks
    
    def chunk_documents(self, documents: List[dict]) -> List[dict]:
        """
        Chunk multiple documents
        
        Args:
            documents: List of document dicts with 'content', 'source', etc.
            
        Returns:
            List of chunked documents with metadata
        """
        all_chunks = []
        
        for doc in documents:
            content = doc.get('content', '')
            chunks = self.chunk_text(content)
            
            for idx, chunk in enumerate(chunks):
                chunk_doc = {
                    'content': chunk,
                    'source': doc.get('source', 'unknown'),
                    'chunk_index': idx,
                    'total_chunks': len(chunks),
                    'page_number': doc.get('page_number'),
                    'metadata': doc.get('metadata', {})
                }
                all_chunks.append(chunk_doc)
        
        logger.info(f"Chunked {len(documents)} documents into {len(all_chunks)} chunks")
        return all_chunks
