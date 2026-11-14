"""HTTP request and response schemas."""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2_000)
    top_k: int = Field(default=5, ge=1, le=20)


class Citation(BaseModel):
    document_id: str
    document_name: str
    chunk_id: str
    page: int | None = None
    score: float
    excerpt: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    retrieval_method: str
    grounded: bool


class IngestResponse(BaseModel):
    document_id: str
    filename: str
    chunks_created: int
    status: str


class EvaluationRequest(BaseModel):
    questions: list[dict] | None = None
    top_k: int = Field(default=5, ge=1, le=20)
