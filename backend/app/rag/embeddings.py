"""
Embedding model wrapper using sentence-transformers.
Provides both direct embedding functions and a LangChain-compatible interface.
"""
import numpy as np
from typing import Optional
from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings

_model: Optional[SentenceTransformer] = None
_model_name: str = "all-MiniLM-L6-v2"


def init_embedding_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """Initialize the embedding model (call once at startup)."""
    global _model, _model_name
    _model_name = model_name
    _model = SentenceTransformer(model_name)
    return _model


def get_model() -> SentenceTransformer:
    """Get the loaded model, initializing if needed."""
    global _model
    if _model is None:
        _model = SentenceTransformer(_model_name)
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed a list of texts. Returns shape (n, 384) float32 array."""
    model = get_model()
    embeddings = model.encode(texts, show_progress_bar=False)
    return np.array(embeddings, dtype="float32")


def embed_query(text: str) -> np.ndarray:
    """Embed a single query string. Returns shape (384,) float32 array."""
    model = get_model()
    embedding = model.encode([text], show_progress_bar=False)
    return np.array(embedding[0], dtype="float32")


class LocalEmbeddings(Embeddings):
    """
    LangChain-compatible embeddings adapter wrapping sentence-transformers.
    Used by FAISS.from_documents() and other LangChain vector stores.
    """

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of document texts."""
        return embed_texts(texts).tolist()

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query."""
        return embed_query(text).tolist()
