# Instructions for integrating search command into main.py

## Step 1: Add handle_search_command to imports (around line 27-35)

Change this:
```python
from .handlers.decision_handlers import (
    handle_propose_command,
    handle_approve_command,
    handle_reject_command,
    handle_show_command,
    handle_myvote_command,
    handle_list_command,
    handle_help_command
)
```

To this:
```python
from .handlers.decision_handlers import (
    handle_propose_command,
    handle_approve_command,
    handle_reject_command,
    handle_show_command,
    handle_myvote_command,
    handle_list_command,
    handle_search_command,
    handle_help_command
)
```

## Step 2: Add search handler call (around line 376-389)

After the LIST handler block (around line 383), add the SEARCH handler block:

```python
            elif parsed.action == DecisionAction.LIST:
                response = handle_list_command(
                    parsed=parsed,
                    user_id=user_id,
                    user_name=user_name,
                    channel_id=channel_id,
                    db=db
                )
            
            elif parsed.action == DecisionAction.SEARCH:
                response = handle_search_command(
                    parsed=parsed,
                    user_id=user_id,
                    user_name=user_name,
                    channel_id=channel_id,
                    db=db
                )
            
            else:
                response = {
                    "text": f"⏳ Command `{parsed.action}` coming soon!",
                    "response_type": "ephemeral"
                }
```

That's it! The search command should now be fully integrated.
