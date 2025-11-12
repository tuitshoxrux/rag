import logging
from typing import List
import google.generativeai as genai
from app.core.config import settings
import time
import asyncio

logger = logging.getLogger(__name__)


class GeminiEmbedding:
    """Google Gemini embedding client with rate limiting"""
    
    def __init__(self):
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model_name = settings.GEMINI_EMBEDDING_MODEL
            logger.info(f"✅ Gemini configured with model: {self.model_name}")
            logger.info(f"✅ API Key: {settings.GEMINI_API_KEY[:20]}...")
        except Exception as e:
            logger.error(f"❌ Failed to configure Gemini: {str(e)}")
            raise
    
    async def embed_text(self, text: str, retry_count: int = 3) -> List[float]:
        """
        Embed single text using Gemini with retry logic
        
        Args:
            text: Text to embed
            retry_count: Number of retries on failure
            
        Returns:
            List of floats representing the embedding
        """
        for attempt in range(retry_count):
            try:
                logger.info(f"🔄 Generating embedding (attempt {attempt + 1}/{retry_count})...")
                
                result = genai.embed_content(
                    model=self.model_name,
                    content=text[:2000],  # Limit text length to 2000 chars
                    task_type="retrieval_document"
                )
                
                embedding = result['embedding']
                logger.info(f"✅ Successfully generated embedding of dimension {len(embedding)}")
                return embedding
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Check for quota/rate limit errors
                if any(keyword in error_str for keyword in ['quota', 'limit', 'rate', 'exhausted', '429']):
                    logger.error(f"⚠️ Rate limit hit on attempt {attempt + 1}")
                    
                    if attempt < retry_count - 1:
                        wait_time = (2 ** attempt) * 5  # Exponential backoff: 5, 10, 20 seconds
                        logger.info(f"⏳ Waiting {wait_time} seconds before retry...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error("❌ GEMINI API LIMIT REACHED after all retries!")
                        raise Exception(
                            "Gemini API limiti tugadi. Iltimos:\n"
                            "1. Bir necha daqiqa kuting\n"
                            "2. Yangi API key yarating: https://makersuite.google.com/app/apikey\n"
                            "3. Yoki to'lov rejasiga o'ting: https://ai.google.dev/pricing"
                        )
                else:
                    logger.error(f"❌ Gemini error: {str(e)}")
                    raise Exception(f"Gemini embedding xatoligi: {str(e)}")
        
        raise Exception("Failed to generate embedding after all retries")
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple texts with rate limiting
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        try:
            logger.info(f"🔄 Generating embeddings for {len(texts)} texts...")
            embeddings = []
            
            # Process in small batches to avoid rate limits
            batch_size = 5  # Process 5 at a time
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_num = i // batch_size + 1
                total_batches = (len(texts) + batch_size - 1) // batch_size
                
                logger.info(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch)} texts)")
                
                for j, text in enumerate(batch):
                    text_num = i + j + 1
                    logger.info(f"Processing text {text_num}/{len(texts)}...")
                    
                    embedding = await self.embed_text(text)
                    embeddings.append(embedding)
                    
                    # Delay between requests to avoid rate limits
                    if text_num < len(texts):
                        await asyncio.sleep(2)  # 2 second delay between each request
                
                # Longer delay between batches
                if i + batch_size < len(texts):
                    logger.info(f"⏳ Batch {batch_num} complete. Waiting 10 seconds before next batch...")
                    await asyncio.sleep(10)
            
            logger.info(f"✅ Successfully generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ Error in embed_texts: {str(e)}")
            raise