def normalize_email(email: str) -> str:
    """Return the canonical form used for account email identity."""
    return email.strip().lower()
