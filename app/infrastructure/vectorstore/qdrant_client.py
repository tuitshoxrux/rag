import logging
from typing import List, Dict
from qdrant_client import QdrantClient as QdrantClientLib
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from app.core.config import settings
import uuid

logger = logging.getLogger(__name__)


class QdrantClient:
    """Qdrant vector store client"""
    
    def __init__(self):
        self.client = QdrantClientLib(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure collection exists"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                # Create collection with 1536 dimensions (OpenAI embedding size)
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)  # YANGILANDI: 768 → 1536
                )
                logger.info(f"Created collection: {self.collection_name} (OpenAI: 1536 dims)")
            else:
                logger.info(f"Collection already exists: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Error ensuring collection: {str(e)}")
            raise
    
    async def add_documents(
        self, 
        texts: List[str], 
        embeddings: List[List[float]], 
        document_id: str
    ) -> int:
        """
        Add documents to vector store
        
        Args:
            texts: List of text chunks
            embeddings: List of embeddings
            document_id: Document identifier
            
        Returns:
            Number of documents added
        """
        try:
            points = []
            for idx, (text, embedding) in enumerate(zip(texts, embeddings)):
                point_id = str(uuid.uuid4())
                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "text": text,
                        "document_id": document_id,
                        "chunk_index": idx
                    }
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Added {len(points)} points to collection")
            return len(points)
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    async def search(
        self, 
        query_embedding: List[float], 
        top_k: int = None
    ) -> List[Dict]:
        """
        Search similar documents
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of search results with content and score
        """
        try:
            if top_k is None:
                top_k = settings.TOP_K_RESULTS
            
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k
            )
            
            results = []
            for hit in search_result:
                results.append({
                    "content": hit.payload.get("text", ""),
                    "score": hit.score,
                    "document_id": hit.payload.get("document_id", ""),
                    "chunk_index": hit.payload.get("chunk_index", 0)
                })
            
            logger.info(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            raise
    
    async def delete_by_document_id(self, document_id: str) -> bool:
        """
        Delete all points for a document
        
        Args:
            document_id: Document identifier
            
        Returns:
            Success status
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id)
                        )
                    ]
                )
            )
            logger.info(f"Deleted documents with id: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            return False