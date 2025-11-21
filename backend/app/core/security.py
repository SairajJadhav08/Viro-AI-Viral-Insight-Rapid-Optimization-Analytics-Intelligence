"""
Simple security utilities - NO TOKEN SYSTEM
"""
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated="auto",
    default="pbkdf2_sha256"
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password with compatibility fallback"""
    try:
        return pwd_context.hash(password)
    except ValueError as e:
        # Handle passlib/bcrypt detection issue on Python 3.13
        if "password cannot be longer than 72 bytes" in str(e):
            safe_password = password[:72]
            return pwd_context.hash(safe_password)
        raise
