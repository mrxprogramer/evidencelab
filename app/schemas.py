"""HTTP request and response schemas."""

from pydantic import BaseModel, Field, field_validator


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2_000)
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("question")
    @classmethod
    def question_must_contain_text(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Question must contain at least 3 non-whitespace characters")
        return value


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


class EvaluationQuestion(BaseModel):
    question: str = Field(min_length=3, max_length=2_000)
    relevant_chunk_ids: list[str] = Field(default_factory=list)

    @field_validator("question")
    @classmethod
    def question_must_contain_text(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Question must contain at least 3 non-whitespace characters")
        return value

    @field_validator("relevant_chunk_ids")
    @classmethod
    def chunk_ids_must_be_nonempty(cls, value: list[str]) -> list[str]:
        cleaned = [chunk_id.strip() for chunk_id in value]
        if any(not chunk_id for chunk_id in cleaned):
            raise ValueError("Relevant chunk IDs must not be empty")
        return cleaned


class EvaluationRequest(BaseModel):
    questions: list[EvaluationQuestion] | None = None
    top_k: int = Field(default=5, ge=1, le=20)
