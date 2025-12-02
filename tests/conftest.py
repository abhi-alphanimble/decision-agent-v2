import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.base import Base

# Try to load .env automatically so TEST_DATABASE_URL in project .env is used during tests
try:
    from dotenv import load_dotenv
    # load dotenv from repo root
    load_dotenv()
except Exception:
    # dotenv not available or .env not present; continue — tests will require TEST_DATABASE_URL env var
    pass


@pytest.fixture(scope='session')
def test_database_url():
    """Return TEST_DATABASE_URL from env; require Postgres URL for accurate tests."""
    url = os.getenv('TEST_DATABASE_URL')
    # Allow falling back to in-memory sqlite for local quick runs when TEST_DATABASE_URL is not provided.
    if not url:
        # Use sqlite in-memory for local developer convenience
        return "sqlite:///:memory:"
    return url


@pytest.fixture(scope='session')
def engine(test_database_url):
    engine = create_engine(test_database_url)
    # Create all tables for tests
    Base.metadata.create_all(bind=engine)
    yield engine
    # Teardown: drop all tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope='function')
def db_session(engine):
    """Creates a new database session for a test and rolls back after test."""
    TestingSessionLocal = sessionmaker(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(autouse=True)
def disable_external_apis(monkeypatch):
    """Monkeypatch Slack and AI clients to avoid external network calls during tests by default."""
    # Minimal fake slack client
    class DummySlack:
        def send_message(self, channel, text, blocks=None):
            return {"ok": True}

        def get_channel_members_count(self, channel_id):
            # Align with handler MVP default used by tests
            return 10

        def get_user_info(self, user_id):
            return {"real_name": "Test User", "name": "testuser"}

    # Minimal fake AI client
    class DummyAI:
        def summarize_decision(self, decision, votes):
            return "Summary"

        def suggest_next_steps(self, decision, votes):
            return "Suggestions"

    # Apply monkeypatches
    monkeypatch.setattr('app.slack_client.slack_client', DummySlack(), raising=False)
    # Also patch any modules that imported the client at import-time
    monkeypatch.setattr('app.handlers.decision_handlers.slack_client', DummySlack(), raising=False)
    # app.ai may not expose ai_client at package attribute level; allow setattr without raising
    monkeypatch.setattr('app.ai.ai_client', DummyAI(), raising=False)
