"""
SkinSense AI - Password Hashing Utilities.

Provides bcrypt-based password hashing and validation using passlib.
"""

from passlib.context import CryptContext

# Configure passlib CryptContext using bcrypt scheme
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt algorithm.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a stored bcrypt hash.
    """
    return pwd_context.verify(plain_password, hashed_password)
