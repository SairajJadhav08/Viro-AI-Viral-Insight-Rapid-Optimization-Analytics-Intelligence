"""
FastAPI dependencies for database - NO AUTHENTICATION REQUIRED
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from typing import Optional

def get_current_user(
    db: Session = Depends(get_db),
    user_id: Optional[int] = None
) -> Optional[User]:
    """Get current user - NO AUTHENTICATION REQUIRED (returns None or default user)"""
    # If no auth required, return None or get a default user
    # For simplicity, we'll just return None and endpoints will work without user
    return None

def get_user_or_create_default(db: Session = Depends(get_db)) -> User:
    """Get or create a default user for operations"""
    # Get first active user or create a default one
    default_user = db.query(User).filter(User.is_active == 1).first()
    if not default_user:
        # Create a default user if none exists
        default_user = User(
            email="default@viroai.local",
            password_hash="no_auth",
            first_name="Default",
            last_name="User",
            role="user",
            is_active=1
        )
        db.add(default_user)
        db.commit()
        db.refresh(default_user)
    return default_user
