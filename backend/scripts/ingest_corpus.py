"""
Corpus Ingestion Script (FAISS Persistent Index)
==============================================
Parses Indian Act text files, chunks them by section, embeds them using
sentence-transformers, and saves a persistent FAISS index locally.

Usage:
    cd backend
    python -m scripts.ingest_corpus
"""
import os
import re
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from app.rag.embeddings import init_embedding_model, LocalEmbeddings
from app.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logger = logging.getLogger(__name__)

CORPUS_DIR = Path(__file__).resolve().parent.parent.parent / "corpus"
INDEX_SAVE_DIR = Path(__file__).resolve().parent.parent / "corpus_index"

ACT_METADATA = {
    "it_act": {
        "act_name": "Information Technology Act, 2000",
        "short_name": "IT Act 2000",
        "year": 2000,
    },
    "consumer_protection": {
        "act_name": "Consumer Protection Act, 2019",
        "short_name": "Consumer Protection Act 2019",
        "year": 2019,
    },
    "bns": {
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "short_name": "BNS 2023",
        "year": 2023,
    },
}


def detect_act_metadata(filename: str) -> dict:
    """Match a filename to its Act metadata."""
    fname_lower = filename.lower()
    for key, meta in ACT_METADATA.items():
        if key in fname_lower:
            return meta
    return {
        "act_name": filename.replace("_", " ").replace(".txt", "").title(),
        "short_name": filename.replace(".txt", ""),
        "year": 0,
    }


def parse_sections(text: str, act_meta: dict) -> list[Document]:
    """Parse a raw Act text into sections and return LangChain Documents."""
    section_pattern = r'(?:^|\n)(?:Section\s+)?(\d+[A-Z]?)\.\s*([^\n]*)'
    matches = list(re.finditer(section_pattern, text))

    docs = []

    if len(matches) >= 2:
        for i, match in enumerate(matches):
            section_num = f"Section {match.group(1)}"
            section_title = match.group(2).strip().rstrip(".")

            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            section_text = text[start:end].strip()

            if len(section_text) < 30:
                continue

            meta = {
                **act_meta,
                "section_number": section_num,
                "section_title": section_title,
            }
            docs.append(Document(page_content=section_text, metadata=meta))
    else:
        meta = {**act_meta, "section_number": "Part 1", "section_title": ""}
        docs.append(Document(page_content=text, metadata=meta))

    return docs


def main():
    if not CORPUS_DIR.exists():
        logger.error(f"Corpus directory not found: {CORPUS_DIR}")
        sys.exit(1)

    txt_files = list(CORPUS_DIR.glob("*.txt"))
    if not txt_files:
        logger.error(f"No .txt files found in {CORPUS_DIR}")
        sys.exit(1)

    settings = get_settings()
    init_embedding_model(settings.embedding_model)
    embeddings = LocalEmbeddings()

    all_docs = []
    for filepath in txt_files:
        act_meta = detect_act_metadata(filepath.name)
        logger.info(f"Parsing {act_meta['act_name']} from {filepath.name}")
        text = filepath.read_text(encoding="utf-8")
        docs = parse_sections(text, act_meta)
        all_docs.extend(docs)

    logger.info(f"Building FAISS vector index for {len(all_docs)} corpus sections...")
    vectorstore = FAISS.from_documents(all_docs, embeddings)

    # Save vector index locally
    INDEX_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(INDEX_SAVE_DIR))
    logger.info(f"FAISS index successfully saved to: {INDEX_SAVE_DIR}")


if __name__ == "__main__":
    main()
