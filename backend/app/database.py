"""
Supabase database client and helper functions.
Uses the service role key for server-side operations (bypasses RLS).
"""
import uuid
from datetime import datetime, timezone
from typing import Optional
from supabase import create_client, Client
from app.config import get_settings

_client: Optional[Client] = None


def get_supabase() -> Client:
    """Get or create the Supabase client (singleton)."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    return _client


# ── Users ─────────────────────────────────────────────

def get_or_create_user(user_id: str, email: str, display_name: str = None, avatar_url: str = None) -> dict:
    """Upsert a user record. Returns the user dict."""
    sb = get_supabase()
    data = {
        "id": user_id,
        "email": email,
    }
    if display_name:
        data["display_name"] = display_name
    if avatar_url:
        data["avatar_url"] = avatar_url

    result = sb.table("users").upsert(data, on_conflict="id").execute()
    return result.data[0] if result.data else data


# ── Chat Sessions ────────────────────────────────────

def create_session(user_id: str, title: str = "New conversation") -> dict:
    """Create a new chat session for a user."""
    sb = get_supabase()
    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    data = {
        "id": session_id,
        "user_id": user_id,
        "title": title,
        "created_at": now,
        "updated_at": now,
    }
    result = sb.table("chat_sessions").insert(data).execute()
    return result.data[0] if result.data else data


def get_sessions(user_id: str) -> list[dict]:
    """List all sessions for a user, newest first."""
    sb = get_supabase()
    result = (
        sb.table("chat_sessions")
        .select("*")
        .eq("user_id", user_id)
        .order("updated_at", desc=True)
        .execute()
    )
    return result.data or []


def update_session_title(session_id: str, title: str) -> None:
    """Update a session's title."""
    sb = get_supabase()
    sb.table("chat_sessions").update({
        "title": title,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", session_id).execute()


def update_session_timestamp(session_id: str) -> None:
    """Touch the updated_at timestamp on a session."""
    sb = get_supabase()
    sb.table("chat_sessions").update({
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", session_id).execute()


# ── Chat Messages ────────────────────────────────────

def save_message(
    session_id: str,
    role: str,
    content: str,
    citations: list[dict] = None,
    mode: str = "general",
) -> dict:
    """Persist a chat message."""
    sb = get_supabase()
    data = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "role": role,
        "content": content,
        "citations": citations or [],
        "mode": mode,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    result = sb.table("chat_messages").insert(data).execute()
    # Also touch session timestamp
    update_session_timestamp(session_id)
    return result.data[0] if result.data else data


def get_messages(session_id: str) -> list[dict]:
    """Fetch all messages for a session, oldest first."""
    sb = get_supabase()
    result = (
        sb.table("chat_messages")
        .select("*")
        .eq("session_id", session_id)
        .order("created_at", desc=False)
        .execute()
    )
    return result.data or []


def delete_session(session_id: str, user_id: str) -> bool:
    """Delete a session and its messages (cascade). Returns True if deleted."""
    sb = get_supabase()
    result = (
        sb.table("chat_sessions")
        .delete()
        .eq("id", session_id)
        .eq("user_id", user_id)
        .execute()
    )
    return len(result.data) > 0 if result.data else False
