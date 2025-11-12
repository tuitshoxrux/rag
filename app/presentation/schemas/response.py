from pydantic import BaseModel, Field
from typing import List


class SourceDocument(BaseModel):
    """Source document schema"""
    content: str = Field(..., description="Hujjat matni")
    score: float = Field(..., description="O'xshashlik darajasi")


class UploadResponse(BaseModel):
    """Upload response schema"""
    success: bool = Field(..., description="Muvaffaqiyat holati")
    message: str = Field(..., description="Xabar")
    document_id: str = Field(..., description="Hujjat identifikatori")
    chunks_count: int = Field(..., description="Yaratilgan bo'laklar soni")


class QueryResponse(BaseModel):
    """Query response schema"""
    success: bool = Field(..., description="Muvaffaqiyat holati")
    question: str = Field(..., description="Berilgan savol")
    answer: str = Field(..., description="Yaratilgan javob")
    sources: List[SourceDocument] = Field(..., description="Manba hujjatlar")