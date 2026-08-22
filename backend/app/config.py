"""
Application configuration loaded from environment variables.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """All configuration for the Nyaya backend, loaded from .env file."""

    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    supabase_jwt_secret: str

    # Groq LLM
    groq_api_key: str

    # Model configuration
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "llama-3.3-70b-versatile"

    # CORS
    frontend_url: str = "http://localhost:5173"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — loaded once per process."""
    return Settings()
