from typing import List
import logging
from app.application.embedding_service import EmbeddingService
from app.infrastructure.embeddings.openai_embedding import OpenAIEmbedding  # YANGILANDI

logger = logging.getLogger(__name__)


class EmbeddingServiceImpl(EmbeddingService):
    """Implementation of embedding service"""
    
    def __init__(self):
        self.embedding_client = OpenAIEmbedding()  # YANGILANDI
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            embedding = await self.embedding_client.embed_text(text)
            logger.info(f"Successfully embedded text of length {len(text)}")
            return embedding
        except Exception as e:
            logger.error(f"Error embedding text: {str(e)}")
            raise
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = await self.embedding_client.embed_texts(texts)
            logger.info(f"Successfully embedded {len(texts)} texts")
            return embeddings
        except Exception as e:
            logger.error(f"Error embedding texts: {str(e)}")
            raise