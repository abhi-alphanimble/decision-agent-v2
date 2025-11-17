import re

def parse_anonymous_flag(text: str):
    """
    Parse anonymous flag from command text.
    Returns: (cleaned_text, is_anonymous)
    
    Supports: --anonymous, --anon, -a
    """
    # Check for flags (case insensitive)
    patterns = [
        r'\s+--anonymous\b',
        r'\s+--anon\b',
        r'\s+-a\b'
    ]
    
    is_anonymous = False
    cleaned_text = text
    
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            is_anonymous = True
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
            break
    
    return cleaned_text.strip(), is_anonymous


def extract_decision_id(text: str):
    """
    Extract decision ID from command text.
    Example: "approve 42 --anonymous" -> 42
    """
    match = re.search(r'\b(\d+)\b', text)
    return int(match.group(1)) if match else None