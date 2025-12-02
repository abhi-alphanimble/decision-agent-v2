import pytest
from app.handlers import decision_handlers as handlers
from app.command_parser import ParsedCommand
from app import crud


def make_parsed(action_text):
    parts = action_text.split(maxsplit=1)
    action = parts[0]
    rest = parts[1] if len(parts) > 1 else ""
    return ParsedCommand(command_type="decision", raw_text=action_text, action=None, args=[rest] if rest else [], flags={})


def test_propose_and_show_and_list_and_search(db_session):
    # propose
    parsed = ParsedCommand(command_type="decision", raw_text='propose "Should we test?"', action=None, args=["Should we test?"], flags={})
    resp = handlers.handle_propose_command(parsed, user_id="Utest", user_name="Tester", channel_id="Ctest", db=db_session)
    assert "posted to the channel" in resp["text"] or "posted" in resp["text"]

    # list
    resp_list = handlers.handle_list_command(ParsedCommand(command_type="decision", raw_text="list", action=None, args=[], flags={}), channel_id="Ctest", db=db_session)
    assert "Decision Summary" in resp_list["text"] or "decisions" in resp_list["text"].lower()

    # search
    resp_search = handlers.handle_search_command(ParsedCommand(command_type="decision", raw_text='search "test"', action=None, args=["test"], flags={}), user_id="Utest", user_name="Tester", channel_id="Ctest", db=db_session)
    assert "Found" in resp_search["text"] or "No decisions found" not in resp_search["text"]


def test_propose_vote_approve_workflow(db_session):
    # propose
    parsed = ParsedCommand(command_type="decision", raw_text='propose "Approve flow test"', action=None, args=["Approve flow test"], flags={})
    handlers.handle_propose_command(parsed, user_id="U1", user_name="User1", channel_id="Cflow", db=db_session)

    decisions = crud.get_decisions_by_channel(db_session, "Cflow")
    assert len(decisions) >= 1
    d = decisions[0]

    # approve
    parsed_approve = ParsedCommand(command_type="decision", raw_text=f"approve {d.id}", action=None, args=[str(d.id)], flags={})
    resp = handlers.handle_approve_command(parsed_approve, user_id="U1", user_name="User1", channel_id="Cflow", db=db_session)
    assert "Vote Recorded" in resp["text"] or "Vote recorded" in resp["text"]


def test_ai_summarize_and_suggest(db_session):
    # create decision
    d = crud.create_decision(db=db_session, channel_id="Cai", text="AI test decision text long enough", created_by="Uai")
    parsed_sum = ParsedCommand(command_type="decision", raw_text=f"summarize {d.id}", action=None, args=[str(d.id)], flags={})
    resp = handlers.handle_summarize_command(parsed_sum, user_id="Uai", user_name="AI", channel_id="Cai", db=db_session)
    assert "AI Summary" in resp["text"] or "Unable to generate summary" not in resp["text"]

    parsed_sug = ParsedCommand(command_type="decision", raw_text=f"suggest {d.id}", action=None, args=[str(d.id)], flags={})
    resp2 = handlers.handle_suggest_command(parsed_sug, user_id="Uai", user_name="AI", channel_id="Cai", db=db_session)
    assert "AI Suggestions" in resp2["text"] or "Unable to generate suggestions" not in resp2["text"]


def test_add_preapproved_decision(db_session):
    """Verify `/decision add` creates an approved decision in the DB."""
    from app.handlers import decision_handlers
    from app import crud

    channel = "C_TEST_ADD"
    user_id = "U_TEST_ADD"
    user_name = "tester"
    # unique text to avoid collisions
    decision_text = "Preapproved add test - unique"

    # Construct a ParsedCommand-like object expected by the handler
    class Parsed:
        command_type = "decision"
        raw_text = f'add "{decision_text}"'
        action = "add"
        args = [decision_text]
        flags = {}

    parsed = Parsed()

    # Call the handler
    resp = decision_handlers.handle_add_command(
        parsed=parsed,
        user_id=user_id,
        user_name=user_name,
        channel_id=channel,
        db=db_session,
    )

    # Handler should return a confirmation text (dict or str)
    assert isinstance(resp, dict) or isinstance(resp, str)

    # Verify the decision exists in DB and is approved
    decisions = crud.get_decisions_by_channel(db_session, channel)
    matches = [d for d in decisions if d.text == decision_text]
    assert len(matches) == 1
    decision = matches[0]
    assert decision.status == "approved"
    assert decision.approval_count >= decision.approval_threshold
