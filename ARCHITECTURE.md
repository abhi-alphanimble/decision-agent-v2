# Architecture Overview

Decision Agent is organized as a small FastAPI service with clear separation of concerns.

- `app/main.py`: FastAPI application and route registration.
- `app/handlers/*`: Command handlers and business logic for decisions.
- `app/slack_client.py`: Slack wrapper and client abstraction (production + mock).
- `app/ai/ai_client.py`: AI client wrapper (production + mock for tests).
- `app/crud.py` and `database/*`: Persistence layer using SQLAlchemy and Alembic migrations.
- `tests/`: Pytest-based unit tests and fixtures. `conftest.py` provides mocks for external services.

Database schema is defined in `database/models.py` and migrations in `alembic/versions`.
