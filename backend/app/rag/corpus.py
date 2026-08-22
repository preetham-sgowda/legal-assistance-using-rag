"""
Mode 1 retriever: queries the law corpus stored in Supabase pgvector.
"""
from app.database import get_supabase
from app.rag.embeddings import embed_query
from langchain_core.documents import Document


def retrieve_from_corpus(query: str, match_count: int = 5, match_threshold: float = 0.3) -> list[Document]:
    """
    Embed the query and retrieve the most similar law corpus chunks
    from Supabase via the match_documents RPC function.

    Returns LangChain Document objects with metadata (act, section, etc.).
    """
    query_embedding = embed_query(query).tolist()

    sb = get_supabase()
    result = sb.rpc("match_documents", {
        "query_embedding": query_embedding,
        "match_threshold": match_threshold,
        "match_count": match_count,
    }).execute()

    documents = []
    for row in (result.data or []):
        metadata = row.get("metadata", {})
        metadata["similarity"] = row.get("similarity", 0.0)
        documents.append(
            Document(
                page_content=row["content"],
                metadata=metadata,
            )
        )

    return documents
