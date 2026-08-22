"""
Application configuration loaded from environment variables for Firebase architecture.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """All configuration for the Nyaya backend, loaded from .env file."""

    # Firebase Admin SDK
    firebase_credentials_path: Optional[str] = "serviceAccountKey.json"
    firebase_credentials_json: Optional[str] = None

    # Groq LLM
    groq_api_key: str = "placeholder_key"

    # Model configuration
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "llama-3.3-70b-versatile"

    # CORS
    frontend_url: str = "http://localhost:5173"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — loaded once per process."""
    return Settings()
