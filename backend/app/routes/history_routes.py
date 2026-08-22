"""
History routes — list and retrieve past chat sessions and messages.
"""
from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user
from app.database import get_sessions, get_messages, delete_session
from app.models import SessionSummary, MessageResponse, Citation

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=list[SessionSummary])
async def list_sessions(user: dict = Depends(get_current_user)):
    """List all chat sessions for the authenticated user, newest first."""
    sessions = get_sessions(user["user_id"])
    return [
        SessionSummary(
            id=s["id"],
            title=s.get("title", "New conversation"),
            created_at=s["created_at"],
            updated_at=s.get("updated_at", s["created_at"]),
        )
        for s in sessions
    ]


@router.get("/{session_id}", response_model=list[MessageResponse])
async def get_session_messages(
    session_id: str,
    user: dict = Depends(get_current_user),
):
    """Fetch all messages for a specific session."""
    messages = get_messages(session_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Session not found or has no messages.")

    return [
        MessageResponse(
            id=m["id"],
            role=m["role"],
            content=m["content"],
            citations=[
                Citation(**c) for c in (m.get("citations") or [])
            ],
            mode=m.get("mode", "general"),
            created_at=m["created_at"],
        )
        for m in messages
    ]


@router.delete("/{session_id}")
async def delete_chat_session(
    session_id: str,
    user: dict = Depends(get_current_user),
):
    """Delete a chat session and all its messages."""
    deleted = delete_session(session_id, user["user_id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"deleted": True, "session_id": session_id}
