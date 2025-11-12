from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from app.core.database import Base


class Chat(Base):
    """Chat model for storing questions and answers"""
    
    __tablename__ = "chat"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question = Column(Text, nullable=False, comment="User question")
    answer = Column(Text, nullable=False, comment="AI generated answer")
    sources = Column(JSONB, nullable=True, comment="Source documents used")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Chat(id={self.id}, question={self.question[:50]}...)>"