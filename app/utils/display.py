"""
Display utilities for formatting voting information.
"""


def display_vote_list(votes: list) -> str:
    """
    Format a list of votes into readable display text.
    
    Args:
        votes: List of Vote objects
    
    Returns:
        Formatted vote list as string
    """
    if not votes:
        return "No votes yet."
    
    lines = []
    for vote in votes:
        vote_name = vote.voter_name
        
        vote_emoji = "✅" if vote.vote_type == "approve" else "❌"
        line = f"{vote_emoji} {vote_name}: {vote.vote_type.capitalize()}"
        lines.append(line)
    
    return "\n".join(lines)


def format_vote_summary(
    decision,
    include_full_list: bool = False
) -> str:
    """
    Format a summary of votes for a decision.
    
    Args:
        decision: Decision object with votes
        include_full_list: Whether to include full vote list
    
    Returns:
        Formatted summary as string
    """
    approval_pct = 0
    if decision.approval_count + decision.rejection_count > 0:
        approval_pct = round(
            100 * decision.approval_count / (decision.approval_count + decision.rejection_count)
        )
    
    summary = f"**Vote Summary:**\n"
    summary += f"✅ Approvals: {decision.approval_count}\n"
    summary += f"❌ Rejections: {decision.rejection_count}\n"
    summary += f"📊 Approval Rate: {approval_pct}%\n"
    summary += f"Status: {decision.status.upper()}\n"
    
    if include_full_list and decision.votes:
        summary += "\n" + display_vote_list(decision.votes)
    
    return summary
