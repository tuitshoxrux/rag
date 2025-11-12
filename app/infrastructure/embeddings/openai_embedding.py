import logging
from typing import List
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIEmbedding:
    """OpenAI embedding client"""
    
    def __init__(self):
        try:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model_name = settings.OPENAI_EMBEDDING_MODEL
            logger.info(f"✅ OpenAI configured with model: {self.model_name}")
            logger.info(f"✅ API Key: {settings.OPENAI_API_KEY[:20]}...")
        except Exception as e:
            logger.error(f"❌ Failed to configure OpenAI: {str(e)}")
            raise
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Embed single text using OpenAI
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding
        """
        try:
            logger.info(f"🔄 Generating embedding for text (length: {len(text)})...")
            
            # OpenAI embedding
            response = self.client.embeddings.create(
                model=self.model_name,
                input=text[:8000],  # OpenAI limit: 8191 tokens (~8000 chars)
                encoding_format="float"
            )
            
            embedding = response.data[0].embedding
            logger.info(f"✅ Successfully generated embedding of dimension {len(embedding)}")
            return embedding
            
        except Exception as e:
            logger.error(f"❌ OPENAI EMBEDDING ERROR:")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            
            # Check for rate limit or quota errors
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ['rate_limit', 'quota', 'insufficient', '429']):
                logger.error("⚠️ OPENAI API LIMIT/QUOTA ERROR!")
                raise Exception(
                    "OpenAI API limiti yoki quota tugadi. Iltimos:\n"
                    "1. https://platform.openai.com/usage da balansni tekshiring\n"
                    "2. Credit qo'shing: https://platform.openai.com/account/billing\n"
                    "3. Bir necha daqiqa kuting va qayta urinib ko'ring"
                )
            
            raise Exception(f"OpenAI embedding xatoligi: {str(e)}")
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple texts using OpenAI (batch processing)
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        try:
            logger.info(f"🔄 Generating embeddings for {len(texts)} texts...")
            
            # OpenAI supports batch processing (up to 2048 inputs)
            # We'll process in batches of 100 for safety
            all_embeddings = []
            batch_size = 100
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_num = i // batch_size + 1
                total_batches = (len(texts) + batch_size - 1) // batch_size
                
                logger.info(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch)} texts)")
                
                # Truncate texts to fit OpenAI limits
                truncated_batch = [text[:8000] for text in batch]
                
                # Batch embedding request
                response = self.client.embeddings.create(
                    model=self.model_name,
                    input=truncated_batch,
                    encoding_format="float"
                )
                
                # Extract embeddings
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                logger.info(f"✅ Batch {batch_num} completed")
            
            logger.info(f"✅ Successfully generated {len(all_embeddings)} embeddings")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"❌ Error in embed_texts: {str(e)}")
            raise