"""
Helper utilities for parsing and extracting data.
"""


def parse_anonymous_flag(text: str) -> tuple:
    """
    Parse anonymous flag from text (e.g., "--anonymous" or "-a").
    
    Args:
        text: Input text to parse
    
    Returns:
        Tuple of (cleaned_text, is_anonymous)
    """
    is_anonymous = False
    cleaned_text = text
    
    # Check for anonymous flag
    if "--anonymous" in text.lower():
        is_anonymous = True
        cleaned_text = text.lower().replace("--anonymous", "").strip()
    elif " -a" in text.lower():
        is_anonymous = True
        cleaned_text = text.lower().replace(" -a", "").strip()
    
    return cleaned_text, is_anonymous


def extract_decision_id(text: str) -> int:
    """
    Extract decision ID from text (e.g., "vote 123" -> 123).
    
    Args:
        text: Input text containing decision ID
    
    Returns:
        Decision ID as integer, or 0 if not found
    """
    parts = text.strip().split()
    for part in parts:
        if part.isdigit():
            return int(part)
    return 0
