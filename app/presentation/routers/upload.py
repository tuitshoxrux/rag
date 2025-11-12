from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import uuid
import logging
import traceback
from app.core.config import settings
from app.core.database import get_db
from app.application.impl.word_extractor_impl import WordExtractorImpl
from app.application.impl.document_service_impl import DocumentServiceImpl
from app.application.impl.embedding_service_impl import EmbeddingServiceImpl
from app.application.impl.vector_store_impl import VectorStoreImpl
from app.application.impl.ingestion_service_impl import IngestionServiceImpl
from app.domain.schemas import UploadResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload Word document and process it
    
    - **file**: Word document file (.docx only)
    """
    file_path = None
    
    try:
        logger.info(f"Starting upload process for file: {file.filename}")
        
        # Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        logger.info(f"File extension: {file_ext}")
        
        if file_ext not in settings.ALLOWED_EXTENSIONS_LIST:
            logger.warning(f"Invalid file extension: {file_ext}")
            raise HTTPException(
                status_code=400,
                detail=f"Faqat {', '.join(settings.ALLOWED_EXTENSIONS_LIST)} formatdagi fayllar qabul qilinadi"
            )
        
        # Read file
        contents = await file.read()
        file_size = len(contents)
        logger.info(f"File size: {file_size} bytes")
        
        # Validate file size
        if file_size > settings.MAX_FILE_SIZE_BYTES:
            logger.warning(f"File too large: {file_size} bytes")
            raise HTTPException(
                status_code=400,
                detail=f"Fayl hajmi {settings.MAX_FILE_SIZE_MB}MB dan oshmasligi kerak"
            )
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        logger.info(f"Generated document ID: {document_id}")
        
        # Save file temporarily
        file_path = os.path.join(UPLOAD_DIR, f"{document_id}{file_ext}")
        with open(file_path, "wb") as f:
            f.write(contents)
        
        logger.info(f"File saved: {file_path}")
        
        # Initialize services
        logger.info("Initializing services...")
        word_extractor = WordExtractorImpl()
        document_service = DocumentServiceImpl(word_extractor)
        embedding_service = EmbeddingServiceImpl()
        vector_store = VectorStoreImpl()
        
        ingestion_service = IngestionServiceImpl(
            document_service=document_service,
            embedding_service=embedding_service,
            vector_store=vector_store
        )
        logger.info("Services initialized")
        
        # Process document
        logger.info("Starting document processing...")
        success, chunks_count = await ingestion_service.ingest_document(
            file_path=file_path,
            document_id=document_id
        )
        logger.info(f"Document processed: {chunks_count} chunks created")
        
        # Clean up temporary file
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Could not remove temporary file: {str(e)}")
        
        return UploadResponse(
            success=success,
            message="Fayl muvaffaqiyatli yuklandi va qayta ishlandi",
            document_id=document_id,
            chunks_count=chunks_count
        )
        
    except HTTPException as he:
        logger.error(f"HTTP Exception: {he.detail}")
        raise
        
    except Exception as e:
        logger.error(f"CRITICAL ERROR in upload_document:")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        
        # Clean up file if exists
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"🗑️ Cleaned up file after error: {file_path}")
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup file: {str(cleanup_error)}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Faylni qayta ishlashda xatolik: {str(e)}"
        )