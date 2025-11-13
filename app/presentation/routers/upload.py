from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import uuid
import logging
import traceback
import asyncio
from typing import List
from app.core.config import settings
from app.core.database import get_db
from app.application.impl.word_extractor_impl import WordExtractorImpl
from app.application.impl.document_service_impl import DocumentServiceImpl
from app.application.impl.embedding_service_impl import EmbeddingServiceImpl
from app.application.impl.vector_store_impl import VectorStoreImpl
from app.application.impl.ingestion_service_impl import IngestionServiceImpl
from app.domain.schemas import UploadResponse, BatchUploadResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def process_single_file(
    file: UploadFile,
    db: Session
) -> dict:
    """Process a single file and return result"""
    file_path = None
    
    try:
        logger.info(f"Processing file: {file.filename}")
        
        # Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in settings.ALLOWED_EXTENSIONS_LIST:
            return {
                "filename": file.filename,
                "success": False,
                "error": f"Invalid file type: {file_ext}",
                "document_id": None,
                "chunks_count": 0
            }
        
        # Read file
        contents = await file.read()
        file_size = len(contents)
        
        # Validate file size
        if file_size > settings.MAX_FILE_SIZE_BYTES:
            return {
                "filename": file.filename,
                "success": False,
                "error": f"File too large: {file_size} bytes",
                "document_id": None,
                "chunks_count": 0
            }
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Save file temporarily
        file_path = os.path.join(UPLOAD_DIR, f"{document_id}{file_ext}")
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Initialize services
        word_extractor = WordExtractorImpl()
        document_service = DocumentServiceImpl(word_extractor)
        embedding_service = EmbeddingServiceImpl()
        vector_store = VectorStoreImpl()
        
        ingestion_service = IngestionServiceImpl(
            document_service=document_service,
            embedding_service=embedding_service,
            vector_store=vector_store
        )
        
        # Process document
        success, chunks_count = await ingestion_service.ingest_document(
            file_path=file_path,
            document_id=document_id
        )
        
        # Clean up temporary file
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.warning(f"Could not remove temporary file: {str(e)}")
        
        return {
            "filename": file.filename,
            "success": success,
            "error": None,
            "document_id": document_id,
            "chunks_count": chunks_count
        }
        
    except Exception as e:
        logger.error(f"Error processing {file.filename}: {str(e)}")
        
        # Clean up file if exists
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup file: {str(cleanup_error)}")
        
        return {
            "filename": file.filename,
            "success": False,
            "error": str(e),
            "document_id": None,
            "chunks_count": 0
        }


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload single Word document and process it
    
    - **file**: Word document file (.docx, .doc)
    """
    result = await process_single_file(file, db)
    
    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result["error"] or "Failed to process document"
        )
    
    return UploadResponse(
        success=True,
        message="Fayl muvaffaqiyatli yuklandi va qayta ishlandi",
        document_id=result["document_id"],
        chunks_count=result["chunks_count"]
    )


@router.post("/upload/batch", response_model=BatchUploadResponse)
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload multiple Word documents and process them
    
    - **files**: List of Word document files (.docx, .doc)
    """
    if not files or len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="No files provided"
        )
    
    logger.info(f"Starting batch upload of {len(files)} files")
    
    # Process all files concurrently
    tasks = [process_single_file(file, db) for file in files]
    results = await asyncio.gather(*tasks)
    
    # Separate successful and failed uploads
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    total_chunks = sum(r["chunks_count"] for r in successful)
    
    logger.info(f"Batch upload complete: {len(successful)} successful, {len(failed)} failed")
    
    return BatchUploadResponse(
        success=len(successful) > 0,
        message=f"Processed {len(successful)}/{len(files)} files successfully",
        total_files=len(files),
        successful_uploads=len(successful),
        failed_uploads=len(failed),
        total_chunks=total_chunks,
        results=results
    )