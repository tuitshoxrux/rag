from typing import List, Tuple
import logging
from sqlalchemy.orm import Session
from app.application.query_service import QueryService
from app.application.embedding_service import EmbeddingService
from app.application.vector_store import VectorStore
from app.infrastructure.llm.openai_llm import OpenAILLM  # YANGILANDI
from app.infrastructure.repositories.chat_repository import ChatRepository
from app.domain.schemas import SourceDocument

logger = logging.getLogger(__name__)


class QueryServiceImpl(QueryService):
    """Implementation of query processing service"""
    
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.llm = OpenAILLM()  # YANGILANDI
        self.chat_repo = ChatRepository()
    
    async def process_query(
        self, 
        question: str, 
        db: Session
    ) -> Tuple[str, List[SourceDocument]]:
        """
        Process user query
        
        Args:
            question: User question
            db: Database session
            
        Returns:
            Tuple of (answer, sources)
        """
        try:
            # 1. Generate question embedding
            logger.info(f"Processing query: {question}")
            question_embedding = await self.embedding_service.embed_text(question)
            
            # 2. Search similar documents
            search_results = await self.vector_store.search(question_embedding)
            
            if not search_results:
                logger.warning("No relevant documents found")
                return "Kechirasiz, bu savolga javob topilmadi. Iltimos, boshqa savol bering.", []
            
            # 3. Prepare context
            context = "\n\n".join([result['content'] for result in search_results])
            
            # 4. Generate answer using LLM
            answer = await self.llm.generate_answer(question, context)
            
            # 5. Prepare sources
            sources = [
                SourceDocument(
                    content=result['content'],
                    score=result['score']
                )
                for result in search_results
            ]
            
            # 6. Save to database
            await self.chat_repo.create_chat(
                db=db,
                question=question,
                answer=answer,
                sources=[s.dict() for s in sources]
            )
            
            logger.info(f"Successfully processed query")
            return answer, sources
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise