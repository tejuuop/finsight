from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.config import settings
from app.db import list_indexed_documents
from app.graph import run_workflow
from app.schemas import AskRequest, AskResponse, DocumentInfo, HealthResponse

FRONTEND_HTML = Path(__file__).resolve().parents[2] / "frontend" / "index.html"

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Agentic Financial Research & Filing Intelligence API. "
        "Educational prototype — not financial advice."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def serve_ui():
    """Serve the minimal web UI at the root URL."""
    if FRONTEND_HTML.exists():
        return FileResponse(FRONTEND_HTML)
    return {"message": "FinSight API running. Visit /docs for OpenAPI documentation."}


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
    )


@app.get("/documents", response_model=List[DocumentInfo], tags=["Filings"])
def get_documents() -> List[DocumentInfo]:
    """List all SEC filings currently indexed in the vector database."""
    try:
        docs = list_indexed_documents()
        return [DocumentInfo(**d) for d in docs]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")


@app.post("/ask", response_model=AskResponse, tags=["Research"])
def ask_question(payload: AskRequest) -> AskResponse:
    """Run the LangGraph workflow (routing between RAG and deterministic calculator)."""
    try:
        result = run_workflow(payload.question, ticker=payload.ticker)
        return AskResponse(
            question=payload.question,
            answer=result["answer"],
            route_used=result["route_used"],
            insufficient_evidence=result["insufficient_evidence"],
            citations=result["citations"],
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Workflow error: {exc}")
