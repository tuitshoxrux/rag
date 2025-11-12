from abc import ABC, abstractmethod
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.domain.schemas import SourceDocument


class QueryService(ABC):
    """Interface for query processing"""
    
    @abstractmethod
    async def process_query(
        self, 
        question: str, 
        db: Session
    ) -> Tuple[str, List[SourceDocument]]:
        """
        Process user query
        Returns: (answer, sources)
        """
        pass