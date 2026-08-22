"""
Corpus Ingestion Script
=======================
One-time script to parse Indian Act text files, chunk them by section,
embed them, and insert into Supabase pgvector.

Usage:
    cd backend
    python -m scripts.ingest_corpus

Expects .txt files in the ../corpus/ directory with section-based formatting.
"""
import os
import re
import sys
import logging
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.config import get_settings
from app.database import get_supabase
from app.rag.embeddings import init_embedding_model, embed_texts

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logger = logging.getLogger(__name__)

# Directory containing the raw Act text files
CORPUS_DIR = Path(__file__).resolve().parent.parent.parent / "corpus"

# Map of filename patterns to act metadata
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


def parse_sections(text: str, act_meta: dict) -> list[dict]:
    """
    Parse a raw Act text into sections.
    Looks for patterns like "Section 1.", "Section 43A.", "1.", "43A." etc.
    Each section becomes one chunk with metadata.
    """
    # Try to split by "Section X" or "X." patterns
    section_pattern = r'(?:^|\n)(?:Section\s+)?(\d+[A-Z]?)\.\s*([^\n]*)'
    matches = list(re.finditer(section_pattern, text))

    chunks = []

    if len(matches) >= 3:
        # We found section headers — split text by them
        for i, match in enumerate(matches):
            section_num = f"Section {match.group(1)}"
            section_title = match.group(2).strip().rstrip(".")

            # Get text from this match to the next match (or end of text)
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            section_text = text[start:end].strip()

            # Skip very short sections (likely just a heading)
            if len(section_text) < 30:
                continue

            # If a section is very long, split it further
            if len(section_text) > 1500:
                sub_chunks = _split_long_section(section_text, 800, 200)
                for j, sub in enumerate(sub_chunks):
                    chunks.append({
                        "content": sub,
                        "metadata": {
                            **act_meta,
                            "section_number": section_num,
                            "section_title": section_title,
                            "chunk_part": j + 1,
                        },
                    })
            else:
                chunks.append({
                    "content": section_text,
                    "metadata": {
                        **act_meta,
                        "section_number": section_num,
                        "section_title": section_title,
                    },
                })
    else:
        # Fallback: split by paragraphs / fixed size
        logger.warning(f"Could not detect sections in {act_meta['act_name']}, using paragraph split")
        sub_chunks = _split_long_section(text, 800, 200)
        for i, chunk_text in enumerate(sub_chunks):
            chunks.append({
                "content": chunk_text,
                "metadata": {
                    **act_meta,
                    "section_number": f"Part {i + 1}",
                    "section_title": "",
                },
            })

    return chunks


def _split_long_section(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split a long text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        # Try to break at a sentence boundary
        if end < len(text):
            last_period = text.rfind(". ", start, end)
            if last_period > start + chunk_size // 2:
                end = last_period + 1
        chunks.append(text[start:end].strip())
        start = end - overlap
    return [c for c in chunks if len(c) > 20]


def ingest_file(filepath: Path) -> int:
    """
    Ingest a single Act file into Supabase pgvector.
    Returns the number of chunks inserted.
    """
    act_meta = detect_act_metadata(filepath.name)
    logger.info(f"Ingesting: {act_meta['act_name']} from {filepath.name}")

    text = filepath.read_text(encoding="utf-8")
    if not text.strip():
        logger.warning(f"Skipping empty file: {filepath.name}")
        return 0

    # Parse into sections
    chunks = parse_sections(text, act_meta)
    logger.info(f"  Parsed into {len(chunks)} chunks")

    if not chunks:
        return 0

    # Embed all chunks
    contents = [c["content"] for c in chunks]
    embeddings = embed_texts(contents)
    logger.info(f"  Embedded {len(embeddings)} chunks")

    # Clear existing entries for this Act (idempotent re-ingestion)
    sb = get_supabase()
    sb.table("documents").delete().eq(
        "metadata->>act_name", act_meta["act_name"]
    ).execute()

    # Insert into Supabase
    rows = []
    for chunk, embedding in zip(chunks, embeddings):
        rows.append({
            "content": chunk["content"],
            "metadata": chunk["metadata"],
            "embedding": embedding.tolist(),
        })

    # Insert in batches of 50
    batch_size = 50
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        sb.table("documents").insert(batch).execute()

    logger.info(f"  Inserted {len(rows)} chunks into Supabase")
    return len(rows)


def main():
    """Ingest all Act files from the corpus directory."""
    if not CORPUS_DIR.exists():
        logger.error(f"Corpus directory not found: {CORPUS_DIR}")
        sys.exit(1)

    txt_files = list(CORPUS_DIR.glob("*.txt"))
    if not txt_files:
        logger.error(f"No .txt files found in {CORPUS_DIR}")
        sys.exit(1)

    # Initialize embedding model
    settings = get_settings()
    init_embedding_model(settings.embedding_model)

    total_chunks = 0
    for filepath in txt_files:
        count = ingest_file(filepath)
        total_chunks += count

    logger.info(f"Ingestion complete. Total chunks: {total_chunks}")


if __name__ == "__main__":
    main()
