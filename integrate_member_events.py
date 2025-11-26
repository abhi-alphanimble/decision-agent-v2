"""
Script to integrate member event handling into main.py
"""

# Read the file
with open('app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add imports at the top
old_imports = """from app.slack_utils import parse_slash_command, parse_event_message"""
new_imports = """from app.slack_utils import parse_slash_command, parse_event_message, parse_member_event
from app.handlers.member_handlers import handle_member_joined_channel, handle_member_left_channel"""

content = content.replace(old_imports, new_imports)

# 2. Add member event processing in process_slack_event function
# Find the function and add member event handling
old_event_processing = """    # Handle slash commands
    if event_data.get("command"):"""

new_event_processing = """    # Handle member events (member_joined_channel, member_left_channel)
    if event_data.get("type") in ["member_joined_channel", "member_left_channel"]:
        user_id = event_data.get("user_id", "")
        channel_id = event_data.get("channel_id", "")
        event_type = event_data.get("type")
        
        # Get user info for name
        try:
            user_info = slack_client.get_user_info(user_id)
            user_name = user_info.get("real_name", user_info.get("name", "Unknown"))
        except:
            user_name = "Unknown"
        
        db = next(get_db())
        try:
            if event_type == "member_joined_channel":
                handle_member_joined_channel(user_id, user_name, channel_id, db)
            elif event_type == "member_left_channel":
                handle_member_left_channel(user_id, user_name, channel_id, db)
        finally:
            db.close()
        return
    
    # Handle slash commands
    if event_data.get("command"):"""

content = content.replace(old_event_processing, new_event_processing)

# 3. Add member event parsing in slack_webhook
old_webhook_parsing = """            # Parse event
            parsed_event = parse_event_message(event)
            if parsed_event:
                logger.info(f"Parsed event: {parsed_event}")
                # Add to background tasks for processing
                background_tasks.add_task(process_slack_event, parsed_event)"""

new_webhook_parsing = """            # Parse member events
            if event_type in ['member_joined_channel', 'member_left_channel']:
                parsed_event = parse_member_event(event)
                if parsed_event:
                    logger.info(f"Parsed member event: {parsed_event}")
                    background_tasks.add_task(process_slack_event, parsed_event)
            # Parse message events
            else:
                parsed_event = parse_event_message(event)
                if parsed_event:
                    logger.info(f"Parsed event: {parsed_event}")
                    # Add to background tasks for processing
                    background_tasks.add_task(process_slack_event, parsed_event)"""

content = content.replace(old_webhook_parsing, new_webhook_parsing)

# Write back
with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully integrated member event handling into main.py")
