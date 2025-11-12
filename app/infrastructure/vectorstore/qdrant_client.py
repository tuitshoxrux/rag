import logging
from typing import List, Dict, Optional
from qdrant_client import QdrantClient as QdrantClientLib
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from app.core.config import settings
import uuid

logger = logging.getLogger(__name__)


class QdrantClient:
    """Qdrant vector store client with support for both local and cloud deployments"""
    
    def __init__(self):
        """Initialize Qdrant client based on available configuration"""
        try:
            # Priority 1: Use QDRANT_URL if available (Qdrant Cloud)
            if settings.QDRANT_URL:
                logger.info(f"🌐 Connecting to Qdrant Cloud: {settings.QDRANT_URL}")
                self.client = QdrantClientLib(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY,
                    timeout=60,
                    prefer_grpc=False,  # Use REST API for cloud
                    https=True  # Ensure HTTPS for cloud
                )
                logger.info("✅ Connected to Qdrant Cloud")
            
            # Priority 2: Use host:port (local/self-hosted)
            else:
                logger.info(f"🔌 Connecting to local Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
                self.client = QdrantClientLib(
                    host=settings.QDRANT_HOST,
                    port=settings.QDRANT_PORT,
                    timeout=60
                )
                logger.info("✅ Connected to local Qdrant")
            
            self.collection_name = settings.QDRANT_COLLECTION_NAME
            self._ensure_collection()
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Qdrant client: {str(e)}")
            raise
    
    def _ensure_collection(self):
        """Ensure collection exists, create if not"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"📦 Creating collection: {self.collection_name}")
                
                # Create collection with 1536 dimensions (text-embedding-3-small)
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=1536,  # OpenAI text-embedding-3-small dimension
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Collection '{self.collection_name}' created successfully (1536 dimensions)")
            else:
                logger.info(f"✅ Collection '{self.collection_name}' already exists")
                
        except Exception as e:
            logger.error(f"❌ Error ensuring collection: {str(e)}")
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
            embeddings: List of embeddings (1536 dimensions each)
            document_id: Document identifier
            
        Returns:
            Number of documents added
        """
        try:
            if not texts or not embeddings:
                logger.warning("No texts or embeddings provided")
                return 0
            
            if len(texts) != len(embeddings):
                raise ValueError(f"Texts ({len(texts)}) and embeddings ({len(embeddings)}) length mismatch")
            
            points = []
            for idx, (text, embedding) in enumerate(zip(texts, embeddings)):
                # Validate embedding dimension
                if len(embedding) != 1536:
                    logger.error(f"Invalid embedding dimension: {len(embedding)}, expected 1536")
                    continue
                
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
            
            if not points:
                logger.error("No valid points to insert")
                return 0
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"✅ Added {len(points)} points to collection '{self.collection_name}'")
            return len(points)
            
        except Exception as e:
            logger.error(f"❌ Error adding documents: {str(e)}")
            raise
    
    async def search(
        self, 
        query_embedding: List[float], 
        top_k: Optional[int] = None
    ) -> List[Dict]:
        """
        Search similar documents
        
        Args:
            query_embedding: Query embedding vector (1536 dimensions)
            top_k: Number of results to return (defaults to settings.TOP_K_RESULTS)
            
        Returns:
            List of search results with content and score
        """
        try:
            if top_k is None:
                top_k = settings.TOP_K_RESULTS
            
            # Validate query embedding dimension
            if len(query_embedding) != 1536:
                raise ValueError(f"Invalid query embedding dimension: {len(query_embedding)}, expected 1536")
            
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
            
            logger.info(f"🔍 Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching documents: {str(e)}")
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
            logger.info(f"🗑️ Deleted documents with id: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting documents: {str(e)}")
            return False
    
    def get_collection_info(self) -> Dict:
        """Get collection information"""
        try:
            info = self.client.get_collection(collection_name=self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            logger.error(f"❌ Error getting collection info: {str(e)}")
            return {}