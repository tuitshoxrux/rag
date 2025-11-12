import logging
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAILLM:
    """OpenAI LLM client"""
    
    def __init__(self):
        try:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model_name = settings.OPENAI_LLM_MODEL
            logger.info(f"✅ OpenAI LLM configured: {self.model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to configure OpenAI LLM: {str(e)}")
            raise
    
    async def generate_answer(self, question: str, context: str) -> str:
        """
        Generate answer using OpenAI LLM
        
        Args:
            question: User question
            context: Context from retrieved documents
            
        Returns:
            Generated answer
        """
        try:
            logger.info(f"🔄 Generating answer with OpenAI...")
            
            messages = [
                {
                    "role": "system",
                    "content": "Siz yordam beruvchi AI assistantsiz. Berilgan kontekst asosida foydalanuvchi savoliga aniq va to'liq javob bering."
                },
                {
                    "role": "user",
                    "content": f"""Kontekst:
{context}

Savol: {question}

Javob:"""
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"✅ Successfully generated answer of length {len(answer)}")
            return answer
            
        except Exception as e:
            logger.error(f"❌ OPENAI LLM ERROR:")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            
            # Check for rate limit or quota errors
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ['rate_limit', 'quota', 'insufficient', '429']):
                logger.error("⚠️ OPENAI API LIMIT/QUOTA ERROR!")
                raise Exception(
                    "OpenAI API limiti yoki quota tugadi. Iltimos:\n"
                    "1. https://platform.openai.com/usage da balansni tekshiring\n"
                    "2. Bir necha daqiqa kuting"
                )
            
            raise Exception(f"OpenAI LLM xatoligi: {str(e)}")