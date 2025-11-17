def display_vote_list(votes: list):
    """
    Format vote list respecting anonymity.
    Returns list of formatted strings.
    """
    approvals = []
    rejections = []
    
    for vote in votes:
        if vote.is_anonymous:
            voter_display = "🔒 Anonymous"
        else:
            voter_display = f"<@{vote.user_id}>"
        
        if vote.vote_type == 'approve':
            approvals.append(f"👍 {voter_display}")
        else:
            rejections.append(f"👎 {voter_display}")
    
    return approvals, rejections


def format_vote_summary(votes: list):
    """
    Create a formatted summary of all votes.
    """
    approvals, rejections = display_vote_list(votes)
    
    sections = []
    
    if approvals:
        sections.append("*Approvals:*\n" + "\n".join(approvals))
    
    if rejections:
        sections.append("*Rejections:*\n" + "\n".join(rejections))
    
    if not approvals and not rejections:
        sections.append("_No votes yet_")
    
    return "\n\n".join(sections)