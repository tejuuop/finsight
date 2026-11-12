import os
from pathlib import Path
from dotenv import load_dotenv

# Locate the root directory of the repository (two levels up from backend/app/config.py)
ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT_DIR / ".env"

# Load environment variables from .env if it exists
load_dotenv(dotenv_path=ENV_PATH)


class Settings:
    """Centralized configuration loaded from environment variables."""

    APP_NAME: str = "FinSight API"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


settings = Settings()