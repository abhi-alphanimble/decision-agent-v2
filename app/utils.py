# app/utils.py

def truncate_text(text: str, max_length: int = 50, ellipsis: str = "...") -> str:
    """
    Truncates a string to max_length and appends ellipsis if truncated.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + ellipsis