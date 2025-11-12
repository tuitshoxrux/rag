from abc import ABC, abstractmethod
from typing import Tuple


class IngestionService(ABC):
    """Interface for document ingestion"""
    
    @abstractmethod
    async def ingest_document(
        self, 
        file_path: str, 
        document_id: str
    ) -> Tuple[bool, int]:
        """
        Ingest document into system
        Returns: (success, chunks_count)
        """
        pass