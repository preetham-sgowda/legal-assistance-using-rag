"""
Nyaya — Legal Assistant Backend
FastAPI application entry point.
"""
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    settings = get_settings()
    logger.info("Initializing Nyaya backend server...")
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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "nyaya-backend",
        "model": settings.llm_model,
    }
