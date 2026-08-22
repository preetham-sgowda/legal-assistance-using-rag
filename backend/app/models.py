"""
Pydantic models for API request/response payloads.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Auth ──────────────────────────────────────────────

class UserResponse(BaseModel):
    id: str
    email: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None


# ── Chat ──────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=4000)


class Citation(BaseModel):
    act: str = ""
    section: str = ""
    text: str = ""


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    citations: list[Citation] = []
    mode: str = "general"  # "general" or "document"


# ── Upload ────────────────────────────────────────────

class UploadResponse(BaseModel):
    filename: str
    page_count: int
    chunk_count: int
    session_id: str


class UploadStatus(BaseModel):
    has_document: bool
    filename: Optional[str] = None


# ── History ───────────────────────────────────────────

class SessionSummary(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    citations: list[Citation] = []
    mode: str = "general"
    created_at: str
