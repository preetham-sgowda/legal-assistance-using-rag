"""
Nyaya — Legal Assistant Backend
FastAPI application entry point.
"""
import os
import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_firebase
from app.routes import auth_routes, chat_routes, upload_routes, history_routes

# Optimize PyTorch memory footprint for CPU environment (Render free tier)
try:
    import torch
    torch.set_num_threads(1)
except Exception:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def warm_up_rag_models():
    """Background pre-loader: loads SentenceTransformer and FAISS index so queries respond instantly."""
    try:
        from app.rag.corpus import get_corpus_vectorstore
        logger.info("Pre-warming FAISS vectorstore and SentenceTransformer embeddings...")
        get_corpus_vectorstore()
        logger.info("FAISS vectorstore pre-warmed and ready for queries!")
    except Exception as e:
        logger.warning(f"RAG model warm-up notice: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: eager startup initialization and model pre-warming."""
    settings = get_settings()
    logger.info("Initializing Nyaya backend server...")
    init_firebase()
    
    # Pre-warm RAG vectorstore in background thread to avoid blocking server boot
    threading.Thread(target=warm_up_rag_models, daemon=True).start()

    logger.info(f"Using LLM: {settings.llm_model} via Groq")
    yield
    logger.info("Shutting down Nyaya backend")


app = FastAPI(
    title="Nyaya — Legal Assistant API",
    description="RAG-powered legal information assistant for Indian law",
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(chat_routes.router)
app.include_router(upload_routes.router)
app.include_router(history_routes.router)


@app.get("/")
async def root():
    """Root landing endpoint for backend API."""
    return {
        "name": "Nyaya Legal Assistant API",
        "status": "online",
        "health": "/health",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "nyaya-backend",
        "model": settings.llm_model,
    }
