from fastapi import FastAPI
from app.config import settings
from app.schemas import HealthResponse

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Agentic Financial Research & Filing Intelligence API. "
        "Educational prototype — not financial advice."
    ),
)


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check() -> HealthResponse:
    """Verify that the API server is running and responsive."""
    return HealthResponse(
        status="ok",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
    )