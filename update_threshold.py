"""
Script to add dynamic threshold calculation to handle_propose_command
"""
import re

# Read the file
with open('app/handlers/decision_handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the hardcoded values section
old_code = """    # Create decision in database
    try:
        decision = crud.create_decision(
            db=db,
            channel_id=channel_id,
            text=proposal_text,
            created_by=user_id,
            created_by_name=user_name,
            group_size_at_creation=MVP_GROUP_SIZE,
            approval_threshold=MVP_APPROVAL_THRESHOLD
        )"""

new_code = """    # Get current channel member count from Slack
    try:
        group_size = slack_client.get_channel_members_count(channel_id)
        logger.info(f"📊 Channel {channel_id} has {group_size} members")
    except Exception as e:
        logger.warning(f"⚠️ Could not get channel member count: {e}. Using default.")
        group_size = MVP_GROUP_SIZE  # Fallback to default
    
    # Calculate approval threshold as 60% of group size (rounded up)
    import math
    approval_threshold = math.ceil(group_size * 0.6)
    
    logger.info(f"📊 Group size: {group_size}, Approval threshold (60%): {approval_threshold}")
    
    # Create decision in database
    try:
        decision = crud.create_decision(
            db=db,
            channel_id=channel_id,
            text=proposal_text,
            created_by=user_id,
            created_by_name=user_name,
            group_size_at_creation=group_size,  # Store current group size
            approval_threshold=approval_threshold  # Store calculated threshold
        )"""

# Replace
content = content.replace(old_code, new_code)

# Write back
with open('app/handlers/decision_handlers.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully updated handle_propose_command with dynamic threshold calculation")
