
from sqlalchemy.orm import Session
from database.base import SessionLocal, test_connection
from fastapi import Depends, HTTPException, status
from typing import Generator

def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI endpoints.
    Yields a database session and ensures it is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_database_connection():
    """
    Verify database is accessible.
    Raises HTTPException if database is down.
    """
    if not test_connection():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )
    return True

