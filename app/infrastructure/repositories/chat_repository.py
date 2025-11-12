import logging
from sqlalchemy.orm import Session
from typing import List, Optional
from app.domain.models import Chat

logger = logging.getLogger(__name__)


class ChatRepository:
    """Repository for Chat model"""
    
    async def create_chat(
        self,
        db: Session,
        question: str,
        answer: str,
        sources: Optional[List[dict]] = None
    ) -> Chat:
        """
        Create new chat record
        
        Args:
            db: Database session
            question: User question
            answer: AI answer
            sources: Source documents
            
        Returns:
            Created Chat object
        """
        try:
            chat = Chat(
                question=question,
                answer=answer,
                sources=sources
            )
            db.add(chat)
            db.commit()
            db.refresh(chat)
            
            logger.info(f"Created chat record with id: {chat.id}")
            return chat
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating chat: {str(e)}")
            raise
    
    async def get_chat_by_id(self, db: Session, chat_id: str) -> Optional[Chat]:
        """
        Get chat by ID
        
        Args:
            db: Database session
            chat_id: Chat ID
            
        Returns:
            Chat object or None
        """
        try:
            return db.query(Chat).filter(Chat.id == chat_id).first()
        except Exception as e:
            logger.error(f"Error getting chat: {str(e)}")
            raise
    
    async def get_recent_chats(self, db: Session, limit: int = 10) -> List[Chat]:
        """
        Get recent chats
        
        Args:
            db: Database session
            limit: Number of records to return
            
        Returns:
            List of Chat objects
        """
        try:
            return db.query(Chat).order_by(Chat.created_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting recent chats: {str(e)}")
            raise