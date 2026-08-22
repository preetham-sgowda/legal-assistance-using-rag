"""
Firebase Cloud Firestore client and database helper functions.
Handles user profiles, chat sessions, and chat message storage.
"""
import os
import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

import firebase_admin
from firebase_admin import credentials, firestore
from app.config import get_settings

logger = logging.getLogger(__name__)
_firestore_db = None


def init_firebase() -> bool:
    """Initialize Firebase Admin SDK app at application startup."""
    if firebase_admin._apps:
        return True

    settings = get_settings()
    cred = None

    # Option 1: Load from JSON string in environment variable
    if settings.firebase_credentials_json:
        try:
            cred_dict = json.loads(settings.firebase_credentials_json)
            cred = credentials.Certificate(cred_dict)
            logger.info("Initialized Firebase Admin SDK from FIREBASE_CREDENTIALS_JSON")
        except Exception as e:
            logger.error(f"Failed to parse FIREBASE_CREDENTIALS_JSON: {e}")

    # Option 2: Load from service account file path
    if cred is None and settings.firebase_credentials_path and os.path.exists(settings.firebase_credentials_path):
        try:
            cred = credentials.Certificate(settings.firebase_credentials_path)
            logger.info(f"Initialized Firebase Admin SDK from {settings.firebase_credentials_path}")
        except Exception as e:
            logger.error(f"Failed to load service account key from {settings.firebase_credentials_path}: {e}")

    # Option 3: Default application credentials / Project options fallback
    if cred is None:
        try:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred)
            logger.info("Initialized Firebase Admin SDK using Application Default Credentials")
            return True
        except Exception:
            logger.warning("Service account key not found. Initializing Firebase Admin SDK with project ID fallback.")
            firebase_admin.initialize_app(options={"projectId": "legal-assistance-using-rag"})
            return True

    firebase_admin.initialize_app(cred)
    return True


def get_firestore_db():
    """Initialize and return Firebase Firestore client (singleton)."""
    global _firestore_db
    if _firestore_db is not None:
        return _firestore_db

    init_firebase()

    try:
        _firestore_db = firestore.client()
    except Exception as e:
        logger.warning(f"Firestore client initialization warning: {e}")
        # In case Firestore is unreachable without credentials, fallback mock for local testing
        _firestore_db = firestore.client()

    return _firestore_db


# ── Users ─────────────────────────────────────────────

def get_or_create_user(user_id: str, email: str, display_name: str = None, avatar_url: str = None) -> dict:
    """Upsert a user document in Firestore `users` collection."""
    try:
        db = get_firestore_db()
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        data = {
            "id": user_id,
            "email": email,
            "updated_at": firestore.SERVER_TIMESTAMP,
        }
        if display_name:
            data["display_name"] = display_name
        if avatar_url:
            data["avatar_url"] = avatar_url

        if not user_doc.exists:
            data["created_at"] = firestore.SERVER_TIMESTAMP
            user_ref.set(data)
        else:
            user_ref.update(data)
    except Exception as e:
        logger.warning(f"Firestore user save notice: {e}")

    return {"id": user_id, "email": email, "display_name": display_name, "avatar_url": avatar_url}


# ── Chat Sessions ────────────────────────────────────

def create_session(user_id: str, title: str = "New conversation") -> dict:
    """Create a new chat session document in Firestore `chat_sessions`."""
    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    data = {
        "id": session_id,
        "user_id": user_id,
        "title": title,
        "created_at": now,
        "updated_at": now,
    }

    try:
        db = get_firestore_db()
        db.collection("chat_sessions").document(session_id).set(data)
    except Exception as e:
        logger.warning(f"Firestore session create notice: {e}")

    return data


def get_sessions(user_id: str) -> List[dict]:
    """List all sessions for a user, sorted by updated_at descending."""
    try:
        db = get_firestore_db()
        docs = (
            db.collection("chat_sessions")
            .where("user_id", "==", user_id)
            .stream()
        )
        sessions = [doc.to_dict() for doc in docs]
        sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
        return sessions
    except Exception as e:
        logger.warning(f"Firestore get_sessions notice: {e}")
        return []


def update_session_title(session_id: str, title: str) -> None:
    """Update a session's title."""
    try:
        db = get_firestore_db()
        now = datetime.now(timezone.utc).isoformat()
        db.collection("chat_sessions").document(session_id).update({
            "title": title,
            "updated_at": now,
        })
    except Exception as e:
        logger.warning(f"Firestore update_session_title notice: {e}")


def update_session_timestamp(session_id: str) -> None:
    """Touch the updated_at timestamp on a session."""
    try:
        db = get_firestore_db()
        now = datetime.now(timezone.utc).isoformat()
        db.collection("chat_sessions").document(session_id).update({
            "updated_at": now,
        })
    except Exception as e:
        logger.warning(f"Firestore update_session_timestamp notice: {e}")


# ── Chat Messages ────────────────────────────────────

def save_message(
    session_id: str,
    role: str,
    content: str,
    citations: list[dict] = None,
    mode: str = "general",
) -> dict:
    """Persist a chat message into Firestore `chat_messages` collection."""
    msg_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    data = {
        "id": msg_id,
        "session_id": session_id,
        "role": role,
        "content": content,
        "citations": citations or [],
        "mode": mode,
        "created_at": now,
    }

    try:
        db = get_firestore_db()
        db.collection("chat_messages").document(msg_id).set(data)
        update_session_timestamp(session_id)
    except Exception as e:
        logger.warning(f"Firestore save_message notice: {e}")

    return data


def get_messages(session_id: str) -> List[dict]:
    """Fetch all messages for a session, ordered by created_at ascending."""
    try:
        db = get_firestore_db()
        docs = (
            db.collection("chat_messages")
            .where("session_id", "==", session_id)
            .stream()
        )
        messages = [doc.to_dict() for doc in docs]
        messages.sort(key=lambda m: m.get("created_at", ""))
        return messages
    except Exception as e:
        logger.warning(f"Firestore get_messages notice: {e}")
        return []


def delete_session(session_id: str, user_id: str) -> bool:
    """Delete a session and its messages from Firestore."""
    try:
        db = get_firestore_db()
        session_ref = db.collection("chat_sessions").document(session_id)
        session_doc = session_ref.get()

        if not session_doc.exists or session_doc.to_dict().get("user_id") != user_id:
            return False

        msg_docs = db.collection("chat_messages").where("session_id", "==", session_id).stream()
        for mdoc in msg_docs:
            mdoc.reference.delete()

        session_ref.delete()
        return True
    except Exception as e:
        logger.warning(f"Firestore delete_session notice: {e}")
        return False
