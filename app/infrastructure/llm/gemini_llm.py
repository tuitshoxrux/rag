import logging
import google.generativeai as genai
from app.core.config import settings
import time

logger = logging.getLogger(__name__)


class GeminiLLM:
    """Google Gemini LLM client"""
    
    def __init__(self):
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_LLM_MODEL)
            self.generation_config = {
                "temperature": settings.LLM_TEMPERATURE,
                "max_output_tokens": settings.LLM_MAX_TOKENS,
            }
            logger.info(f"Gemini LLM configured: {settings.GEMINI_LLM_MODEL}")
        except Exception as e:
            logger.error(f"Failed to configure Gemini LLM: {str(e)}")
            raise
    
    async def generate_answer(self, question: str, context: str) -> str:
        """
        Generate answer using Gemini LLM
        
        Args:
            question: User question
            context: Context from retrieved documents
            
        Returns:
            Generated answer
        """
        try:
            logger.info(f"Generating answer with Gemini...")
            prompt = self._create_prompt(question, context)
            
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            answer = response.text.strip()
            logger.info(f"Successfully generated answer of length {len(answer)}")
            return answer
            
        except Exception as e:
            logger.error(f"GEMINI LLM ERROR:")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            
            # Check if it's a quota/limit error
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ['quota', 'limit', 'rate', 'exhausted', '429']):
                logger.error("GEMINI API LIMIT REACHED!")
                raise Exception(
                    "Gemini API limiti tugadi. Iltimos, bir oz kuting va qayta urinib ko'ring."
                )
            
            raise Exception(f"Gemini LLM xatoligi: {str(e)}")
    
    def _create_prompt(self, question: str, context: str) -> str:
        """
        Create prompt for LLM
        
        Args:
            question: User question
            context: Context from documents
            
        Returns:
            Formatted prompt
        """
        prompt = f"""Siz yordam beruvchi AI assistantsiz. Berilgan kontekst asosida foydalanuvchi savoliga aniq va to'liq javob bering.

Kontekst:
{context}

Savol: {question}

Javob:"""
        
        return prompt