from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Schema for the GET /health response."""

    status: str = Field(..., description="Service health status", examples=["ok"])
    app_name: str = Field(..., description="Name of the service", examples=["FinSight API"])
    version: str = Field(..., description="API version", examples=["0.1.0"])
    environment: str = Field(..., description="Current runtime environment", examples=["development"])