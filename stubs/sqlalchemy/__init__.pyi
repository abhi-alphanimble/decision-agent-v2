from typing import Any

def and_(*args: Any) -> Any: ...

class _FuncNamespace:
    def __getattr__(self, name: str) -> Any: ...
    def count(self, *args: Any) -> Any: ...

func: _FuncNamespace

# Engine and SQL helpers
def create_engine(url: str, **kwargs: Any) -> Any: ...

def text(sql: str) -> Any: ...

# Generic placeholder for other sqlalchemy helpers
Engine: Any
Column: Any
Table: Any
MetaData: Any

# Re-export commonly used ORM names for simple static resolution
from .orm import Session, sessionmaker, declarative_base  # type: ignore
