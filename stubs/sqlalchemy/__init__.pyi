from typing import Any

def and_(*args: Any) -> Any: ...

class _FuncNamespace:
    def __getattr__(self, name: str) -> Any: ...
    def count(self, *args: Any) -> Any: ...

func: _FuncNamespace

# Engine and SQL helpers
def create_engine(url: str, **kwargs: Any) -> Any: ...
def engine_from_config(config: Any, **kwargs: Any) -> Any: ...

def text(sql: str) -> Any: ...

# Pool module
class pool:
    @staticmethod
    def NullPool() -> Any: ...

# Column types
Integer: Any
String: Any
Boolean: Any
DateTime: Any
Float: Any
Text: Any

# Constraints
CheckConstraint: Any
ForeignKey: Any
ForeignKeyConstraint: Any
PrimaryKeyConstraint: Any
UniqueConstraint: Any

# Table and Column
Column: Any
Table: Any
MetaData: Any

# Re-export commonly used ORM names for simple static resolution
from .orm import Session, sessionmaker, declarative_base, relationship  # type: ignore
