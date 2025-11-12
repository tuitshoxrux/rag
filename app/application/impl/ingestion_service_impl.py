from typing import Tuple
import logging
from app.application.ingestion_service import IngestionService
from app.application.document_service import DocumentService
from app.application.embedding_service import EmbeddingService
from app.application.vector_store import VectorStore

logger = logging.getLogger(__name__)


class IngestionServiceImpl(IngestionService):
    """Implementation of document ingestion service"""
    
    def __init__(
        self,
        document_service: DocumentService,
        embedding_service: EmbeddingService,
        vector_store: VectorStore
    ):
        self.document_service = document_service
        self.embedding_service = embedding_service
        self.vector_store = vector_store
    
    async def ingest_document(
        self, 
        file_path: str, 
        document_id: str
    ) -> Tuple[bool, int]:
        """
        Ingest document into system
        
        Args:
            file_path: Path to document file
            document_id: Document identifier
            
        Returns:
            Tuple of (success, chunks_count)
        """
        try:
            # 1. Extract text
            logger.info(f"Extracting text from {file_path}")
            text = await self.document_service.extract_text_from_word(file_path)
            
            # 2. Chunk text
            logger.info(f"Chunking text")
            chunks = self.document_service.chunk_text(text)
            
            if not chunks:
                raise ValueError("No chunks created from document")
            
            # 3. Generate embeddings
            logger.info(f"Generating embeddings for {len(chunks)} chunks")
            embeddings = await self.embedding_service.embed_texts(chunks)
            
            # 4. Store in vector database
            logger.info(f"Storing in vector database")
            stored_count = await self.vector_store.add_documents(
                texts=chunks,
                embeddings=embeddings,
                document_id=document_id
            )
            
            logger.info(f"Successfully ingested document {document_id} with {stored_count} chunks")
            return True, stored_count
            
        except Exception as e:
            logger.error(f"Error ingesting document: {str(e)}")
            raise