import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)


class Settings:
    """Centralized configuration loaded from environment variables."""

    APP_NAME: str = "FinSight API"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIM: int = 384


settings = Settings()
