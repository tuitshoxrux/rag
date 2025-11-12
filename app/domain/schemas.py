from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid


class ChatBase(BaseModel):
    """Base chat schema"""
    question: str
    answer: str
    sources: Optional[List[dict]] = None


class ChatCreate(ChatBase):
    """Chat creation schema"""
    pass


class ChatResponse(ChatBase):
    """Chat response schema"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SourceDocument(BaseModel):
    """Source document schema"""
    content: str = Field(..., description="Document content")
    score: float = Field(..., description="Relevance score")


class QueryRequest(BaseModel):
    """Query request schema"""
    question: str = Field(..., min_length=1, max_length=1000, description="Question to ask")


class QueryResponse(BaseModel):
    """Query response schema"""
    success: bool
    question: str
    answer: str
    sources: List[SourceDocument]


class UploadResponse(BaseModel):
    """Upload response schema"""
    success: bool
    message: str
    document_id: str
    chunks_count: int