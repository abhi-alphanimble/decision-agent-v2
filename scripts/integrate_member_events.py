"""
Robust integrator: inserts member-event handling into `app/main.py`.

This script is idempotent and uses regex to safely insert the
member-event block before the first `if event_data.get("command"):`
check and to replace the simple `parse_event_message` usage inside
the `event_callback` parsing with an `event_type` branch that calls
`parse_member_event` for member join/leave events.

Run this script if you want to programmatically update `app/main.py`.
It will not duplicate blocks on multiple runs.
"""

import re
from pathlib import Path


MAIN_PATH = Path(__file__).resolve().parents[1] / 'app' / 'main.py'


MEMBER_BLOCK = (
    '    # Handle member events (member_joined_channel, member_left_channel)\n'
    '    if event_data.get("type") in ["member_joined_channel", "member_left_channel"]:\n'
    '        # Slack may use \'user\'/\'channel\' or \'user_id\'/\'channel_id\' depending on source\n'
    '        user_id = event_data.get("user") or event_data.get("user_id", "")\n'
    '        channel_id = event_data.get("channel") or event_data.get("channel_id", "")\n'
    '        event_type = event_data.get("type")\n\n'
    '        try:\n'
    '            user_info = slack_client.get_user_info(user_id)\n'
    '            user_name = user_info.get("real_name", user_info.get("name", "Unknown"))\n'
    '        except Exception:\n'
    '            user_name = "Unknown"\n\n'
    '        db = next(get_db())\n'
    '        try:\n'
    '            if event_type == "member_joined_channel":\n'
    '                handle_member_joined_channel(user_id, user_name, channel_id, db)\n'
    '            elif event_type == "member_left_channel":\n'
    '                handle_member_left_channel(user_id, user_name, channel_id, db)\n'
    '        finally:\n'
    '            db.close()\n\n'
    '        # Member event handled — stop further processing\n'
    '        return\n\n'
)


WEBHOOK_REPLACEMENT = (
    "event = payload.get('event', {})\n"
    "                event_type = event.get('type')\n"
    "                logger.info(f\"Received event: {event_type}\")\n\n"
    "                # Member events (join/leave) -> use dedicated parser\n"
    "                if event_type in ['member_joined_channel', 'member_left_channel']:\n"
    "                    parsed_event = parse_member_event(event)\n"
    "                    if parsed_event:\n"
    "                        logger.info(f\"Parsed member event: {parsed_event}\")\n"
    "                        background_tasks.add_task(process_slack_event, parsed_event)\n"
    "                else:\n"
    "                    # Fallback to standard message/event parser\n"
    "                    parsed_event = parse_event_message(event)\n"
    "                    if parsed_event:\n"
    "                        logger.info(f\"Parsed event: {parsed_event}\")\n"
    "                        background_tasks.add_task(process_slack_event, parsed_event)\n"
)


def main():
    content = MAIN_PATH.read_text(encoding='utf-8')

    # Ensure member imports exist near other slack_utils imports
    if 'parse_member_event' not in content:
        content = content.replace(
            'from app.slack_utils import parse_slash_command, parse_event_message',
            'from app.slack_utils import parse_slash_command, parse_event_message, parse_member_event'
        )

    if 'handle_member_joined_channel' not in content:
        content = content.replace(
            'from app.handlers.member_handlers import handle_member_joined_channel, handle_member_left_channel',
            'from app.handlers.member_handlers import handle_member_joined_channel, handle_member_left_channel'
        )

    # Insert MEMBER_BLOCK before the first occurrence of `if event_data.get("command"):`
    pattern = re.compile(r"(\n\s*)if event_data\.get\(\"command\"\):", re.MULTILINE)
    if pattern.search(content):
        # Only insert if MEMBER_BLOCK isn't already present
        if 'Handle member events (member_joined_channel' not in content:
            content = pattern.sub(lambda m: '\n' + MEMBER_BLOCK + m.group(0), content, count=1)

    # Replace the simple parse_event_message block inside the event_callback parsing
    # We look for the known small snippet and replace it with WEBHOOK_REPLACEMENT
    old_snippet = (
        "# Parse event\n"
        "                parsed_event = parse_event_message(event)\n"
        "                if parsed_event:\n"
        "                    logger.info(f\"Parsed event: {parsed_event}\")\n"
        "                    # Add to background tasks for processing\n"
        "                    background_tasks.add_task(process_slack_event, parsed_event)"
    )

    if old_snippet in content:
        content = content.replace(old_snippet, WEBHOOK_REPLACEMENT)
    else:
        # try a looser regex replace in case whitespace differs
        loose_pattern = re.compile(r"parsed_event\s*=\s*parse_event_message\(event\)[\s\S]*?background_tasks\.add_task\(process_slack_event, parsed_event\)", re.MULTILINE)
        if loose_pattern.search(content):
            content = loose_pattern.sub(WEBHOOK_REPLACEMENT.strip(), content)

    # Write back
    MAIN_PATH.write_text(content, encoding='utf-8')
    print("✅ Successfully integrated member event handling into app/main.py (idempotent)")


if __name__ == '__main__':
    main()
