"""
Script to register summarize command in main.py
"""

# Read the file
with open('app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
old_imports = """    handle_search_command,
    handle_help_command
)"""
new_imports = """    handle_search_command,
    handle_help_command,
    handle_summarize_command
)"""

content = content.replace(old_imports, new_imports)

# 2. Add handler dispatch
# Find the end of the dispatch chain
dispatch_marker = """        elif command.action == DecisionAction.SEARCH:
            result = handle_search_command(command, user_id, user_name, channel_id, db)"""

new_dispatch = """        elif command.action == DecisionAction.SEARCH:
            result = handle_search_command(command, user_id, user_name, channel_id, db)
            
        elif command.action == DecisionAction.SUMMARIZE:
            result = handle_summarize_command(command, user_id, user_name, channel_id, db)"""

content = content.replace(dispatch_marker, new_dispatch)

# Write back
with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully registered summarize command in main.py")
