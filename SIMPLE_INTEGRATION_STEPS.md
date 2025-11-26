# SIMPLE INTEGRATION INSTRUCTIONS

## Problem
The welcome message feature isn't working because app/main.py is missing the integration code.

## Solution
Add these 3 code blocks to app/main.py:

### 1. Line 11 - Add this import AFTER line 10:
```python
    handle_add_command
)
from app.handlers.member_handlers import handle_member_joined_channel
```

### 2. Line 30 - Change this line:
FROM:
```python
from app.slack_utils import parse_slash_command, parse_event_message
```

TO:
```python
from app.slack_utils import parse_slash_command, parse_event_message, parse_member_event
```

### 3. Line 283 - Add this code AFTER line 282 (after `db.close()` and BEFORE the `except Exception` line):

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

### 4. Around line 340 - Find the event callback section and UPDATE it:

FIND THIS:
```python
            # Handle event callback
            if payload.get('type') == 'event_callback':
                event = payload.get('event', {})
                logger.info(f"Received event: {event.get('type')}")
                
                # Parse event
                parsed_event = parse_event_message(event)
                if parsed_event:
                    logger.info(f"Parsed event: {parsed_event}")
                    # Add to background tasks for processing
                    background_tasks.add_task(process_slack_event, parsed_event)
                
                # Return 200 OK immediately
                return {"ok": True}
```

REPLACE WITH:
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

## After Making Changes

1. Save the file
2. Restart the server (Ctrl+C and run `python run.py` again)
3. Configure Slack app to subscribe to `member_joined_channel` event
4. Test by having a new user join a channel

## Slack App Configuration

Go to https://api.slack.com/apps → Your App → Event Subscriptions → Subscribe to bot events:
- Add: `member_joined_channel`
- Save Changes
- Reinstall app if prompted
