"""
Nyaya — Legal Assistant Backend
FastAPI application entry point.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.rag.embeddings import init_embedding_model
from app.routes import auth_routes, chat_routes, upload_routes, history_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: load the embedding model once at startup."""
    settings = get_settings()
    logger.info(f"Loading embedding model: {settings.embedding_model}")
    init_embedding_model(settings.embedding_model)
    logger.info("Embedding model loaded successfully")
    logger.info(f"Using LLM: {settings.llm_model} via Groq")
    yield
    logger.info("Shutting down Nyaya backend")


app = FastAPI(
    title="Nyaya — Legal Assistant API",
    description="RAG-powered legal information assistant for Indian law",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount route modules
app.include_router(auth_routes.router)
app.include_router(chat_routes.router)
app.include_router(upload_routes.router)
app.include_router(history_routes.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "nyaya-backend",
        "model": settings.llm_model,
    }
