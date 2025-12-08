"""
FastAPI dependencies for the application.

Provides database session management and other common dependencies.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from functools import partial
from typing import Generator, TypeVar, Callable, Any

from sqlalchemy.orm import Session
from database.base import SessionLocal, check_db_connection
from fastapi import Depends, HTTPException, status

# Thread pool for running sync DB operations in async context
_db_executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="db_worker")

T = TypeVar('T')


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI endpoints.
    Yields a database session and ensures it is closed after use.
    
    Usage in FastAPI endpoints:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions outside of FastAPI dependency injection.
    
    Usage:
        with get_db_session() as db:
            result = db.query(Model).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def run_in_threadpool(func: Callable[..., T], *args, **kwargs) -> T:
    """
    Run a synchronous function in the thread pool.
    
    Use this to run sync database operations in async functions without
    blocking the event loop.
    
    Usage:
        async def my_async_function():
            result = await run_in_threadpool(sync_db_function, arg1, arg2)
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _db_executor,
        partial(func, *args, **kwargs)
    )


def verify_database_connection():
    """
    Verify database is accessible.
    Raises HTTPException if database is down.
    """
    if not check_db_connection():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )
    return True


async def async_verify_database_connection():
    """
    Async version of database connection verification.
    """
    is_connected = await run_in_threadpool(check_db_connection)
    if not is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )
    return True
