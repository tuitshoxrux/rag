from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "RAG Word Service"
    APP_VERSION: str = "1.0.0"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True
    
    # OpenAI API (YANGI)
    OPENAI_API_KEY: str
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_LLM_MODEL: str = "gpt-4o-mini"
    
    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 8088
    POSTGRES_USER: str = "rag_user"
    POSTGRES_PASSWORD: str = "rag_password"
    POSTGRES_DB: str = "rag_database"
    
    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "documents"
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: str = ".docx"
    
    # RAG Settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 100
    TOP_K_RESULTS: int = 3
    
    # LLM Settings
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1000
    
    @property
    def DATABASE_URL(self) -> str:
        """Get database URL"""
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()