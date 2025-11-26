# Member Leave Feature - Manual Integration Guide

## Files Already Created ✅
- `app/handlers/member_handlers.py` - Contains `handle_member_left_channel` function
- `app/crud.py` - Updated with `expired_unreachable` status

## Manual Changes Required

### 1. Add Function to app/crud.py

**Location:** After the `update_decision_status` function (around line 202)

**Add this function:**

```python
def close_decision_as_unreachable(
    db: Session,
    decision_id: int
) -> Optional[Decision]:
    """
    Close a decision as unreachable (when threshold > current members).
    Sets status to 'expired_unreachable' and closed_at timestamp.
    Preserves all vote history.
    """
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if decision is None:
        logger.warning(f"Decision #{decision_id} not found for unreachable close")
        return None
    
    if decision.status != "pending":
        logger.warning(f"Decision #{decision_id} is not pending, cannot close as unreachable")
        return None
    
    decision.status = "expired_unreachable"
    decision.closed_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(decision)
        logger.info(f"🔒 Closed decision #{decision_id} as unreachable")
        return decision
    except Exception as exc:
        logger.error(f"Database error in close_decision_as_unreachable: {exc}")
        db.rollback()
        return None
```

### 2. Add Method to app/slack_client.py

**Location:** In the `SlackClient` class, after the `send_ephemeral_message` method

**Add this method:**

```python
def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
    """
    Get channel information including member count.
    
    Args:
        channel_id: Slack channel ID
        
    Returns:
        Channel info dictionary
    """
    try:
        response = self.client.conversations_info(channel=channel_id)
        if response.get("ok"):
            return response.get("channel", {})
        else:
            logger.error(f"Error getting channel info: {response.get('error')}")
            return {}
    except Exception as e:
        logger.error(f"Exception getting channel info: {e}")
        return {}
```

### 3. Update app/main.py

**Location:** In the `process_slack_event` function, in the member events section (around line 292)

**Find this code:**
```python
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

**Add this code AFTER the member_joined_channel block:**

```python
            elif event_type == "member_left_channel":
                # Get database session
                db = next(get_db())
                
                try:
                    # Get user info from Slack
                    try:
                        user_info = slack_client.get_user_info(user_id)
                        user_name = user_info.get('real_name', user_info.get('name', 'Unknown'))
                    except Exception as e:
                        logger.warning(f"Could not get user info for {user_id}: {e}")
                        user_name = "Member"
                    
                    # Handle member left
                    handle_member_left_channel(
                        user_id=user_id,
                        user_name=user_name,
                        channel_id=channel_id,
                        db=db
                    )
                finally:
                    db.close()
```

**Also add import at the top of main.py (around line 12):**

Change:
```python
from app.handlers.member_handlers import handle_member_joined_channel
```

To:
```python
from app.handlers.member_handlers import handle_member_joined_channel, handle_member_left_channel
```

### 4. Subscribe to member_left_channel Event in Slack

1. Go to https://api.slack.com/apps → Your App → Event Subscriptions
2. Under "Subscribe to bot events", click "Add Bot User Event"
3. Add: `member_left_channel`
4. Click "Save Changes"
5. Reinstall the app if prompted

## Testing

After making these changes:

1. Restart the server: `python run.py`
2. Create a pending decision in a test channel
3. Have a member leave the channel
4. Check server logs for:
   ```
   👋 Member [name] left channel [channel_id]
   📊 Current channel member count: X
   🚫 Decision #X is unreachable
   🔒 Auto-closed decision #X as unreachable
   📢 Sent notification about X auto-closed decisions
   ```
5. Check the channel for the auto-close notification message

## What This Feature Does

When a member leaves a channel:
1. ✅ Detects the leave event
2. ✅ Gets current channel member count
3. ✅ Finds pending decisions where `approval_threshold > current_members`
4. ✅ Auto-closes those decisions with status `expired_unreachable`
5. ✅ Sets `closed_at` timestamp
6. ✅ Preserves all vote history
7. ✅ Sends notification to channel about auto-closed decisions
8. ✅ Logs all actions
