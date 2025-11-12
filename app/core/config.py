from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "RAG Word Service"
    APP_VERSION: str = "1.0.0"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # OpenAI API
    OPENAI_API_KEY: str
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_LLM_MODEL: str = "gpt-4o-mini"
    
    # PostgreSQL - Support both individual vars and DATABASE_URL
    DATABASE_URL: Optional[str] = None
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "rag_user"
    POSTGRES_PASSWORD: str = "rag_password"
    POSTGRES_DB: str = "rag_database"
    
    # Qdrant - Support both host-based and URL-based (cloud)
    QDRANT_URL: Optional[str] = None  # NEW: For Qdrant Cloud
    QDRANT_API_KEY: Optional[str] = None  # NEW: For Qdrant Cloud
    QDRANT_HOST: str = "localhost"  # Fallback for local
    QDRANT_PORT: int = 6333  # Fallback for local
    QDRANT_COLLECTION_NAME: str = "documents"
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: str = ".docx,.doc"
    
    # RAG Settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RESULTS: int = 3
    
    # LLM Settings
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1000
    
    @property
    def database_url(self) -> str:
        """Get database URL - prefer DATABASE_URL if available"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def ALLOWED_EXTENSIONS_LIST(self) -> List[str]:
        """Get list of allowed extensions"""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    @property
    def MAX_FILE_SIZE_BYTES(self) -> int:
        """Get max file size in bytes"""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    @property
    def is_qdrant_cloud(self) -> bool:
        """Check if using Qdrant Cloud"""
        return self.QDRANT_URL is not None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()