from typing import List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["ok"])
    app_name: str = Field(..., examples=["FinSight API"])
    version: str = Field(..., examples=["0.1.0"])
    environment: str = Field(..., examples=["development"])


class DocumentInfo(BaseModel):
    document_name: str
    company: str
    ticker: str
    year: int
    chunk_count: int


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Financial research question about the indexed filings.",
        examples=["What supply chain risks does Apple highlight?"],
    )
    ticker: Optional[str] = Field(
        default=None,
        max_length=10,
        description="Optional company ticker filter (e.g., AAPL or MSFT).",
        examples=["AAPL"],
    )


class Citation(BaseModel):
    source_id: int
    document_name: str
    company: str
    ticker: str
    year: int
    section: str
    page_number: int
    similarity: float
    excerpt: str


class AskResponse(BaseModel):
    question: str
    answer: str
    route_used: str = Field(default="rag", description="Workflow path taken")
    insufficient_evidence: bool = False
    citations: List[Citation] = []
    disclaimer: str = (
        "Educational portfolio prototype only — not investment or financial advice."
    )
