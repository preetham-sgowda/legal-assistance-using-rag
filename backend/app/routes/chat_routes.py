"""
Chat routes — main Q&A endpoint for both Mode 1 (General Law) and Mode 2 (Document).
Supports both synchronous responses and SSE streaming.
"""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.auth import get_current_user
from app.models import ChatRequest, ChatResponse, Citation
from app.database import (
    create_session,
    save_message,
    get_messages,
    update_session_title,
)
from app.rag.corpus import retrieve_from_corpus
from app.rag.document import document_store
from app.rag.chain import (
    generate_general_law_answer,
    generate_document_answer,
    stream_general_law_answer,
    stream_document_answer,
    _parse_citations,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])


def _generate_title(question: str) -> str:
    """Generate a short title from the first user question."""
    title = question.strip()[:80]
    if len(question) > 80:
        title += "…"
    return title


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: dict = Depends(get_current_user),
):
    """
    Main chat endpoint. Routes to Mode 1 or Mode 2 based on whether
    the session has an active uploaded document.
    """
    user_id = user["user_id"]

    # Create or use existing session
    session_id = request.session_id
    is_new_session = False
    if not session_id:
        session = create_session(user_id)
        session_id = session["id"]
        is_new_session = True

    # Save user message
    save_message(session_id, "user", request.message)

    # If this is the first message, set the session title
    if is_new_session:
        update_session_title(session_id, _generate_title(request.message))

    # Get recent chat history for context
    history_msgs = get_messages(session_id)
    chat_history = [
        {"role": m["role"], "content": m["content"]}
        for m in history_msgs[:-1]  # Exclude the message we just saved
    ]

    # Determine mode based on whether a document is uploaded for this session
    if document_store.has_document(session_id):
        # Mode 2: Document Q&A
        mode = "document"
        doc_info = document_store.get_document_info(session_id)
        context_docs = document_store.query(session_id, request.message, k=4)
        answer = generate_document_answer(
            question=request.message,
            context_docs=context_docs,
            filename=doc_info["filename"],
            chat_history=chat_history,
        )
        citations = []
    else:
        # Mode 1: General Law
        mode = "general"
        context_docs = retrieve_from_corpus(request.message, match_count=5)
        answer, raw_citations = generate_general_law_answer(
            question=request.message,
            context_docs=context_docs,
            chat_history=chat_history,
        )
        citations = [
            Citation(act=c.get("act", ""), section=c.get("section", ""), text=c.get("text", ""))
            for c in raw_citations
        ]

    # Save assistant message
    save_message(
        session_id, "assistant", answer,
        citations=[c.model_dump() for c in citations],
        mode=mode,
    )

    return ChatResponse(
        session_id=session_id,
        answer=answer,
        citations=citations,
        mode=mode,
    )


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    user: dict = Depends(get_current_user),
):
    """
    SSE streaming chat endpoint. Streams tokens as they are generated.
    Event format: data: {"token": "...", "done": false}
    Final event:  data: {"token": "", "done": true, "citations": [...], "session_id": "..."}
    """
    user_id = user["user_id"]

    session_id = request.session_id
    is_new_session = False
    if not session_id:
        session = create_session(user_id)
        session_id = session["id"]
        is_new_session = True

    save_message(session_id, "user", request.message)

    if is_new_session:
        update_session_title(session_id, _generate_title(request.message))

    history_msgs = get_messages(session_id)
    chat_history = [
        {"role": m["role"], "content": m["content"]}
        for m in history_msgs[:-1]
    ]

    def event_generator():
        full_answer = ""

        if document_store.has_document(session_id):
            mode = "document"
            doc_info = document_store.get_document_info(session_id)
            context_docs = document_store.query(session_id, request.message, k=4)

            for token in stream_document_answer(
                question=request.message,
                context_docs=context_docs,
                filename=doc_info["filename"],
                chat_history=chat_history,
            ):
                full_answer += token
                yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"

            citations = []
        else:
            mode = "general"
            context_docs = retrieve_from_corpus(request.message, match_count=5)

            for token in stream_general_law_answer(
                question=request.message,
                context_docs=context_docs,
                chat_history=chat_history,
            ):
                full_answer += token
                yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"

            # Parse citations from the full streamed answer
            clean_answer, raw_citations = _parse_citations(full_answer)
            full_answer = clean_answer
            citations = raw_citations

        # Save the complete message
        save_message(
            session_id, "assistant", full_answer,
            citations=citations,
            mode=mode,
        )

        # Send final event with metadata
        yield f"data: {json.dumps({'token': '', 'done': True, 'citations': citations, 'session_id': session_id, 'mode': mode})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
