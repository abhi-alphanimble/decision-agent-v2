# Member Join Event Integration Guide

## Files Created
✅ `app/handlers/member_handlers.py` - Member event handler module
✅ `app/slack_utils.py` - Added `parse_member_event` function

## Manual Changes Required in app/main.py

### 1. Update Imports (Lines 2-12)

Replace the decision_handlers import block with:

```python
from app.handlers.decision_handlers import (
    handle_propose_command,
    handle_approve_command,
    handle_reject_command,
    handle_show_command,
    handle_myvote_command,
    handle_list_command,
    handle_search_command,
    handle_help_command,
    handle_add_command
)
from app.handlers.member_handlers import handle_member_joined_channel
```

### 2. Update slack_utils import (Line 28)

Replace:
```python
from app.slack_utils import parse_slash_command, parse_event_message
```

With:
```python
from app.slack_utils import parse_slash_command, parse_event_message, parse_member_event
```

### 3. Add Member Event Handling in process_slack_event function

Find the `process_slack_event` function (around line 150) and add this code AFTER the slash command handling block and BEFORE the exception handler:

```python
        # Handle member events (member_joined_channel, member_left_channel)
        elif event_data.get("type") in ["member_joined_channel", "member_left_channel"]:
            event_type = event_data.get("type")
            user_id = event_data.get("user_id", "")
            channel_id = event_data.get("channel_id", "")
            
            logger.info(f"📥 Received {event_type} event for user {user_id} in channel {channel_id}")
            
            if event_type == "member_joined_channel":
                # Get database session
                db = next(get_db())
                
                try:
                    # Get user info from Slack
                    try:
                        user_info = slack_client.get_user_info(user_id)
                        user_name = user_info.get('real_name', user_info.get('name', 'Unknown'))
                    except Exception as e:
                        logger.warning(f"Could not get user info for {user_id}: {e}")
                        user_name = "New Member"
                    
                    # Handle member joined
                    handle_member_joined_channel(
                        user_id=user_id,
                        user_name=user_name,
                        channel_id=channel_id,
                        db=db
                    )
                finally:
                    db.close()
```

### 4. Update Event Callback Handler in slack_webhook function

Find the event callback section (around line 340) and update it to parse member events:

```python
            # Handle event callback
            if payload.get('type') == 'event_callback':
                event = payload.get('event', {})
                event_type = event.get('type', '')
                logger.info(f"Received event: {event_type}")
                
                # Parse message events
                if event_type in ['message', 'app_mention']:
                    parsed_event = parse_event_message(event)
                    if parsed_event:
                        logger.info(f"Parsed event: {parsed_event}")
                        background_tasks.add_task(process_slack_event, parsed_event)
                
                # Parse member events
                elif event_type in ['member_joined_channel', 'member_left_channel']:
                    parsed_event = parse_member_event(event)
                    if parsed_event:
                        logger.info(f"Parsed member event: {parsed_event}")
                        background_tasks.add_task(process_slack_event, parsed_event)
                
                # Return 200 OK immediately
                return {"ok": True}
```

## Slack App Configuration Required

### Subscribe to Events in Slack App Settings

1. Go to https://api.slack.com/apps
2. Select your app
3. Navigate to "Event Subscriptions"
4. Under "Subscribe to bot events", add:
   - `member_joined_channel` - A user joined a public or private channel
5. Save Changes
6. Reinstall the app to your workspace if prompted

### Required Bot Scopes

Ensure your bot has these scopes (in OAuth & Permissions):
- `channels:read` - View basic information about public channels
- `groups:read` - View basic information about private channels
- `users:read` - View people in a workspace
- `chat:write` - Send messages as the bot

## Testing Checklist

After making the changes:

1. ✅ Restart the server: `python run.py`
2. ✅ Check logs for "Starting up Slack Decision Agent API..."
3. ✅ Verify no import errors
4. ✅ Test member join flow (see TESTING_STEPS.md)
