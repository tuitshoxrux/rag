from abc import ABC, abstractmethod


class FileExtractor(ABC):
    """Interface for file text extraction"""
    
    @abstractmethod
    async def extract_text(self, file_path: str) -> str:
        """Extract text from file"""
        pass