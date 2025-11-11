import secrets
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from .config import ADMIN_API_KEY

api_key_header = APIKeyHeader(name="X-Admin-API-Key", auto_error=False)

def generate_access_key():
    """Generates a secure, random access key for users."""
    return f"bkmstr_{secrets.token_urlsafe(32)}"

async def get_admin_user(api_key: str = Security(api_key_header)):
    """A FastAPI dependency to protect admin routes."""
    if api_key == ADMIN_API_KEY:
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )