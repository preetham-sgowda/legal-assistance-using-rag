"""
Upload routes — handle document upload and removal for Mode 2.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.auth import get_current_user
from app.models import UploadResponse, UploadStatus
from app.rag.document import document_store

router = APIRouter(tags=["upload"])

# Max file size: 10 MB
MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    session_id: str = Form(...),
    user: dict = Depends(get_current_user),
):
    """
    Upload a PDF or DOCX document for Mode 2 Q&A.
    Builds a session-scoped FAISS index from the document.
    """
    # Validate file extension
    filename = file.filename or "document"
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{ext}'. Please upload a PDF or DOCX file.",
        )

    # Read file content
    file_bytes = await file.read()

    # Validate file size
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({len(file_bytes) / 1024 / 1024:.1f} MB). Maximum size is 10 MB.",
        )

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    try:
        session_doc = document_store.add_document(session_id, file_bytes, filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}",
        )

    return UploadResponse(
        filename=session_doc.filename,
        page_count=session_doc.page_count,
        chunk_count=session_doc.chunk_count,
        session_id=session_id,
    )


@router.delete("/upload")
async def remove_document(
    session_id: str,
    user: dict = Depends(get_current_user),
):
    """
    Remove the active document for a session, reverting to Mode 1.
    """
    removed = document_store.remove_document(session_id)
    return {"removed": removed, "session_id": session_id}


@router.get("/upload/status", response_model=UploadStatus)
async def document_status(
    session_id: str,
    user: dict = Depends(get_current_user),
):
    """Check if a session has an active uploaded document."""
    info = document_store.get_document_info(session_id)
    if info:
        return UploadStatus(has_document=True, filename=info["filename"])
    return UploadStatus(has_document=False)
