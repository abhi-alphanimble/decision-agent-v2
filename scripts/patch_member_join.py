"""
Patch script to add member join event handling to app/main.py
Run this script to automatically integrate the member join feature.
"""

import re

def patch_main_py():
    """Add member join event handling to app/main.py"""
    
    # Read the current file
    with open('app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already patched
    if 'handle_member_joined_channel' in content:
        print("✅ File already patched!")
        return
    
    # 1. Add imports
    print("📝 Adding imports...")
    
    # Add handle_add_command to decision_handlers import
    content = content.replace(
        'from app.handlers.decision_handlers import (\n    handle_propose_command,\n    handle_approve_command,\n    handle_reject_command,\n    handle_show_command,\n    handle_myvote_command,\n    handle_list_command,\n    handle_search_command,\n    handle_help_command\n)',
        'from app.handlers.decision_handlers import (\n    handle_propose_command,\n    handle_approve_command,\n    handle_reject_command,\n    handle_show_command,\n    handle_myvote_command,\n    handle_list_command,\n    handle_search_command,\n    handle_help_command,\n    handle_add_command\n)\nfrom app.handlers.member_handlers import handle_member_joined_channel'
    )
    
    # Add parse_member_event to slack_utils import
    content = content.replace(
        'from app.slack_utils import parse_slash_command, parse_event_message',
        'from app.slack_utils import parse_slash_command, parse_event_message, parse_member_event'
    )
    
    # 2. Add member event handling in process_slack_event
    print("📝 Adding member event handling...")
    
    # Find the end of the slash command handling block
    member_handler_code = '''
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
            
    except Exception as e:'''
    
    content = content.replace(
        '            \r\n    except Exception as e:',
        member_handler_code
    )
    
    # 3. Update event callback handler
    print("📝 Updating event callback handler...")
    
    event_callback_code = '''            # Handle event callback
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
                return {"ok": True}'''
    
    # Find and replace the event callback section
    pattern = r'            # Handle event callback\s+if payload\.get\(\'type\'\) == \'event_callback\':\s+event = payload\.get\(\'event\', \{\}\)\s+logger\.info\(f"Received event: \{event\.get\(\'type\'\)\}"\)\s+# Parse event\s+parsed_event = parse_event_message\(event\)\s+if parsed_event:\s+logger\.info\(f"Parsed event: \{parsed_event\}"\)\s+# Add to background tasks for processing\s+background_tasks\.add_task\(process_slack_event, parsed_event\)\s+# Return 200 OK immediately\s+return \{"ok": True\}'
    
    content = re.sub(pattern, event_callback_code, content, flags=re.MULTILINE)
    
    # Write the patched file
    with open('app/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Patch applied successfully!")
    print("\n📋 Next steps:")
    print("1. Restart the server: python run.py")
    print("2. Configure Slack app to subscribe to 'member_joined_channel' event")
    print("3. Test by having a new user join a channel")

if __name__ == "__main__":
    try:
        patch_main_py()
    except Exception as e:
        print(f"❌ Error applying patch: {e}")
        print("\nPlease manually integrate the changes using MEMBER_JOIN_INTEGRATION.md")
