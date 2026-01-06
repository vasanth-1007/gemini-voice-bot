"""
Vector store module using ChromaDB for semantic search
"""
from typing import List, Dict, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from loguru import logger


class VectorStore:
    """Manage vector embeddings and similarity search using ChromaDB"""
    
    def __init__(
        self,
        persist_directory: Path,
        collection_name: str = "sop_documents",
        embedding_function=None
    ):
        """
        Initialize vector store
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection
            embedding_function: Custom embedding function (optional)
        """
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        
        # Create persist directory if it doesn't exist
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        if embedding_function:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=embedding_function
            )
        else:
            # Use default embedding function
            self.collection = self.client.get_or_create_collection(
                name=collection_name
            )
        
        logger.info(f"Initialized VectorStore: {collection_name} at {persist_directory}")
    
    def add_documents(self, documents: List[Dict]) -> None:
        """
        Add documents to vector store
        
        Args:
            documents: List of document dicts with 'content', 'source', etc.
        """
        if not documents:
            logger.warning("No documents to add")
            return
        
        # Prepare data for ChromaDB
        ids = []
        contents = []
        metadatas = []
        
        for idx, doc in enumerate(documents):
            doc_id = f"{doc.get('source', 'unknown')}_{idx}"
            ids.append(doc_id)
            contents.append(doc['content'])
            
            # Prepare metadata (ChromaDB doesn't support nested dicts)
            metadata = {
                'source': str(doc.get('source', 'unknown')),
                'chunk_index': doc.get('chunk_index', 0),
                'total_chunks': doc.get('total_chunks', 1),
            }
            
            if doc.get('page_number'):
                metadata['page_number'] = doc['page_number']
            
            metadatas.append(metadata)
        
        # Add to collection
        try:
            self.collection.add(
                ids=ids,
                documents=contents,
                metadatas=metadatas
            )
            logger.info(f"Added {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def search(
        self,
        query: str,
        top_k: int = 3,
        similarity_threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score (optional)
            
        Returns:
            List of matching documents with scores
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            # Format results
            matched_docs = []
            
            if results['documents'] and results['documents'][0]:
                for idx in range(len(results['documents'][0])):
                    # Calculate similarity (ChromaDB returns distance, convert to similarity)
                    distance = results['distances'][0][idx] if results.get('distances') else 0
                    similarity = 1 / (1 + distance)  # Convert distance to similarity
                    
                    # Apply threshold if specified
                    if similarity_threshold and similarity < similarity_threshold:
                        continue
                    
                    doc = {
                        'content': results['documents'][0][idx],
                        'metadata': results['metadatas'][0][idx] if results.get('metadatas') else {},
                        'similarity': similarity,
                        'distance': distance
                    }
                    matched_docs.append(doc)
            
            logger.info(f"Found {len(matched_docs)} matching documents for query")
            return matched_docs
        
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        count = self.collection.count()
        
        return {
            'collection_name': self.collection_name,
            'document_count': count,
            'persist_directory': str(self.persist_directory)
        }
    
    def clear_collection(self) -> None:
        """Clear all documents from collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(name=self.collection_name)
            logger.info(f"Cleared collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise
    
    def rebuild_index(self, documents: List[Dict]) -> None:
        """
        Rebuild the entire index with new documents
        
        Args:
            documents: List of documents to index
        """
        logger.info("Rebuilding vector index...")
        self.clear_collection()
        self.add_documents(documents)
        logger.info("Index rebuild complete")
