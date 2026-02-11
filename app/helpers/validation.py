"""
Input validation and normalization for appeal flow.
"""


def normalize_phone(raw: str) -> str:
    """Ensure phone has leading + for storage."""
    s = (raw or "").strip()
    if not s:
        return ""
    return s if s.startswith("+") else f"+{s}"
