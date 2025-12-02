"""
Script to append handle_summarize_command to decision_handlers.py
"""

with open('app/handlers/decision_handlers.py', 'a', encoding='utf-8') as f:
    f.write("""

def handle_summarize_command(
    parsed: ParsedCommand,
    user_id: str,
    user_name: str,
    channel_id: str,
    db: Session
) -> Dict[str, Any]:
    \"\"\"
    Handle summarize command to generate AI summary for a decision.
    Command: /decision summarize <decision_id>
    \"\"\"
    logger.info(f"🤖 Handling SUMMARIZE from {user_name} in {channel_id}")
    
    # 1. Extract decision_id
    if not parsed.args or len(parsed.args) == 0:
        logger.warning("❌ No decision ID provided for summary")
        return {
            "text": "❌ Please provide a decision ID to summarize.\n\n*Example:* `/decision summarize 42`",
            "response_type": "ephemeral"
        }
    
    try:
        decision_id = int(parsed.args[0])
    except (ValueError, TypeError):
        logger.warning(f"❌ Invalid decision ID: {parsed.args[0]}")
        return {
            "text": f"❌ Invalid decision ID: `{parsed.args[0]}`\n\nDecision ID must be a number.",
            "response_type": "ephemeral"
        }
    
    # 2. Get decision from database
    decision = crud.get_decision_by_id(db, decision_id)
    
    if not decision:
        logger.warning(f"❌ Decision #{decision_id} not found")
        return {
            "text": f"❌ Decision #{decision_id} not found.",
            "response_type": "ephemeral"
        }
    
    # 3. Get votes for context
    votes = crud.get_votes_by_decision(db, decision_id)
    
    # 4. Generate summary
    # Send ephemeral "thinking" message first? Slack slash commands expect immediate response.
    # We can return a message saying "Generating summary..." but we can't update it easily without response_url.
    # For now, we'll try to generate it synchronously. If it takes too long (>3s), Slack might timeout.
    # Ideally, this should be a background task, but for MVP we'll try sync.
    
    try:
        summary = ai_client.summarize_decision(decision, votes)
        
        if not summary:
            return {
                "text": "❌ Unable to generate summary. Please check if the AI service is configured correctly.",
                "response_type": "ephemeral"
            }
            
        return {
            "text": f"🤖 *AI Summary for Decision #{decision_id}*\n\n{summary}",
            "response_type": "ephemeral"  # Or in_channel if we want everyone to see
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating summary: {e}")
        return {
            "text": "❌ An error occurred while generating the summary. Please try again later.",
            "response_type": "ephemeral"
        }
""")

print("✅ Successfully appended handle_summarize_command")
