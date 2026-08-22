"""
Auth routes — verify Supabase JWT and sync user record.
"""
from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.database import get_or_create_user
from app.models import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/session", response_model=UserResponse)
async def create_session(user: dict = Depends(get_current_user)):
    """
    Verify the Supabase JWT and create/return the app-side user record.
    Called by the frontend after Google sign-in.
    """
    user_metadata = user.get("user_metadata", {})
    db_user = get_or_create_user(
        user_id=user["user_id"],
        email=user["email"],
        display_name=user_metadata.get("full_name") or user_metadata.get("name"),
        avatar_url=user_metadata.get("avatar_url") or user_metadata.get("picture"),
    )
    return UserResponse(
        id=db_user["id"],
        email=db_user["email"],
        display_name=db_user.get("display_name"),
        avatar_url=db_user.get("avatar_url"),
    )
