from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging
import traceback
from app.core.database import get_db
from app.application.impl.embedding_service_impl import EmbeddingServiceImpl
from app.application.impl.vector_store_impl import VectorStoreImpl
from app.application.impl.query_service_impl import QueryServiceImpl
from app.domain.schemas import QueryRequest, QueryResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """
    Query uploaded documents
    
    - **question**: Question to ask about uploaded documents
    """
    try:
        logger.info(f"Received query: {request.question}")
        
        if not request.question or not request.question.strip():
            logger.warning("Empty question received")
            raise HTTPException(
                status_code=400,
                detail="Savol bo'sh bo'lmasligi kerak"
            )
        
        # Initialize services
        logger.info("Initializing query services...")
        embedding_service = EmbeddingServiceImpl()
        vector_store = VectorStoreImpl()
        
        query_service = QueryServiceImpl(
            embedding_service=embedding_service,
            vector_store=vector_store
        )
        logger.info("Query services initialized")
        
        # Process query
        logger.info("Processing query...")
        answer, sources = await query_service.process_query(
            question=request.question,
            db=db
        )
        logger.info(f"Query processed successfully, found {len(sources)} sources")
        
        return QueryResponse(
            success=True,
            question=request.question,
            answer=answer,
            sources=sources
        )
        
    except HTTPException as he:
        logger.error(f"HTTP Exception: {he.detail}")
        raise
        
    except Exception as e:
        logger.error(f"CRITICAL ERROR in query_documents:")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Savolni qayta ishlashda xatolik: {str(e)}"
        )