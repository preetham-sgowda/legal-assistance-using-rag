"""
Authentication dependency for FastAPI using Firebase Admin SDK.
Verifies Firebase ID Tokens sent from the frontend.
"""
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import firebase_admin
from firebase_admin import auth

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Decode and verify the Firebase ID Token from the Authorization header.
    Returns decoded token dictionary containing user info.
    """
    token = credentials.credentials
    try:
        # Verify Firebase ID token
        decoded_token = auth.verify_id_token(token)
        return {
            "user_id": decoded_token.get("uid"),
            "email": decoded_token.get("email"),
            "display_name": decoded_token.get("name"),
            "avatar_url": decoded_token.get("picture"),
        }
    except Exception as e:
        logger.warning(f"Firebase token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
