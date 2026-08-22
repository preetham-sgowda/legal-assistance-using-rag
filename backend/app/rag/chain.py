"""
RAG chain logic: builds LLM calls for both Mode 1 and Mode 2.
Uses Groq API with Llama for fast inference.
"""
import json
import re
import logging
from typing import AsyncIterator

from groq import Groq
from langchain_core.documents import Document

from app.config import get_settings
from app.prompts.general_law import GENERAL_LAW_SYSTEM_PROMPT
from app.prompts.document_qa import DOCUMENT_QA_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_groq_client: Groq = None


def get_groq_client() -> Groq:
    """Get or create the Groq client (singleton)."""
    global _groq_client
    if _groq_client is None:
        settings = get_settings()
        _groq_client = Groq(api_key=settings.groq_api_key)
    return _groq_client


def _format_context(documents: list[Document]) -> str:
    """Format retrieved documents into context string for the prompt."""
    if not documents:
        return "No relevant legal text found."

    context_parts = []
    for i, doc in enumerate(documents, 1):
        meta = doc.metadata
        act = meta.get("act_name", "Unknown Act")
        section = meta.get("section_number", "")
        section_title = meta.get("section_title", "")

        header = f"[{act}"
        if section:
            header += f", {section}"
        if section_title:
            header += f" — {section_title}"
        header += "]"

        context_parts.append(f"--- Excerpt {i} {header} ---\n{doc.page_content}")

    return "\n\n".join(context_parts)


def _parse_citations(answer: str) -> tuple[str, list[dict]]:
    """
    Parse citation JSON from the LLM response.
    Returns (clean_answer, citations_list).
    """
    citations = []
    clean_answer = answer

    # Try to extract CITATIONS_JSON block
    json_match = re.search(r'CITATIONS_JSON:\s*(\[.*?\])', answer, re.DOTALL)
    if json_match:
        try:
            citations = json.loads(json_match.group(1))
            # Remove the JSON block from the visible answer
            clean_answer = answer[:json_match.start()].strip()
        except json.JSONDecodeError:
            logger.warning("Failed to parse citations JSON from LLM response")

    # Fallback: extract citations from [Act Name, Section X] patterns in text
    if not citations:
        citation_pattern = r'\[([^,\]]+),\s*(Section\s+\d+\w*(?:\s*\([^)]*\))?)\]'
        matches = re.findall(citation_pattern, answer)
        seen = set()
        for act, section in matches:
            key = f"{act}|{section}"
            if key not in seen:
                seen.add(key)
                citations.append({
                    "act": act.strip(),
                    "section": section.strip(),
                    "text": "",
                })

    return clean_answer, citations


def generate_general_law_answer(
    question: str,
    context_docs: list[Document],
    chat_history: list[dict] = None,
) -> tuple[str, list[dict]]:
    """
    Generate a Mode 1 answer using retrieved law corpus chunks.
    Returns (answer_text, citations_list).
    """
    settings = get_settings()
    client = get_groq_client()

    context = _format_context(context_docs)

    # Build the prompt
    system_message = GENERAL_LAW_SYSTEM_PROMPT.format(
        context=context,
        question=question,
    )

    messages = [{"role": "system", "content": system_message}]

    # Add chat history for context continuity (last 6 messages max)
    if chat_history:
        for msg in chat_history[-6:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

    messages.append({"role": "user", "content": question})

    # Call Groq
    completion = client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        temperature=0.1,  # Low temperature for factual accuracy
        max_tokens=2048,
    )

    raw_answer = completion.choices[0].message.content
    answer, citations = _parse_citations(raw_answer)

    # Enrich citations with source text from context docs
    for citation in citations:
        if not citation.get("text"):
            for doc in context_docs:
                meta = doc.metadata
                if (citation["act"].lower() in meta.get("act_name", "").lower() and
                    citation["section"].lower() in meta.get("section_number", "").lower()):
                    citation["text"] = doc.page_content[:300]
                    break

    return answer, citations


def generate_document_answer(
    question: str,
    context_docs: list[Document],
    filename: str,
    chat_history: list[dict] = None,
) -> str:
    """
    Generate a Mode 2 answer using uploaded document chunks.
    Returns the answer text (no formal citations for personal documents).
    """
    settings = get_settings()
    client = get_groq_client()

    context = "\n\n".join(
        f"--- Excerpt {i+1} ---\n{doc.page_content}"
        for i, doc in enumerate(context_docs)
    )

    system_message = DOCUMENT_QA_SYSTEM_PROMPT.format(
        filename=filename,
        context=context,
        question=question,
    )

    messages = [{"role": "system", "content": system_message}]

    if chat_history:
        for msg in chat_history[-6:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

    messages.append({"role": "user", "content": question})

    completion = client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        temperature=0.2,
        max_tokens=2048,
    )

    return completion.choices[0].message.content


def stream_general_law_answer(
    question: str,
    context_docs: list[Document],
    chat_history: list[dict] = None,
):
    """
    Stream a Mode 1 answer token by token. Yields string chunks.
    """
    settings = get_settings()
    client = get_groq_client()

    context = _format_context(context_docs)
    system_message = GENERAL_LAW_SYSTEM_PROMPT.format(
        context=context,
        question=question,
    )

    messages = [{"role": "system", "content": system_message}]
    if chat_history:
        for msg in chat_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    stream = client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        temperature=0.1,
        max_tokens=2048,
        stream=True,
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def stream_document_answer(
    question: str,
    context_docs: list[Document],
    filename: str,
    chat_history: list[dict] = None,
):
    """
    Stream a Mode 2 answer token by token. Yields string chunks.
    """
    settings = get_settings()
    client = get_groq_client()

    context = "\n\n".join(
        f"--- Excerpt {i+1} ---\n{doc.page_content}"
        for i, doc in enumerate(context_docs)
    )
    system_message = DOCUMENT_QA_SYSTEM_PROMPT.format(
        filename=filename,
        context=context,
        question=question,
    )

    messages = [{"role": "system", "content": system_message}]
    if chat_history:
        for msg in chat_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    stream = client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        temperature=0.2,
        max_tokens=2048,
        stream=True,
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
