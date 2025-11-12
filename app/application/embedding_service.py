from abc import ABC, abstractmethod
from typing import List


class EmbeddingService(ABC):
    """Interface for embedding generation"""
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        pass
    
    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        pass