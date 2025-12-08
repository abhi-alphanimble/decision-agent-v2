"""
Database utilities and error handling decorators.

Provides consistent error handling patterns for database operations.
"""
from functools import wraps
from typing import Any, Callable, Dict, TypeVar, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from ..config import get_context_logger

logger = get_context_logger(__name__)

# Type variable for generic return type
T = TypeVar('T')


class DatabaseError(Exception):
    """Base exception for database operations."""
    pass


class RecordNotFoundError(DatabaseError):
    """Raised when a requested record is not found."""
    pass


class DuplicateRecordError(DatabaseError):
    """Raised when attempting to create a duplicate record."""
    pass


def handle_db_errors(
    operation_name: str = "database operation",
    reraise: bool = False,
    default_return: Any = None
) -> Callable:
    """
    Decorator for consistent database error handling.
    
    Args:
        operation_name: Human-readable name for logging
        reraise: If True, re-raise the exception after logging
        default_return: Value to return on error if not reraising
        
    Usage:
        @handle_db_errors("create decision", reraise=True)
        def create_decision(db: Session, ...) -> Decision:
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except IntegrityError as e:
                logger.error(
                    f"Integrity error in {operation_name}: {e}",
                    exc_info=True,
                    extra={"operation": operation_name, "error_type": "integrity"}
                )
                # Try to rollback if session is available
                _try_rollback(args, kwargs)
                if reraise:
                    raise DuplicateRecordError(f"Duplicate record in {operation_name}") from e
                return default_return
            except SQLAlchemyError as e:
                logger.error(
                    f"Database error in {operation_name}: {e}",
                    exc_info=True,
                    extra={"operation": operation_name, "error_type": "sqlalchemy"}
                )
                _try_rollback(args, kwargs)
                if reraise:
                    raise DatabaseError(f"Database error in {operation_name}") from e
                return default_return
            except Exception as e:
                logger.error(
                    f"Unexpected error in {operation_name}: {e}",
                    exc_info=True,
                    extra={"operation": operation_name, "error_type": "unexpected"}
                )
                _try_rollback(args, kwargs)
                if reraise:
                    raise
                return default_return
        return wrapper
    return decorator


def _try_rollback(args: tuple, kwargs: dict) -> None:
    """Try to find and rollback a database session from function arguments."""
    # Check kwargs first
    db = kwargs.get('db')
    if db and isinstance(db, Session):
        try:
            db.rollback()
        except Exception:
            pass
        return
    
    # Check positional args
    for arg in args:
        if isinstance(arg, Session):
            try:
                arg.rollback()
            except Exception:
                pass
            return


def safe_commit(db: Session, operation_name: str = "commit") -> bool:
    """
    Safely commit a database transaction with proper error handling.
    
    Args:
        db: Database session
        operation_name: Name of the operation for logging
        
    Returns:
        True if commit succeeded, False otherwise
    """
    try:
        db.commit()
        return True
    except IntegrityError as e:
        logger.error(f"Integrity error during {operation_name}: {e}", exc_info=True)
        db.rollback()
        return False
    except SQLAlchemyError as e:
        logger.error(f"Database error during {operation_name}: {e}", exc_info=True)
        db.rollback()
        return False


def safe_refresh(db: Session, obj: Any, operation_name: str = "refresh") -> bool:
    """
    Safely refresh an object from the database.
    
    Args:
        db: Database session
        obj: Object to refresh
        operation_name: Name of the operation for logging
        
    Returns:
        True if refresh succeeded, False otherwise
    """
    try:
        db.refresh(obj)
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error refreshing object in {operation_name}: {e}", exc_info=True)
        return False
