from pydantic import BaseModel, Field


class UploadRequest(BaseModel):
    """Upload request schema"""
    pass  # File is handled by FastAPI's UploadFile


class QueryRequest(BaseModel):
    """Query request schema"""
    question: str = Field(
        ..., 
        min_length=1, 
        max_length=1000,
        description="Savol matni",
        example="Hujjatda nima haqida yozilgan?"
    )