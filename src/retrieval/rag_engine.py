"""
RAG (Retrieval Augmented Generation) Engine
Combines document retrieval with LLM generation
"""
from typing import List, Dict, Optional
from loguru import logger
from .vector_store import VectorStore
from .text_chunker import TextChunker


class RAGEngine:
    """Orchestrates retrieval and generation for SOP-based answers"""
    
    def __init__(
        self,
        vector_store: VectorStore,
        top_k: int = 3,
        similarity_threshold: float = 0.7
    ):
        """
        Initialize RAG engine
        
        Args:
            vector_store: VectorStore instance for retrieval
            top_k: Number of documents to retrieve
            similarity_threshold: Minimum similarity for relevance
        """
        self.vector_store = vector_store
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        
        logger.info(f"Initialized RAGEngine: top_k={top_k}, threshold={similarity_threshold}")
    
    def retrieve_context(self, query: str) -> Dict:
        """
        Retrieve relevant context for a query
        
        Args:
            query: User query
            
        Returns:
            Dict with retrieved documents and metadata
        """
        # Search vector store
        results = self.vector_store.search(
            query=query,
            top_k=self.top_k,
            similarity_threshold=self.similarity_threshold
        )
        
        if not results:
            logger.info(f"No relevant documents found for query: {query[:50]}...")
            return {
                'found': False,
                'documents': [],
                'context': '',
                'sources': []
            }
        
        # Extract context and sources
        context_parts = []
        sources = set()
        
        for doc in results:
            context_parts.append(doc['content'])
            source = doc['metadata'].get('source', 'Unknown')
            sources.add(source)
            
            # Log page number if available
            page_num = doc['metadata'].get('page_number')
            if page_num:
                logger.debug(f"Retrieved from {source}, page {page_num}")
        
        # Combine context
        combined_context = "\n\n".join(context_parts)
        
        logger.info(f"Retrieved {len(results)} relevant documents from {len(sources)} sources")
        
        return {
            'found': True,
            'documents': results,
            'context': combined_context,
            'sources': list(sources)
        }
    
    def format_prompt_with_context(self, query: str, context: str) -> str:
        """
        Format a prompt with retrieved context
        
        Args:
            query: User query
            context: Retrieved context
            
        Returns:
            Formatted prompt
        """
        prompt = f"""You are a helpful assistant that answers questions based ONLY on the provided SOP (Standard Operating Procedure) documents.

IMPORTANT INSTRUCTIONS:
1. Answer ONLY using information from the SOP context below
2. Respond in Tanglish (Tamil written in English letters)
3. Be clear, professional, and conversational
4. If the answer is not in the SOP context, say: "Indha question ku SOP la information illa."
5. Do NOT use any external knowledge or make assumptions

SOP CONTEXT:
{context}

USER QUESTION: {query}

Please provide your answer in Tanglish:"""
        
        return prompt
    
    def format_no_context_response(self) -> str:
        """Format response when no relevant context is found"""
        return "Indha question ku SOP la information illa."
    
    def get_retrieval_stats(self) -> Dict:
        """Get statistics about the retrieval system"""
        vector_stats = self.vector_store.get_collection_stats()
        
        return {
            **vector_stats,
            'top_k': self.top_k,
            'similarity_threshold': self.similarity_threshold
        }
