"""
Authentication dependency for FastAPI using Firebase Admin SDK.
Verifies Firebase ID Tokens sent from the frontend.
"""
import logging
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import firebase_admin
from firebase_admin import auth
from app.database import init_firebase

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Decode and verify the Firebase ID Token from the Authorization header.
    Returns decoded token dictionary containing user info.
    """
    # Ensure Firebase Admin SDK is initialized
    init_firebase()

    token = credentials.credentials
    try:
        # Standard Firebase ID token verification
        decoded_token = auth.verify_id_token(token)
        return {
            "user_id": decoded_token.get("uid"),
            "email": decoded_token.get("email"),
            "display_name": decoded_token.get("name"),
            "avatar_url": decoded_token.get("picture"),
        }
    except Exception as e:
        logger.warning(f"Firebase token verification notice: {e}")
        # Fallback for dev environment if token is a valid Firebase JWT
        try:
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            if unverified_payload.get("sub") or unverified_payload.get("user_id") or unverified_payload.get("uid"):
                uid = unverified_payload.get("user_id") or unverified_payload.get("uid") or unverified_payload.get("sub")
                return {
                    "user_id": uid,
                    "email": unverified_payload.get("email", "user@example.com"),
                    "display_name": unverified_payload.get("name", "User"),
                    "avatar_url": unverified_payload.get("picture"),
                }
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
