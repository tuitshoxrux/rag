from abc import ABC, abstractmethod
from typing import List, Dict


class VectorStore(ABC):
    """Interface for vector store operations"""
    
    @abstractmethod
    async def add_documents(
        self, 
        texts: List[str], 
        embeddings: List[List[float]], 
        document_id: str
    ) -> int:
        """Add documents to vector store"""
        pass
    
    @abstractmethod
    async def search(
        self, 
        query_embedding: List[float], 
        top_k: int = None
    ) -> List[Dict]:
        """Search similar documents"""
        pass
    
    @abstractmethod
    async def delete_by_document_id(self, document_id: str) -> bool:
        """Delete documents by document ID"""
        pass