from typing import List, Dict
import logging
from app.application.vector_store import VectorStore
from app.infrastructure.vectorstore.qdrant_client import QdrantClient as QdrantClientInfra

logger = logging.getLogger(__name__)


class VectorStoreImpl(VectorStore):
    """Implementation of vector store service"""
    
    def __init__(self):
        self.client = QdrantClientInfra()
    
    async def add_documents(
        self, 
        texts: List[str], 
        embeddings: List[List[float]], 
        document_id: str
    ) -> int:
        """
        Add documents to vector store
        
        Args:
            texts: List of text chunks
            embeddings: List of embeddings
            document_id: Document identifier
            
        Returns:
            Number of documents added
        """
        try:
            count = await self.client.add_documents(texts, embeddings, document_id)
            logger.info(f"Added {count} documents to vector store")
            return count
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    async def search(
        self, 
        query_embedding: List[float], 
        top_k: int = None
    ) -> List[Dict]:
        """
        Search similar documents
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results
            
        Returns:
            List of search results
        """
        try:
            results = await self.client.search(query_embedding, top_k)
            logger.info(f"Found {len(results)} similar documents")
            return results
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            raise
    
    async def delete_by_document_id(self, document_id: str) -> bool:
        """
        Delete documents by document ID
        
        Args:
            document_id: Document identifier
            
        Returns:
            Success status
        """
        try:
            success = await self.client.delete_by_document_id(document_id)
            logger.info(f"Deleted documents for {document_id}: {success}")
            return success
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            return False