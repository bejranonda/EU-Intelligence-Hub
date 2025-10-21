"""Authentication utilities for admin endpoints."""
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
import logging

from app.config import get_settings
from app.database import get_db

logger = logging.getLogger(__name__)
settings = get_settings()
security = HTTPBasic()


def verify_admin_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Verify admin credentials using HTTP Basic Authentication.

    Args:
        credentials: HTTP Basic Auth credentials

    Returns:
        dict: Admin credentials if valid

    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        # Check if username and password match configured values
        correct_username = getattr(settings, 'admin_username', 'admin')
        correct_password = getattr(settings, 'admin_password', 'password')

        logger.info(f"Auth attempt: username={credentials.username} (expected: {correct_username}), "
                   f"password_match={credentials.password == correct_password}")

        if (credentials.username == correct_username and
            credentials.password == correct_password):
            logger.info(f"Admin authentication successful for: {credentials.username}")
            return credentials
        else:
            # Log failed authentication attempt
            logger.warning(f"Failed admin login attempt: {credentials.username}")
            raise HTTPException(
                status_code=401,
                detail="Invalid admin credentials",
                headers={"WWW-Authenticate": "Basic"},
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Authentication error"
        )


def get_current_admin(credentials: HTTPBasicCredentials = Depends(verify_admin_credentials)):
    """
    Dependency to ensure current user is authenticated admin.
    
    Returns:
        dict: Admin user info
        
    Raises:
        HTTPException: If not authenticated
    """
    return {"username": credentials.username, "authenticated": True}
