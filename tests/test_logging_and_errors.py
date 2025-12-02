import logging
import json
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _ensure_dev_env(monkeypatch):
    # Ensure logging is in development mode for verbose output during tests
    monkeypatch.setenv('ENV', 'development')
    yield


def make_form_payload():
    return {
        'command': '/decision',
        'text': 'list',
        'user_id': 'Utest',
        'user_name': 'Tester',
        'channel_id': 'Ctest',
    }


def test_slash_command_success_logs(monkeypatch):
    """POST a slash command and assert that request and context are written to the log file."""
    # Import app after ENV set
    from app.main import app

    # Monkeypatch signature check to always allow (we test logging, not signature)
    monkeypatch.setattr('app.main.slack_client.verify_slack_signature', lambda body, ts, sig: True, raising=False)

    # Stub ephemeral send so network isn't called
    monkeypatch.setattr('app.main.slack_client.send_ephemeral_message', lambda channel, user, text: {'ok': True}, raising=False)

    client = TestClient(app)

    payload = make_form_payload()
    response = client.post('/webhook/slack', data=payload)

    assert response.status_code == 200
    data = response.json()
    assert 'Processing your command' in data.get('text', '')

    # Read log file and assert incoming request & context present
    import time
    time.sleep(0.1)
    log_path = 'logs/app.log'
    with open(log_path, 'r', encoding='utf-8') as f:
        contents = f.read()

    assert 'Incoming request' in contents
    assert 'user=Utest' in contents or '"user_id": "Utest"' in contents
    assert 'channel=Ctest' in contents or '"channel_id": "Ctest"' in contents


def test_slash_command_handler_exception_is_logged(monkeypatch):
    """Force a handler-level exception and assert it is written to the log file with stack trace."""
    from app.main import app
    import app.crud as crud

    # Allow signature
    monkeypatch.setattr('app.main.slack_client.verify_slack_signature', lambda body, ts, sig: True, raising=False)

    # Make the summary function raise
    def _boom(db, channel_id):
        raise RuntimeError('boom')

    monkeypatch.setattr(crud, 'get_decision_summary_by_channel', _boom)

    client = TestClient(app)
    payload = make_form_payload()

    response = client.post('/webhook/slack', data=payload)
    assert response.status_code == 200

    # Read log file and assert exception stack trace present
    import time
    time.sleep(0.1)
    log_path = 'logs/app.log'
    with open(log_path, 'r', encoding='utf-8') as f:
        contents = f.read()

    assert 'RuntimeError' in contents or 'boom' in contents
