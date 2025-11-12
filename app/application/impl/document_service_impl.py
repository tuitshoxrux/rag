from typing import List
import logging
from app.application.document_service import DocumentService
from app.application.file_extractor import FileExtractor
from app.core.config import settings

logger = logging.getLogger(__name__)


class DocumentServiceImpl(DocumentService):
    """Implementation of document processing service"""
    
    def __init__(self, file_extractor: FileExtractor):
        self.extractor = file_extractor
    
    async def extract_text_from_word(self, file_path: str) -> str:
        """
        Extract text from Word document
        
        Args:
            file_path: Path to Word file
            
        Returns:
            Extracted text
        """
        try:
            text = await self.extractor.extract_text(file_path)
            logger.info(f"Successfully extracted text from {file_path}")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            raise
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        chunk_size = settings.CHUNK_SIZE
        chunk_overlap = settings.CHUNK_OVERLAP
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            
            # Find last sentence boundary if not at end
            if end < text_length:
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                boundary = max(last_period, last_newline)
                
                if boundary > chunk_size * 0.5:
                    end = start + boundary + 1
                    chunk = text[start:end]
            
            chunks.append(chunk.strip())
            start = end - chunk_overlap
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks