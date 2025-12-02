import pytest

from app import command_parser


def test_parse_propose_simple():
    text = 'propose "Do we adopt policy X?"'
    parsed = command_parser.parse_message(text)
    assert parsed.action == command_parser.DecisionAction.PROPOSE
    assert parsed.args[0] == "Do we adopt policy X?"


def test_parse_config_set_with_percent():
    text = "config set approval_percentage 70%"
    parsed = command_parser.parse_message(text)
    assert parsed.action == command_parser.DecisionAction.CONFIG
    assert parsed.args == ["approval_percentage", "70"]


def test_parse_config_set_with_equals():
    text = "config set approval_percentage=80%"
    parsed = command_parser.parse_message(text)
    assert parsed.action == command_parser.DecisionAction.CONFIG
    assert parsed.args == ["approval_percentage", "80"]


def test_parse_config_without_set_keyword():
    text = "config approval_percentage 65"
    parsed = command_parser.parse_message(text)
    assert parsed.action == command_parser.DecisionAction.CONFIG
    assert parsed.args == ["approval_percentage", "65"]


def test_parse_config_inline_equals():
    text = "config group_size=25"
    parsed = command_parser.parse_message(text)
    assert parsed.action == command_parser.DecisionAction.CONFIG
    assert parsed.args == ["group_size", "25"]


def test_parse_invalid_command():
    parsed = command_parser.parse_message("")
    assert parsed.is_valid is False
    assert parsed.error_message is not None
"""
Unit tests for command parser
Run with: pytest tests/test_command_parser.py -v
"""
import pytest
from app.command_parser import (
    parse_message,
    extract_quoted_text,
    extract_id_from_command,
    parse_flags,
    CommandType,
    DecisionAction
)


def test_propose_double_quotes():
    result = parse_message('propose "Should we order pizza?"')
    assert result.is_valid is True
    assert result.action == DecisionAction.PROPOSE
    assert result.args == ["Should we order pizza?"]


def test_propose_single_quotes():
    result = parse_message("propose 'Should we have a meeting?'")
    assert result.is_valid is True
    assert result.action == DecisionAction.PROPOSE
    assert result.args == ["Should we have a meeting?"]


def test_propose_without_quotes():
    result = parse_message("propose Should we order pizza")
    assert result.is_valid is False
    assert "quoted text" in result.error_message.lower()


def test_approve_with_id():
    result = parse_message("approve 42")
    assert result.is_valid is True
    assert result.action == DecisionAction.APPROVE
    assert result.args == [42]


def test_approved_alias():
    result = parse_message("approved 42")
    assert result.is_valid is True
    assert result.action == DecisionAction.APPROVE
    assert result.args == [42]


def test_approve_anonymous():
    result = parse_message("approve 42 --anonymous")
    assert result.is_valid is True
    assert result.action == DecisionAction.APPROVE
    assert result.args == [42]
    assert result.flags == {"anonymous": True}


def test_reject_with_id():
    result = parse_message("reject 42")
    assert result.is_valid is True
    assert result.action == DecisionAction.REJECT
    assert result.args == [42]


def test_rejected_alias():
    result = parse_message("rejected 42")
    assert result.is_valid is True
    assert result.action == DecisionAction.REJECT
    assert result.args == [42]


def test_reject_anonymous():
    result = parse_message("reject 42 --anonymous")
    assert result.is_valid is True
    assert result.action == DecisionAction.REJECT
    assert result.args == [42]
    assert result.flags == {"anonymous": True}


def test_list_no_args():
    result = parse_message("list")
    assert result.is_valid is True
    assert result.action == DecisionAction.LIST
    assert result.args == []


def test_list_pending():
    result = parse_message("list pending")
    assert result.is_valid is True
    assert result.action == DecisionAction.LIST
    assert result.args == ["pending"]


def test_search_with_quotes():
    result = parse_message('search "pizza"')
    assert result.is_valid is True
    assert result.action == DecisionAction.SEARCH
    assert result.args == ["pizza"]


def test_search_without_quotes():
    result = parse_message("search pizza")
    assert result.is_valid is True
    assert result.action == DecisionAction.SEARCH
    assert result.args == ["pizza"]


def test_show():
    result = parse_message("show 42")
    assert result.is_valid is True
    assert result.action == DecisionAction.SHOW
    assert result.args == [42]


def test_myvote():
    result = parse_message("myvote 42")
    assert result.is_valid is True
    assert result.action == DecisionAction.MYVOTE
    assert result.args == [42]


def test_summarize():
    result = parse_message("summarize")
    assert result.is_valid is True
    assert result.action == DecisionAction.SUMMARIZE
    assert result.args == []


def test_suggest():
    result = parse_message("suggest")
    assert result.is_valid is True
    assert result.action == DecisionAction.SUGGEST
    assert result.args == []


def test_help():
    result = parse_message("help")
    assert result.is_valid is True
    assert result.command_type == CommandType.HELP


def test_unknown_action():
    result = parse_message("invalid")
    assert result.is_valid is False
    assert result.command_type == CommandType.UNKNOWN


def test_empty_command():
    result = parse_message("")
    assert result.is_valid is False


def test_extract_quoted_text():
    assert extract_quoted_text('"Hello World"') == "Hello World"
    assert extract_quoted_text("'Hello World'") == "Hello World"
    assert extract_quoted_text("No quotes") is None


def test_extract_id():
    assert extract_id_from_command("approve 42") == 42
    assert extract_id_from_command("show 123 --anonymous") == 123
    assert extract_id_from_command("no id here") is None


def test_parse_flags():
    assert parse_flags("approve 42 --anonymous") == {"anonymous": True}
    assert parse_flags("approve 42") == {}