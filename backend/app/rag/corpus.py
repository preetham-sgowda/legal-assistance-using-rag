"""
Mode 1 retriever: queries the law corpus stored in the local persistent FAISS index.
"""
import os
import logging
from pathlib import Path
from typing import Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from app.rag.embeddings import LocalEmbeddings

logger = logging.getLogger(__name__)

INDEX_DIR = Path(__file__).resolve().parent.parent.parent / "corpus_index"
_corpus_vectorstore: Optional[FAISS] = None


def get_corpus_vectorstore() -> Optional[FAISS]:
    """Load or return the persistent FAISS law corpus vector store."""
    global _corpus_vectorstore
    if _corpus_vectorstore is not None:
        return _corpus_vectorstore

    if not INDEX_DIR.exists() or not (INDEX_DIR / "index.faiss").exists():
        logger.warning(f"Corpus index not found at {INDEX_DIR}. Run 'python -m scripts.ingest_corpus' first.")
        return None

    try:
        embeddings = LocalEmbeddings()
        _corpus_vectorstore = FAISS.load_local(
            str(INDEX_DIR),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        logger.info(f"Successfully loaded FAISS law corpus index from {INDEX_DIR}")
        return _corpus_vectorstore
    except Exception as e:
        logger.error(f"Failed to load FAISS corpus index: {e}")
        return None


def retrieve_from_corpus(query: str, match_count: int = 5) -> list[Document]:
    """
    Search the persistent FAISS index for relevant Indian Bare Act sections.
    Returns list of LangChain Document objects with metadata.
    """
    vectorstore = get_corpus_vectorstore()
    if vectorstore is None:
        return []

    return vectorstore.similarity_search(query, k=match_count)
