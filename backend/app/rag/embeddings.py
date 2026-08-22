"""
Embedding model wrapper using sentence-transformers.
Optimized for low-RAM CPU environments (Render 512MB free tier).
"""
import logging
import numpy as np
from typing import Optional
from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)

_model: Optional[SentenceTransformer] = None
_model_name: str = "all-MiniLM-L6-v2"


def get_model() -> SentenceTransformer:
    """Get or lazy-load the SentenceTransformer model on first query."""
    global _model
    if _model is None:
        try:
            import torch
            torch.set_num_threads(1)
        except Exception:
            pass
        logger.info(f"Lazy loading embedding model: {_model_name}")
        _model = SentenceTransformer(_model_name, device="cpu")
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed a list of texts. Returns shape (n, 384) float32 array."""
    model = get_model()
    embeddings = model.encode(texts, show_progress_bar=False, batch_size=8)
    return np.array(embeddings, dtype="float32")


def embed_query(text: str) -> np.ndarray:
    """Embed a single query string. Returns shape (384,) float32 array."""
    model = get_model()
    embedding = model.encode([text], show_progress_bar=False)
    return np.array(embedding[0], dtype="float32")


class LocalEmbeddings(Embeddings):
    """LangChain-compatible embeddings adapter wrapping sentence-transformers."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return embed_texts(texts).tolist()

    def embed_query(self, text: str) -> list[float]:
        return embed_query(text).tolist()
