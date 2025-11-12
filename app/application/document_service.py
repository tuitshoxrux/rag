from abc import ABC, abstractmethod
from typing import List


class DocumentService(ABC):
    """Interface for document text processing"""
    
    @abstractmethod
    async def extract_text_from_word(self, file_path: str) -> str:
        """Extract text from Word document"""
        pass
    
    @abstractmethod
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        pass